import os
import sys

RAW_DATA_DIR = "raw_data"
DISTILLED_DATA_DIR = "distilled_data"
GRAPHS_DIR = "graphs"

ROWS = (100*1000*1000)
CARDINALITY = 1000
WORKERS = 16
ALGORITHMS = ["rabit", "cubit-lk", "ub"]

UDI_RATIO_RE = ["0.0", "0.02", "0.05", "0.1", "0.2", "0.3", "0.4", "0.5"]
UDI_RATIO_NORMAL = ["0.0", "0.1", "0.2", "0.3", "0.4", "0.5"]

RQ_RANGE_FIX = 0.15

RQ_RANGE = [0.05, 0.15, 0.25, 0.35, 0.45]
UDI_RATIO_FIX = 0.2

GE_GROUP_SIZE = [50, 100, 200]

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
    f = open(filename)
    ret = 0.0
    for line in f:
        a = line.split()
        if len(a) != 3 or a[0] != 'Throughput':
            continue
        ret += float(a[1])
    f.close()
    return ret


def analyse_throughput_varying_UDI_rabit(directory_path):
    for ge_group_size in GE_GROUP_SIZE:
        experiment_name = f"eva_rabit_throughput_{int(ROWS/1000000)}M_c_{CARDINALITY}_w_{WORKERS}"
        output_file_name = os.path.join(directory_path, DISTILLED_DATA_DIR, experiment_name + f"_GL_{ge_group_size}_vary_UDI.distilled")
        
        if os.path.exists(output_file_name):
            print(f"Output file '{output_file_name}' already exists. Skip the analysis.")
            continue

        output_file = open(output_file_name, 'w')
        output_file.write('# UDI ratio (% of operations) \t Throughput (op/s) \n')

        for udi in UDI_RATIO_NORMAL:
            src_file = os.path.join(directory_path, RAW_DATA_DIR, experiment_name + f"_ratio_{udi}" + f"_range_{int(RQ_RANGE_FIX*CARDINALITY)}_GL_{ge_group_size}.rawdata")
            ret = throughput_analysis(src_file)
        
            output_file.write('{} \t\t {} \n'.format(int(float(udi)*100), f"{ret:.2f}"))
            print("\tAnalyzing rawdata file : " + src_file)
            print("\tThroughput results : " + str(f"{ret:.2f}") + "\n")

        print("Output file is created at " + output_file.name + "\n")
        output_file.close()


def analyse_throughput_varying_UDI_common(directory_path, alg):
    experiment_name = "eva_{}_throughput_{}M_c_{}_w_{}".format(alg, int(ROWS/1000000), CARDINALITY, WORKERS)
    output_file_name = os.path.join(directory_path, DISTILLED_DATA_DIR, experiment_name + f"_vary_UDI.distilled")
    
    if os.path.exists(output_file_name):
        print(f"Output file '{output_file_name}' already exists. Skip the analysis.")
        return

    output_file = open(output_file_name, 'w')
    output_file.write('# UDI ratio (% of operations) \t Throughput (op/s) \n')

    UDI_RATIO = UDI_RATIO_RE if alg == "ub" else UDI_RATIO_NORMAL
    for udi in UDI_RATIO:
        src_file = os.path.join(directory_path, RAW_DATA_DIR, experiment_name + f"_ratio_{udi}" + f"_range_{int(RQ_RANGE_FIX*CARDINALITY)}_GL_0.rawdata")

        ret = throughput_analysis(src_file)
    
        output_file.write('{} \t\t {} \n'.format(int(float(udi)*100),f"{ret:.2f}"))
        print("\tAnalyzing rawdata file : " + src_file)
        print("\tThroughput results : " + str(f"{ret:.2f}") + "\n")

    print("Output file is created at " + output_file.name + "\n")
    output_file.close()


def analyse_throughput_varying_UDI(directory_path):
    print ('-' * 10)
    print ('Analyse the throughput of range queries with varying UDI ratio.')

    for alg in ALGORITHMS:
        if alg == "rabit":
            analyse_throughput_varying_UDI_rabit(directory_path)
        else:
            analyse_throughput_varying_UDI_common(directory_path, alg)


