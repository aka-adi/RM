import os
import sys

RAW_DATA_DIR = "raw_data"
DISTILLED_DATA_DIR = "distilled_data"
GRAPHS_DIR = "graphs"

HEADER = '# GL \t Query Latency (ms) \t RQ (ms) \t Update (ms) \t Delete (ms) \t Insert (nums)\n'


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
    Qvec = []
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
            Ivec.append(int(a[-1]))
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

def analyse_exp4_merge(directory_path):
    import re
    raw_dir = os.path.join(directory_path, RAW_DATA_DIR)
    distilled_dir = os.path.join(directory_path, DISTILLED_DATA_DIR)
    if os.path.exists(distilled_dir):
        print(f"WARNING: Distilled data directory '{distilled_dir}' already exists.")
        return
    create_directory(distilled_dir)

    files = [f for f in os.listdir(raw_dir) if f.endswith('.rawdata')]
    if not files:
        print(f"No rawdata files found in {raw_dir}")
        return

    merged_lines = ["# merge_threshold\trange_query_latency(ms)\tupdate_latency(ms)\n"]
    for fname in files:
        src_file = os.path.join(raw_dir, fname)
        ret = latency_analysis(src_file)
        # 线程数从文件名中提取 mh_x
        mh_match = re.search(r'mh_(\d+)', fname)
        mh = int(mh_match.group(1)) if mh_match else 0
        range_query_latency = ret[1] if len(ret) > 1 else 0
        update_latency = ret[2] if len(ret) > 2 else 0
        merged_lines.append(f"{mh}\t{range_query_latency}\t{update_latency}\n")
    # 写入合并后的distilled文件
    merged_distilled = os.path.join(distilled_dir, "exp4_merge_latency_merged.distilled")
    with open(merged_distilled, 'w') as fout:
        fout.writelines(merged_lines)
    print(f"Merged distilled file written to {merged_distilled}")

def draw_exp4_merge_latency(directory_path):
    # 创建graphs目录
    graphs_dir = os.path.join(directory_path, "graphs")
    if not os.path.exists(graphs_dir):
        os.makedirs(graphs_dir)
        print(f"Output directory '{graphs_dir}' has been created.")
    # 调用gnuplot脚本
    gnu_command = f"gnuplot -e 'directory_path=\"{directory_path}\"' eva_scripts/gnuplot_scripts/exp4_merge_latency.gnuplot"
    print("Generating graph Exp4 Merge Latency using command \n\t" + gnu_command)
    os.system(gnu_command)
    print("\tGraphs are generated in the directory : " + graphs_dir + "\n")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python analyse_exp4_merge.py <directory_path> (clean|analyse)")
        sys.exit(1)
    directory_path = sys.argv[1]
    command = sys.argv[2]

    if command == "clean":
        os.system("rm -rf " + os.path.join(directory_path, DISTILLED_DATA_DIR))
        sys.exit(0)

    analyse_exp4_merge(directory_path)
    draw_exp4_merge_latency(directory_path)
    convert_eps_to_png(directory_path)
    print("All analyses are done.")
