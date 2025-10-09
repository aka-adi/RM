#include <iostream>
#include <sys/mman.h>
#include <mutex>
#include <vector>
#include <random>
#include <chrono>
#include <unistd.h>
#include <stdio.h>
#include <signal.h>
#include <thread>
#include <fstream>
#include <urcu.h>
#include <iomanip>

// bitvector compliment
#include "fastbit/bitvector_base.h"
#include "fastbit/bitvector.h"
// #include "fastbit/bitvector8.h"
// #include "fastbit/bitvector16.h"

// build index
#include "nicolas/gen_bitmap.h"

// different algorithms
#include "util.h"
#include "bitmaps/base_table.h"
#include "bitmaps/ub/table.h"
#include "bitmaps/ucb/table.h"
#include "bitmaps/naive/table.h"
#include "bitmaps/rabit/table.h"

#ifdef LINUX
#include "GTest/perf.h"
#endif

using namespace std;

static BaseTable *table;

bool existdone(std::string path) {
    bool ret = false;
    ifstream doneFlag;
    doneFlag.open(path + "/" + "done");
    if (doneFlag.good()) { 
        cout << "NOTE: Index " + path + " exits. Skip building." << endl;
        doneFlag.close();
        ret = true;
    }
    return ret;
}

void createdone(std::string path) {
    //create file "done" 
    std::fstream done;
    done.open(path + "/" + "done", ios::out);
    if (done.is_open()) {
        done << "Succeeded in building bitmap files";
        done << "\nIndex Path: " << path << "\n";
        auto now = std::chrono::system_clock::now();
        auto in_time_t = std::chrono::system_clock::to_time_t(now);
        done << "Date: " << std::put_time(std::localtime(&in_time_t), "%Y-%m-%d %X") << "\n";
        cout << "NOTE: Succeeded in building bitmap " << path << endl;
        done.close(); 
    }
    else {
        cout << "ERROR: Failed in building bitmap " << path << endl;
        exit(-1);
    }
}


void build_index(Table_config *config) 
{
    if(config->encoding == GE) {
        if(existdone(config->GROUP_PATH)) return;
    }
    else {
        if(existdone(config->INDEX_PATH)) return;
    }

    if(config->encoding == EE) {
        genEE(config->DATA_PATH, config->INDEX_PATH, config->n_rows);
    }
    else if(config->encoding == RE) {
        genRE(config->DATA_PATH, config->INDEX_PATH, config->g_cardinality - 1, config->n_rows);
    }
    else if(config->encoding == GE) {
        if(existdone(config->INDEX_PATH)) {
            genGEbyEE(config->INDEX_PATH, config->GROUP_PATH, config->GE_group_len, config->g_cardinality, config->n_rows);
        }
        else {
            genGE(config->DATA_PATH, config->GROUP_PATH,config->GE_group_len, config->g_cardinality, config->n_rows);
        }
    }
    else {
        cerr << "ERROR: Invalid encoding scheme. Supported schemes are EE, RE, and GE." << endl;
        exit(-1);
    }

    if(config->encoding == GE) {
        createdone(config->GROUP_PATH);
    }
    else {
        createdone(config->INDEX_PATH);
    }

}

void verify_op_rcu(int rid, int expected_val, Table_config *config)
{
    if (config->approach == "rabit") {
        RUB rub_t{0, TYPE_INV, {}};
        rabit::Rabit* table2 = dynamic_cast<rabit::Rabit*>(table);
        assert(table2->get_value_rcu(rid, table2->get_g_timestamp(), rub_t) == expected_val);
    }
    return;
}

// Mutex to ensure worker threads print results sequentially without interleaving.
static mutex g_dump_results_lock;