def analyse_throughput_varying_range_rabit(directory_path):
    for ge_group_size in GE_GROUP_SIZE:
        experiment_name = "eva_rabit_throughput_{}M_c_{}_w_{}_ratio_{}".format(int(ROWS/1000000), CARDINALITY, WORKERS, UDI_RATIO_FIX)
        output_file_name = os.path.join(directory_path, DISTILLED_DATA_DIR, experiment_name + f"_GL_{ge_group_size}_vary_QL.distilled")

        if os.path.exists(output_file_name):
            print(f"Output file '{output_file_name}' already exists. Skip the analysis.")
            continue

        output_file = open(output_file_name, 'w')
        output_file.write('# Range (% of cardinality) \t Throughput (op/s) \n')

        for rq_range in RQ_RANGE:
            src_file = os.path.join(directory_path, RAW_DATA_DIR, experiment_name + f"_range_{int(rq_range*CARDINALITY)}" + f"_GL_{ge_group_size}.rawdata")

            ret = throughput_analysis(src_file)
        
            output_file.write('{} \t\t {} \n'.format(int(rq_range*100), f"{ret:.2f}"))
            print("\tAnalyzing rawdata file : " + src_file)
            print("\tThroughput results : " + str(f"{ret:.2f}") + "\n")

        print("Output file is created at " + output_file.name + "\n")
        output_file.close()


def analyse_throughput_varying_range_common(directory_path, alg):
    experiment_name = "eva_{}_throughput_{}M_c_{}_w_{}_ratio_{}".format(alg, int(ROWS/1000000), CARDINALITY, WORKERS, UDI_RATIO_FIX)
    output_file_name = os.path.join(directory_path, DISTILLED_DATA_DIR, experiment_name + f"_vary_QL.distilled")

    if os.path.exists(output_file_name):
        print(f"Output file '{output_file_name}' already exists. Skip the analysis.")
        return

    output_file = open(output_file_name, 'w')
    output_file.write('# Range (% of cardinality) \t Throughput (op/s) \n')

    for rq_range in RQ_RANGE:
        src_file = os.path.join(directory_path, RAW_DATA_DIR, experiment_name + f"_range_{int(rq_range*CARDINALITY)}" + "_GL_0.rawdata")

        ret = throughput_analysis(src_file)
    
        output_file.write('{} \t\t {} \n'.format(int(rq_range*100), f"{ret:.2f}"))
        print("\tAnalyzing rawdata file : " + src_file)
        print("\tThroughput results : " + str(f"{ret:.2f}") + "\n")

    print("Output file is created at " + output_file.name + "\n")
    output_file.close()


def analyse_throughput_varying_range(directory_path):
    print ('-' * 10)
    print ('Analyse the throughput of range queries with varying range.')

    for alg in ALGORITHMS:
        if alg == "rabit":
            analyse_throughput_varying_range_rabit(directory_path)
        else:
            analyse_throughput_varying_range_common(directory_path, alg)


def draw_throughput_varying_range(directory_path):    
    # invoke gnuplot script
    gnu_command = "gnuplot -e 'directory_path=\"" + directory_path + "\"' eva_scripts/gnuplot_scripts/throughput_vs_query_range.gnuplot" 
    print("Generating graph Throughput vs. Query Range using command \n\t" + gnu_command)
    os.system(gnu_command)
    print("\tGraphs are generated in the directory : " + os.path.join(directory_path, GRAPHS_DIR) + "\n")

def draw_throughput_varying_UDI(directory_path):    
    # invoke gnuplot script
    gnu_command = "gnuplot -e 'directory_path=\"" + directory_path + "\"' eva_scripts/gnuplot_scripts/throughput_vs_UDI.gnuplot" 
    print("Generating graph Throughput vs. UDI ratio using command \n\t" + gnu_command)
    os.system(gnu_command)
    print("\tGraphs are generated in the directory : " + os.path.join(directory_path, GRAPHS_DIR) + "\n")

def draw_latency_varying_range(directory_path):
    # invoke gnuplot script
    gnu_command = "gnuplot -e 'directory_path=\"" + directory_path + "\"' eva_scripts/gnuplot_scripts/latency_vs_query_range.gnuplot" 
    print("Generating graphs using command \n\t" + gnu_command)
    os.system(gnu_command)
    print("\tGraphs are generated in the directory : " + os.path.join(directory_path, GRAPHS_DIR) + "\n")

