#include <stdlib.h>
#include <memory>

#include "gtest/gtest.h"

#include "fastbit/bitvector_base.h"
#include "fastbit/bitvector8.h"
#include "fastbit/bitvector16.h"
#include "fastbit/bitvector.h"

#include "nicolas/util.h"
#include "bitmaps/base_table.h"

#include "bitmaps/ub/table.h"
#include "bitmaps/ucb/table.h"
#include "bitmaps/naive/table.h"
#include "bitmaps/rabit/table.h"

#define M (1000000)

std::atomic<int> atomicstopnum(0);
std::atomic<int> atomicremovenum(0);

void init_config(Table_config *tconfig, uint64_t rows_num, size_t cardinality, Index_encoding encoding, size_t word_size, size_t n_queries = 970) {
	if(encoding == Index_encoding::RE)
		cardinality--;
	std::string work_dir = "./BM_uniform_";
	std::string data_name = "a_" + std::to_string(rows_num) + "_" + std::to_string(cardinality);
	std::string index_name = std::to_string(rows_num/M) + "M_" + std::to_string(cardinality) + "_AE_10_" + std::to_string(word_size);
	std::string group_name = std::to_string(rows_num/M) + "M_" + std::to_string(cardinality) + "_GE_" + std::to_string(word_size);
	tconfig->n_workers = 1;
	tconfig->DATA_PATH = work_dir + data_name;
	tconfig->INDEX_PATH = work_dir + index_name;
	tconfig->GROUP_PATH = work_dir + group_name;
	tconfig->GE_group_len = 10;
	tconfig->n_rows = rows_num; 
	tconfig->g_cardinality = cardinality;
	enable_fence_pointer = tconfig->enable_fence_pointer = false;
	INDEX_WORDS = 10000;  // Fence length 
	tconfig->approach = {"rabit"};
	tconfig->nThreads_for_getval = 4;
	tconfig->show_memory = true;
	tconfig->on_disk = false;
	tconfig->showEB = false;
	tconfig->decode = false;
	tconfig->n_queries = n_queries;
	tconfig->n_udis = 30;
	tconfig->verbose = false;
	tconfig->WAH_config = word_size;
	tconfig->btv_WAH_length_map = {};
	tconfig->encoding = encoding;
	tconfig->segmented_btv = true;
	tconfig->rows_per_seg = 10000;
	tconfig->encoded_word_len = 31;
	tconfig->enable_parallel_cnt = true;
	tconfig->nThreads_for_getval = 2;
	tconfig->autoCommit = true;
	tconfig->nThreads_for_merge = 1;

	for(int i = 0; i < cardinality; i++)
		tconfig->btv_WAH_length_map.insert(std::make_pair(i, word_size));
}

void Update(rabit::Rabit *rabit, int tid) {
	rcu_register_thread();
	for(uint64_t row_id = 0; row_id < M; row_id += 10000) {
		rabit->update(tid, row_id, rand() % rabit->config->g_cardinality);
		// rabit->Merge_worker();
	}
	atomicstopnum.fetch_add(1);
	// while(rabit->Merge_worker() != -1);
	rcu_unregister_thread();
}

void Remove(rabit::Rabit *rabit, int tid) {
	rcu_register_thread();
	for(uint64_t row_id = 0; row_id < M; row_id += 10000) {
		if(rabit->remove(tid ,row_id) == 0)
			atomicremovenum.fetch_add(1);
		// rabit->Merge_worker();
	}
	atomicstopnum.fetch_add(1);
	// while(rabit->Merge_worker() != -1);
	rcu_unregister_thread();
}

bool Check_AE(rabit::Rabit *rabit, int deleted = 0) 
{
	uint64_t sum = 0;
	rcu_register_thread();
	for(int i = rabit->config->GE_group_len - 1; i < rabit->config->g_cardinality; i += rabit->config->GE_group_len) {
		sum += rabit->evaluate(0, i);
	}
	rcu_unregister_thread();
	return sum == rabit->config->n_rows - deleted;
}

TEST(DISABLED_MERGETEST, MULTIINTEGRITY) {
int n = 500;
while(n--)
{
	auto row_nums = M;
	auto cardinality = 200;
	auto word_size = 32;
	auto thread_nums = 10;

	atomicstopnum.store(0);
	atomicremovenum.store(0);

	Table_config *tconfig = new Table_config{};
	init_config(tconfig, row_nums, cardinality, Index_encoding::AE, word_size);
	rabit::Rabit *rabit = new rabit::Rabit(tconfig);

	auto merge_thread = std::thread(rabit_merge_dispatcher, rabit);

	std::vector<std::thread> thread_pool(thread_nums);
	for (int i = 0; i < thread_pool.size(); i++) {
		struct RABIT_ThreadInfo *info = &g_ths_info[i];
		info->tid = i;
		info->active_trans = NULL;
	}
	for(int i = 0; i < thread_pool.size(); i++) {
		if(rand() % 2)
			thread_pool[i] = std::thread(&Update, rabit, i);
		else thread_pool[i] = std::thread(&Remove, rabit, i);
	}

	for(int i = 0; i < thread_pool.size(); i++) {
		thread_pool[i].join();
	}
	__atomic_store_n(&run_merge_func, false, MM_CST);
	merge_thread.join();


	EXPECT_EQ(Check_AE(rabit, atomicremovenum.load()), 1);
	GTEST_LOG_(INFO) << "num of rows: " << rabit->config->n_rows - atomicremovenum.load();
	delete rabit;
	GTEST_LOG_(INFO) << n;
}

}

TEST(RANGETEST, SEQUENTIAL_AE) {

	auto row_nums = M;
	auto n_queries = row_nums / 100;
	auto cardinality = 200;
	auto word_size = 32;
	auto thread_nums = 10;
	__atomic_store_n(&run_merge_func, true, MM_CST);
	
	atomicstopnum.store(0);
	atomicremovenum.store(0);

	Table_config *tconfig = new Table_config{};
	init_config(tconfig, row_nums, cardinality, Index_encoding::AE, word_size, 2 * row_nums / 100);
	rabit::Rabit *rabit = new rabit::Rabit(tconfig);

	auto merge_thread = std::thread(rabit_merge_dispatcher, rabit);

	RUB last_rub = RUB{0, TYPE_INV, {}};
	std::vector<int> rows(row_nums / 100);
	rcu_register_thread();
	for(int row = 0; row < row_nums / 100; row++) {
		auto tmp = (rand() + 1) % cardinality;
		rabit->update(0, row, tmp);
		rows[row] = tmp;
	}
	rcu_unregister_thread();
	__atomic_store_n(&run_merge_func, false, MM_CST);
	merge_thread.join();
	__atomic_store_n(&run_merge_func, true, MM_CST);
	for(int row = 0; row < row_nums / 100; row++) {
		EXPECT_EQ(rows[row], rabit->get_value_rcu(row, rabit->g_timestamp, last_rub));
	}

	rcu_register_thread();

	merge_thread = std::thread(rabit_merge_dispatcher, rabit);
	for(int row = 0; row < row_nums / 100; row++) {
		auto tmp = (rand() + 1) % cardinality;
		rabit->update(0, row, tmp);
		rows[row] = tmp;
		if(row == row_nums / 200) {
			__atomic_store_n(&run_merge_func, false, MM_CST);
			merge_thread.join();
			__atomic_store_n(&run_merge_func, true, MM_CST);
		}
	}
	EXPECT_EQ(rabit->range(0, 0, cardinality), rabit->config->n_rows);

	rcu_unregister_thread();
}