void worker_func(int tid, const string& mode, Table_config *config)
{
    auto seed = chrono::system_clock::now().time_since_epoch().count();
    default_random_engine generator(seed);
    
    int btv_range;
    if (config->encoding == EE || config->encoding == GE) {
        btv_range = config->g_cardinality - 1;
    }
    else if (config->encoding == RE) {
        btv_range = config->g_cardinality - 2;
    }
    else {
        cerr << "ERROR: Invalid encoding scheme. Supported schemes are EE, RE, and GE." << endl;
        exit(-1);
    }
    uniform_int_distribution<int> val_distribution(0, btv_range);

#if defined(VERIFY_RESULTS)
    int rid_min = (config->n_rows/config->n_workers)*tid;
    int rid_max = (config->n_rows/config->n_workers)*(tid+1) - 1;
    uniform_int_distribution<uint32_t> rid_distribution(rid_min, rid_max);
    cout << "Thread " << tid << ". Rid range: [" << rid_min << ", " << rid_max << "]" << endl;
#else
    uniform_int_distribution<uint32_t> rid_distribution(0, config->n_rows - 1);
#endif

    unsigned long timeout_begin, timeout_end;
    unsigned long t_before, t_after; // HZ numbers
    vector<unsigned long> times_Q; // Query
    vector<unsigned long> times_RQ; // Query
    vector<unsigned long> times_I; // Insert
    vector<unsigned long> times_D; // Delete
    vector<unsigned long> times_U; // Update
    long l_n_query=0, l_n_insert=0, l_n_delete=0, l_n_update=0; // Numbers of different ops.

    double ratio = (double) config->n_udis / (double) (config->n_udis + config->n_queries);
    uniform_real_distribution<double> ratio_distribution(0.0, 1.0);
    string _mode = mode;

    rcu_register_thread();

    int perf_pid;
    // Only thread 1 is responsible for generating perf process.
    if (perf_enabled == true && config->segmented_btv && tid == 1) {
        string size = to_string(config->n_rows / config->rows_per_seg);
        cout << "Generating perf process for segmented btv " << size << endl;
        perf_pid = gen_perf_process((char *)size.c_str());
    }

    timeout_begin = read_timestamp();
    for (int i = 0; i < config->n_queries + config->n_udis; ++i) {
        int val = val_distribution(generator);
        if (ratio_distribution(generator) < ratio) {
            uint32_t rid = rid_distribution(generator);
            if (mode == "mix" || mode == "range") {
                int test = rid_distribution(generator);
                switch (test % 3) {
                    case 0:
                        _mode = "update";
                        break;
                    case 1:
                        _mode = "delete";
                        break;
                    case 2:
                        _mode = "insert";
                        break;
                }
            }
            if (_mode == "update") {
                t_before = read_timestamp();
                int ret = table->update(tid, rid, val);
                #if defined(VERIFY_RESULTS)
                rcu_read_lock();
                if (!ret) {
                    verify_op_rcu(rid, val, config);
                }
                rcu_read_unlock();
                #endif
                l_n_update ++;
                t_after = read_timestamp();
                if (config->verbose)
                    times_U.push_back(rdtsc_diff(t_before, t_after));
            }
            else if (_mode == "delete") {
                t_before = read_timestamp();
                int ret = table->remove(tid, rid);
                #if defined(VERIFY_RESULTS)
                rcu_read_lock();
                if (!ret) {
                    verify_op_rcu(rid, -1, config);
                }
                rcu_read_unlock();
                #endif
                l_n_delete ++;
                t_after = read_timestamp();
                if (config->verbose)
                    times_D.push_back(rdtsc_diff(t_before, t_after));
            }
            else if (_mode == "insert") {
                t_before = read_timestamp();
                table->append(tid, val);
                l_n_insert ++;
                t_after = read_timestamp();
                if (config->verbose)
                    times_I.push_back(rdtsc_diff(t_before, t_after));
            }
        } else {
            t_before = read_timestamp();
            if(mode == "range") {
                table->range(tid, 0, config->n_range);
                t_after = read_timestamp();
                if (config->verbose)
                    times_RQ.push_back(rdtsc_diff(t_before, t_after));
            }
            else {
                table->evaluate(tid, val);
                t_after = read_timestamp();
                if (config->verbose)
                    times_Q.push_back(rdtsc_diff(t_before, t_after));
            }
            l_n_query ++;

        }

        // if (config->verbose && config->show_memory && i % 1000 == 0) {
        //     table->printMemory();
        //     table->printUncompMemory();
        // }

        if (config->time_out > 0 && i % 100 == 0) {
            timeout_end = read_timestamp();
            if (rdtsc_diff(timeout_begin, timeout_end) > config->time_out * 1000000000) {
                break;
            }
        }
    }
    timeout_end = read_timestamp();

    if (perf_enabled == true && config->segmented_btv && tid == 1) {
        kill_perf_process(perf_pid);
        usleep(WAIT_FOR_PERF_U);
    }

    rcu_quiescent_state();
    rcu_unregister_thread();

    {
        // To dump experimental results sequentially.
        lock_guard<mutex> guard(g_dump_results_lock);

        auto l_n_total = l_n_query + l_n_insert + l_n_delete + l_n_update;
        cout << endl << "Thread " << dec << tid 
            << " Queries " << l_n_query
            << " Inserts " << l_n_insert
            << " Deletes " << l_n_delete
            << " Updates " << l_n_update
            << " Total " << l_n_total 
            << endl;

        if (config->verbose) {
            cout << "Details are shown below." << endl;
            for (long t : times_Q)
                cout << "Q " << t << endl;
            for (long t : times_RQ)
                cout << "RQ " << t << endl;
            for (long t : times_I)
                cout << "I " << t << endl;                
            for (long t : times_D)
                cout << "D " << t << endl;
            for (long t : times_U)
                cout << "U " << t << endl;
            cout << "Thread " << tid << " has dumped all results." << endl << endl;
        }
        else {
            cout << "Throughput " << l_n_total / (rdtsc_diff(timeout_begin, timeout_end) / 1000000000.0) << "   op/s" << endl;
        }
    }
}