def latency_analysis(filename):
    f = open(filename)
    Qvec = [] # vec for operations
    Uvec = []
    Ivec = []
    Dvec = []
    RQvec = []
    ret = []

    for line in f:
        a = line.split()
        if (len(a) != 2):
            continue
        elif line.startswith('Q '):
            Qvec.append(int(a[-1]) / 1000000)
        elif line.startswith('RQ '):
            RQvec.append(int(a[-1]) / 1000000)
        elif line.startswith('U '):
            Uvec.append(int(a[-1]) / 1000000)
        elif line.startswith('D '):
            Dvec.append(int(a[-1]) / 1000000)
        elif line.startswith('I '):
            Ivec.append(int(a[-1]) / 1000000)
        else:
            continue

    if len(Qvec) != 0:
        ret.append(round(sum(Qvec) / len(Qvec), 2)) 
    else:
        ret.append(0)
    if len(RQvec) != 0:
        ret.append(round(sum(RQvec) / len(RQvec), 2))
    else:
        ret.append(0)
    if len(Uvec) != 0:
        ret.append(round(sum(Uvec) / len(Uvec), 2))
    else:
        ret.append(0)
    if len(Dvec) != 0:
        ret.append(round(sum(Dvec) / len(Dvec), 2)) 
    else:
        ret.append(0)
    if len(Ivec) != 0:
        ret.append(round(sum(Ivec) / len(Ivec), 2)) 
    else:
        ret.append(0)

    return ret

def analyse_latency_varying_range(directory_path):
    print ('-' * 10)
    print ('Analyse the latency of range queries with varying range.')

    for alg in ALGORITHMS:
        experiment_name = "eva_{}_latency_{}M_c_{}_w_{}_ratio_{}".format(alg, int(ROWS/1000000), CARDINALITY, WORKERS, UDI_RATIO_FIX)
        output_file_name = os.path.join(directory_path, DISTILLED_DATA_DIR, experiment_name + f".distilled")

        if os.path.exists(output_file_name):
            print(f"Output file '{output_file_name}' already exists. Skip the analysis.")
            continue

        output_file = open(output_file_name, 'w')
        output_file.write('# Range (% of cardinality) \t Query Latency (ms) \t RQ (ms) \t Update (ms) \t Delete (ms) \t Insert (ms)\n')

        for rq_range in RQ_RANGE:
            src_file = os.path.join(directory_path, RAW_DATA_DIR, experiment_name + f"_range_{int(rq_range*CARDINALITY)}")
            if alg == "rabit":
                src_file += "GL_100.rawdata"
            else:
                src_file += "GL_0.rawdata"

            ret = latency_analysis(src_file)

            # print out latency values in ret to a single line
            output_file.write('{} \t\t {} \n'.format(int(rq_range*100), "           ".join(map(str, ret))))
            print("\tAnalyzing rawdata file : " + src_file)
            print("\tLatency results : " + " ".join(map(str, ret)) + "\n")

        print("Output file is created at " + output_file.name + "\n")
        output_file.close()

def convert_eps_to_pdf(directory_path):
    # if epstopdf is not installed, return
    if os.system("which epstopdf") != 0:
        print("epstopdf is not installed. Skip converting eps files to pdf files.")
        return    

    eps_files = os.listdir(os.path.join(directory_path, GRAPHS_DIR))
    print (f"Convert eps files in {eps_files} to pdf files.")
    for eps_file in eps_files:
        if eps_file.endswith(".eps"):
            pdf_file = eps_file.replace(".eps", ".pdf")
            eps_file_path = os.path.join(directory_path, GRAPHS_DIR, eps_file)
            pdf_file_path = os.path.join(directory_path, GRAPHS_DIR, pdf_file)
            os.system(f"epstopdf {eps_file_path} --outfile={pdf_file_path}")
            print(f"Converted {eps_file_path} to {pdf_file_path}")

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

    analyse_throughput_varying_UDI(directory_path)

    analyse_throughput_varying_range(directory_path)

    #     analyse_latency_varying_range(directory_path)


    ### Draw figures ###    
    create_directory(os.path.join(directory_path, GRAPHS_DIR))

    draw_throughput_varying_UDI(directory_path)

    draw_throughput_varying_range(directory_path)

    #     draw_latency_varying_range(directory_path)

    convert_eps_to_pdf(directory_path)

    print("All analyses are done.")