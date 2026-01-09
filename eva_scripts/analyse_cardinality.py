import os
import sys

RAW_DATA_DIR = "raw_data"
DISTILLED_DATA_DIR = "distilled_data"
GRAPHS_DIR = "graphs"

ROWS = (10*1000*1000)

WORKERS = 16
ALGORITHMS = ["rabit", "cubit-lk", "ub"]
UDI_RATIO = "0.2"

RQ_RANGE_FIX = 0.15

CARDINALITY = [256, 512, 1024, 2048]

GE_GROUP_NUM = [128, 64]

global distilled_data_directory
global graphs_directory


def check_rawdata_directory_exist(path):
    if os.path.isdir(path):
        data_path = os.path.join(path, RAW_DATA_DIR)
        if os.path.isdir(data_path):
            print(f"Processing the raw data in  '{path}'.")
            return True

    print(f"The directory '{path}' is not valid.")
    sys.exit(1)


def create_directory(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        print(f"Output directory '{directory_path}' has been created.")
    else:
        print(f"WARNING: Output directory '{directory_path}' already exists. \nSkip building the directory and overwrite the existing files.")


def throughput_analysis(filename):
    if not os.path.exists(filename):
        print(f"WARNING: Raw data file '{filename}' does not exist. Skip the analysis.")
        return 0.0
    f = open(filename)
    ret = 0.0
    for line in f:
        a = line.split()
        if len(a) != 3 or a[0] != 'Throughput':
            continue
        ret += float(a[1])
    f.close()
    return ret


def analyse_throughput_varying_cardinality_rabit(directory_path):
    for ge_group_num in GE_GROUP_NUM:
        experiment_name = f"eva_rabit_throughput_{int(ROWS/1000000)}M"
        output_file_name = os.path.join(directory_path, DISTILLED_DATA_DIR, experiment_name +
                                        f"_w_{WORKERS}_ratio_{UDI_RATIO}_rangefix_{RQ_RANGE_FIX}_GN_{ge_group_num}_vary_cardinality.distilled")
        
        if os.path.exists(output_file_name):
            print(f"Output file '{output_file_name}' already exists. Skip the analysis.")
            return

        output_file = open(output_file_name, 'w')
        output_file.write('# cardinality \t Throughput (op/s) \n')

        for cardinality in CARDINALITY:
            g_len = int(cardinality / ge_group_num)
            src_file = os.path.join(directory_path, RAW_DATA_DIR, experiment_name +
                                    f"_c_{cardinality}_w_{WORKERS}_ratio_{UDI_RATIO}_range_{int(RQ_RANGE_FIX*cardinality)}_GL_{g_len}.rawdata")
            ret = throughput_analysis(src_file)
        
            output_file.write('{} \t\t {} \n'.format(cardinality, f"{ret:.2f}"))
            print("\tAnalyzing rawdata file : " + src_file)
            print("\tThroughput results : " + str(f"{ret:.2f}") + "\n")

        print("Output file is created at " + output_file.name + "\n")
        output_file.close()
def analyse_throughput_varying_cardinality_common(directory_path, alg):
    experiment_name = f"eva_{alg}_throughput_{int(ROWS/1000000)}M"
    output_file_name = os.path.join(directory_path, DISTILLED_DATA_DIR, experiment_name +
                                    f"_w_{WORKERS}_ratio_{UDI_RATIO}_rangefix_{RQ_RANGE_FIX}_vary_cardinality.distilled")
    
    if os.path.exists(output_file_name):
        print(f"Output file '{output_file_name}' already exists. Skip the analysis.")
        return

    output_file = open(output_file_name, 'w')
    output_file.write('# cardinality \t Throughput (op/s) \n')

    for cardinality in CARDINALITY:
        src_file = os.path.join(directory_path, RAW_DATA_DIR, experiment_name +
                                f"_c_{cardinality}_w_{WORKERS}_ratio_{UDI_RATIO}_range_{int(RQ_RANGE_FIX*cardinality)}_GL_0.rawdata")

        ret = throughput_analysis(src_file)
    
        output_file.write('{} \t\t {} \n'.format(cardinality, f"{ret:.2f}"))
        print("\tAnalyzing rawdata file : " + src_file)
        print("\tThroughput results : " + str(f"{ret:.2f}") + "\n")

    print("Output file is created at " + output_file.name + "\n")
    output_file.close()
def analyse_throughput_varying_cardinality(directory_path):
    print ('-' * 10)
    print ('Analyse the throughput of range queries with varying cardinality.')

    for alg in ALGORITHMS:
        if alg == "rabit":
            analyse_throughput_varying_cardinality_rabit(directory_path)
        else:
            analyse_throughput_varying_cardinality_common(directory_path, alg)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python analyse_range.py <directory_path> (clean|analyse)")
        sys.exit(1)
    directory_path = sys.argv[1]
    command = sys.argv[2]

    if command == "clean":
        os.system("rm -rf " + os.path.join(directory_path, DISTILLED_DATA_DIR))
        os.system("rm -rf " + os.path.join(directory_path, GRAPHS_DIR))
        sys.exit(0)

    check_rawdata_directory_exist(directory_path)

    ### Analyse the raw data ###
    create_directory(os.path.join(directory_path, DISTILLED_DATA_DIR))

    analyse_throughput_varying_cardinality(directory_path)


    print("All analyses are done.")