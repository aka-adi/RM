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

def latency_analysis(filename):
    if not os.path.exists(filename):
        print(f"WARNING: Raw data file '{filename}' does not exist. Skip the analysis.")
        return [0, 0]

    RQvec = []
    UDIvec = []

    with open(filename) as f:
        for line in f:
            a = line.split()
            if len(a) != 2:
                continue

            if line.startswith('Q ') or line.startswith('RQ '):
                RQvec.append(int(a[-1]) / 1000000)
            elif line.startswith('U '):
                UDIvec.append(int(a[-1]) / 1000000)

    ret = []

    if len(RQvec) != 0:
        ret.append(round(sum(RQvec) / len(RQvec), 2))
    else:
        ret.append(0)

    if len(UDIvec) != 0:
        ret.append(round(sum(UDIvec) / len(UDIvec), 2))
    else:
        ret.append(0)

    return ret

def analyse_latency_varying_cardinality_rabit(directory_path):
    for ge_group_num in GE_GROUP_NUM:
        experiment_name = f"eva_rabit_latency_{int(ROWS/1000000)}M"
        output_file_name = os.path.join(
            directory_path,
            DISTILLED_DATA_DIR,
            experiment_name + f"_w_{WORKERS}_ratio_{UDI_RATIO}_rangefix_{RQ_RANGE_FIX}_GN_{ge_group_num}_vary_cardinality.distilled"
        )

        if os.path.exists(output_file_name):
            print(f"Output file '{output_file_name}' already exists. Skip the analysis.")
            continue

        output_file = open(output_file_name, 'w')
        output_file.write('# cardinality \t RQ \t UDI (ms) \n')

        for cardinality in CARDINALITY:
            g_len = int(cardinality / ge_group_num)
            src_file = os.path.join(
                directory_path,
                RAW_DATA_DIR,
                experiment_name + f"_c_{cardinality}_w_{WORKERS}_ratio_{UDI_RATIO}_range_{int(RQ_RANGE_FIX*cardinality)}_GL_{g_len}.rawdata"
            )

            ret = latency_analysis(src_file)

            output_file.write('{} \t\t {} \t\t {} \n'.format(cardinality, ret[0], ret[1]))
            print("\tAnalyzing rawdata file : " + src_file)
            print("\tLatency results : RQ = " + str(ret[0]) + " ms, UDI = " + str(ret[1]) + " ms\n")

        print("Output file is created at " + output_file.name + "\n")
        output_file.close()

def analyse_latency_varying_cardinality_common(directory_path, alg):
    experiment_name = f"eva_{alg}_latency_{int(ROWS/1000000)}M"
    output_file_name = os.path.join(
        directory_path,
        DISTILLED_DATA_DIR,
        experiment_name + f"_w_{WORKERS}_ratio_{UDI_RATIO}_rangefix_{RQ_RANGE_FIX}_vary_cardinality.distilled"
    )

    if os.path.exists(output_file_name):
        print(f"Output file '{output_file_name}' already exists. Skip the analysis.")
        return

    output_file = open(output_file_name, 'w')
    output_file.write('# cardinality \t RQ \t UDI (ms) \n')

    for cardinality in CARDINALITY:
        src_file = os.path.join(
            directory_path,
            RAW_DATA_DIR,
            experiment_name + f"_c_{cardinality}_w_{WORKERS}_ratio_{UDI_RATIO}_range_{int(RQ_RANGE_FIX*cardinality)}_GL_0.rawdata"
        )

        ret = latency_analysis(src_file)

        output_file.write('{} \t\t {} \t\t {} \n'.format(cardinality, ret[0], ret[1]))
        print("\tAnalyzing rawdata file : " + src_file)
        print("\tLatency results : RQ = " + str(ret[0]) + " ms, UDI = " + str(ret[1]) + " ms\n")

    print("Output file is created at " + output_file.name + "\n")
    output_file.close()

def analyse_latency_varying_cardinality(directory_path):
    print('-' * 10)
    print('Analyse the latency of range queries with varying cardinality.')

    for alg in ALGORITHMS:
        if alg == "rabit":
            analyse_latency_varying_cardinality_rabit(directory_path)
        else:
            analyse_latency_varying_cardinality_common(directory_path, alg)

def draw_latency_varying_cardinality(directory_path):
    gnu_command = "gnuplot -e 'directory_path=\"" + directory_path + "\"' eva_scripts/gnuplot_scripts/latency_vs_cardinality.gnuplot"
    print("Generating graph Latency vs. cardinality using command \n\t" + gnu_command)
    os.system(gnu_command)
    print("\tGraphs are generated in the directory : " + os.path.join(directory_path, GRAPHS_DIR) + "\n")

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

def draw_throughput_varying_cardinality(directory_path):    
    # invoke gnuplot script
    gnu_command = "gnuplot -e 'directory_path=\"" + directory_path + "\"' eva_scripts/gnuplot_scripts/throughput_vs_cardinality.gnuplot" 
    print("Generating graph Throughput vs. cardinality using command \n\t" + gnu_command)
    os.system(gnu_command)
    print("\tGraphs are generated in the directory : " + os.path.join(directory_path, GRAPHS_DIR) + "\n")

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

def convert_eps_to_png(directory_path, dpi=1200):
    # if ghostscript is not installed, return
    if os.system("which gs") != 0:
        print("ghostscript is not installed. Skip converting eps files to png files.")
        return    

    # 确保DPI大于1000
    if dpi <= 1000:
        print(f"WARNING: DPI setting ({dpi}) is too low, using 1200 DPI instead.")
        dpi = 1200
    
    eps_files = os.listdir(os.path.join(directory_path, GRAPHS_DIR))
    print(f"Convert eps files in {os.path.join(directory_path, GRAPHS_DIR)} to png files with {dpi} DPI.")
    
    for eps_file in eps_files:
        if eps_file.endswith(".eps"):
            png_file = eps_file.replace(".eps", ".png")
            eps_file_path = os.path.join(directory_path, GRAPHS_DIR, eps_file)
            png_file_path = os.path.join(directory_path, GRAPHS_DIR, png_file)
            
            # 使用ghostscript将EPS转换为PNG
            gs_command = f"gs -dSAFER -dBATCH -dNOPAUSE -dEPSCrop -r{dpi} -sDEVICE=pngalpha -sOutputFile={png_file_path} {eps_file_path}"
            os.system(gs_command)
            print(f"Converted {eps_file} to {png_file} with {dpi} DPI")


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
    analyse_latency_varying_cardinality(directory_path)
    
    create_directory(os.path.join(directory_path, GRAPHS_DIR))
    draw_throughput_varying_cardinality(directory_path)
    draw_latency_varying_cardinality(directory_path)
    convert_eps_to_png(directory_path)


    print("All analyses are done.")