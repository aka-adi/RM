import os
import sys
import re
import glob
import numpy as np

RAW_DATA_DIR = "raw_data"
DISTILLED_DATA_DIR = "distilled_data"
GRAPHS_DIR = "graphs"

DISTILLED_FILENAME = "rabit_ee_vs_cubit_latency.distilled"
HEADER = '# approach\tencoding\tGL\trange\tmean_latency(ms)\tp99_latency(ms)\n'


def create_directory(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        print(f"Output directory '{directory_path}' has been created.")
    else:
        print(
            f"WARNING: Output directory '{directory_path}' already exists.\n"
            f"Skip building the directory and overwrite the existing files."
        )


def latency_analysis(filename, startwith):
    if not os.path.exists(filename):
        print(f"WARNING: Raw data file '{filename}' does not exist. Skip the analysis.")
        return [0, 0]

    latencies = []
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            a = line.split()
            if len(a) != 2:
                continue
            if line.startswith(startwith):
                latencies.append(int(a[-1]) / 1000000)

    if not latencies:
        return [0, 0]

    arr = np.array(latencies)
    mean = round(float(np.mean(arr)), 4)
    p99 = round(float(np.percentile(arr, 99)), 4)
    return [mean, p99]


def parse_filename(fname):
    pattern = (
        r'eva_(\w+)_(\w+)_latency_\d+M_c_\d+_w_\d+_ratio_([\d\.]+)_range_(\d+)_GL_([\d]+)\.rawdata'
    )
    m = re.match(pattern, fname)
    if not m:
        return "-", "-", "-", "-"

    approach = m.group(1)
    encoding = m.group(2)
    rq_range = m.group(4)
    gl = m.group(5)
    return approach, encoding, gl, rq_range


def analyse_data(directory_path):
    raw_dir = os.path.join(directory_path, RAW_DATA_DIR)
    distilled_dir = os.path.join(directory_path, DISTILLED_DATA_DIR)
    create_directory(distilled_dir)

    if not os.path.exists(raw_dir):
        print(f"Raw data directory does not exist: {raw_dir}")
        return None

    files = sorted(f for f in os.listdir(raw_dir) if f.endswith(".rawdata"))
    if not files:
        print(f"No rawdata files found in {raw_dir}")
        return None

    lines = [HEADER]

    for fname in files:
        approach, encoding, gl, rq_range = parse_filename(fname)
        src_file = os.path.join(raw_dir, fname)

        startwith = "RQ " if approach == "rabit" else "Q "
        mean, p99 = latency_analysis(src_file, startwith)

        lines.append(
            f"{approach}\t{encoding}\t{gl}\t{rq_range}\t{mean}\t{p99}\n"
        )

    distilled_file = os.path.join(distilled_dir, DISTILLED_FILENAME)
    with open(distilled_file, "w", encoding="utf-8") as fout:
        fout.writelines(lines)

    print(f"Distilled file written to {distilled_file}")
    return distilled_file


def convert_eps_to_png(directory_path, dpi=1200):
    if os.system("which gs > /dev/null 2>&1") != 0:
        print("ghostscript is not installed. Skip converting eps files to png files.")
        return

    eps_files = glob.glob(os.path.join(directory_path, GRAPHS_DIR, "*.eps"))
    for eps_file in eps_files:
        png_file = eps_file.replace(".eps", ".png")
        gs_command = (
            f"gs -dSAFER -dBATCH -dNOPAUSE -dEPSCrop "
            f"-r{dpi} -sDEVICE=pngalpha "
            f"-sOutputFile={png_file} {eps_file}"
        )
        os.system(gs_command)
        print(
            f"Converted {os.path.basename(eps_file)} "
            f"to {os.path.basename(png_file)} with {dpi} DPI"
        )


def plot_graphs(directory_path):
    distilled_file = os.path.join(
        directory_path,
        DISTILLED_DATA_DIR,
        DISTILLED_FILENAME
    )
    if not os.path.exists(distilled_file):
        print(
            f"Distilled file does not exist: {distilled_file}\n"
            f"Please run analysis first."
        )
        return

    graphs_dir = os.path.join(directory_path, GRAPHS_DIR)
    create_directory(graphs_dir)

    gnuplot_script = os.path.join(
        os.path.dirname(__file__),
        "gnuplot_scripts",
        "rabit_ee_vs_cubit_latency.gnuplot"
    )
    if not os.path.exists(gnuplot_script):
        print(f"Gnuplot script does not exist: {gnuplot_script}")
        return

    gnu_command = f"gnuplot -e 'directory_path=\"{directory_path}\"' {gnuplot_script}"
    print("Generating graph using command:\n\t" + gnu_command)
    os.system(gnu_command)

    print(f"Graphs are generated in the directory: {graphs_dir}\n")
    convert_eps_to_png(directory_path)


def analyse(directory_path, mode="all"):
    if mode == "analyse":
        analyse_data(directory_path)
    elif mode == "plot":
        plot_graphs(directory_path)
    elif mode == "all":
        analyse_data(directory_path)
        plot_graphs(directory_path)
    else:
        print(f"Unknown mode: {mode}")
        print("Supported modes: analyse, plot, all")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) not in (2, 3):
        print("Usage:")
        print("  python analyse_rabit_ee_vs_cubit.py <directory_path>")
        print("  python analyse_rabit_ee_vs_cubit.py <directory_path> <mode>")
        print("Modes:")
        print("  analyse   only run data analysis")
        print("  plot      only generate graphs")
        print("  all       run analysis and plotting (default)")
        sys.exit(1)

    directory_path = sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) == 3 else "all"
    analyse(directory_path, mode)