void evaluate(Table_config *config, string mode) 
{
    auto t1 = std::chrono::high_resolution_clock::now();

    if (config->approach == "naive") {
        table = new naive::Table(config);
    } else if (config->approach == "ucb") {
        table = new ucb::Table(config);
    } else if (config->approach == "ub") {
        table = new ub::Table(config);
    } else if (config->approach == "cubit") {
        // table = new cubit_lk::CubitLK(config);
        cerr << "WARNING: CUBIT is currently not supported in this framework." << endl;
        return;
    } else if (config->approach == "rabit") {
        table = new rabit::Rabit(config);
    } else {
        cerr << "Unknown approach." << endl;
        return;
    }

    auto t2 = std::chrono::high_resolution_clock::now();
    long long time1 = std::chrono::duration_cast<std::chrono::microseconds>(t2-t1).count();
    cout << "=== Bitmap" << config->approach << " init time (ms): " << time1/1000 << endl;

    if (config->show_memory) {
        table->printMemory();
        table->printUncompMemory();
    }

    // Start merge dispatcher thread.
    std::thread merge_thread;

    if (config->approach == "rabit") {
        merge_thread = std::thread(rabit_merge_dispatcher, table);
    }

    std::thread *ths = new thread[config->n_workers];
    for (int i = 0; i < config->n_workers; i++) {
        struct RABIT_ThreadInfo *info = &g_ths_info[i];
        info->tid = i;
        info->active_trans = NULL;
        
        ths[i] = std::thread(worker_func, i, mode, config);
    }

    for (int i = 0; i < config->n_workers; i++) {
        ths[i].join();
    }

    if (config->approach == "rabit")
    {
        __atomic_store_n(&run_merge_func, false, MM_CST);
        merge_thread.join();
    }
    
    if (config->show_memory) {
        table->printMemory();
        table->printUncompMemory();
    }

    delete[] ths;
    return;
}

int index_is_valid(Table_config *config)
{
    ifstream doneFlag;
    doneFlag.open(config->INDEX_PATH + "/" + "done");
    if (!doneFlag.good()) {
        cout << "WARNING: The index for " + config->INDEX_PATH + " hasn't been set correctly. Please check." << endl;
        return 0;
    }
    doneFlag.close();
    return 1;
}

std::map<std::string, Index_encoding> encodingMap = {
    {"EE", EE},
    {"RE", RE},
    {"IE", IE},
    {"GE", GE}
};

int main(const int argc, const char *argv[]) 
{
    po::variables_map options = get_options(argc, argv);
    Table_config *config = new Table_config{};
    init_config(config, options);
    int n_btvs;

    #if defined(VERIFY_RESULTS)
    cout << "**************************************************" << endl <<
            "WARNING: Debug option VERIFY_RESULTS is set." << endl <<
            "         The result should no be used for " << endl <<
            "         performance evaluation." << endl <<
            "**************************************************" << endl;
    #endif

    if (options.count("encoding-scheme")) {
        string encoding = options["encoding-scheme"].as<string>();

        auto it = encodingMap.find(encoding);
        if (it != encodingMap.end()) {
            config->encoding = it->second;
        } else {
            cout << "Invalid encoding scheme: " << encoding << endl;
            assert(0);
        }
        cout << "=== Encoding scheme: " << it->first << " : " << it->second << endl;
    }
    
    if (options.count("mode")) {
        string mode = options["mode"].as<string>();

        if (mode == "build") {
            build_index(config);
            return 0;
        }
        
        /*if(mode == "test"){     /// call the test function
            test_logic_opera(config);
            return 0;
        }*/

        if (!index_is_valid(config))
            return 0;

        if (mode == "query" || mode == "mix" || mode == "range"){
            evaluate(config, mode);
        }
        // else if (mode == "getvalue") {
        //     evaluateGetValue(config);
        // } else if (mode == "impact") {
        //     evaluateImpact(config, 0);
        // }         
        else {
            std::cout << "not implemented" << std::endl;
            assert(0);
        }
    }

    return 0;
}

