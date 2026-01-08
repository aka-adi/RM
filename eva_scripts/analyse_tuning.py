import os
import sys

RAW_DATA_DIR = "raw_data"
DISTILLED_DATA_DIR = "distilled_data"
GRAPHS_DIR = "graphs"

ROWS = (10*1000*1000)
CARDINALITYS = [256, 512, 1024, 2048]
WORKERS = 16
ALGORITHMS = ["rabit"]

UDI_RATIO_RE = ["0.0", "0.1", "0.2", "0.4"]
UDI_RATIO_NORMAL = ["0.0", "0.1", "0.2", "0.4", "0.6"]

RQ_RANGE_FIX = 0.35

RQ_RANGE = [0.35]
UDI_RATIO_FIX = 0.2

AE_GROUP_SIZES = [2, 4, 8, 16, 32, 64, 128, 256]

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

def latency_analysis(filename):
    if not os.path.exists(filename):
        print(f"WARNING: Raw data file '{filename}' does not exist. Skip the analysis.")
        return []
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

def analyse_latency_varying_cardinality(directory_path):
    print ('-' * 10)
    print ('Analyse the latency of range queries with varying range.')
    
    for cc in CARDINALITYS:
        for alg in ALGORITHMS:
            experiment_name = "eva_{}_latency_{}M_c_{}_w_{}_ratio_{}".format(alg, int(ROWS/1000000), cc, WORKERS, UDI_RATIO_FIX)
            output_file_name = os.path.join(directory_path, DISTILLED_DATA_DIR, experiment_name + f".distilled")

            if os.path.exists(output_file_name):
                print(f"Output file '{output_file_name}' already exists. Skip the analysis.")
                continue

            output_file = open(output_file_name, 'w')
            output_file.write('# GL \t Query Latency (ms) \t RQ (ms) \t Update (ms) \t Delete (ms) \t Insert (ms)\n')

            for rq_range in RQ_RANGE:
                src_file_p = os.path.join(directory_path, RAW_DATA_DIR, experiment_name + f"_range_{int(rq_range*cc)}_")
                for gl in AE_GROUP_SIZES:
                    src_file = src_file_p + f"GL_{gl}.rawdata"

                    ret = latency_analysis(src_file)

                    # print out latency values in ret to a single line
                    output_file.write('{} \t\t {} \n'.format(gl, "           ".join(map(str, ret))))
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

    analyse_latency_varying_cardinality(directory_path)

    print("All analyses are done.")