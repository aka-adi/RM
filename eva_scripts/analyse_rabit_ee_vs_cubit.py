import os
import sys

RAW_DATA_DIR = "raw_data"
DISTILLED_DATA_DIR = "distilled_data"
GRAPHS_DIR = "graphs"

M = 1000000

# =========================
# Basic configuration
# =========================

ROWS = 10 * M
CARDINALITY = 1024
WORKERS = 16
GROUP_LEN = 64

APPROACHES = [
    ("rabit", "EE", "HiBI-EE"),
    ("cubit-lk", "EE", "CUBIT-EE")
]

# 实验设置：
# 查询范围 5%，更新率 40%
# 查询范围 1%，更新率 20%
EXPERIMENTS = [
    {
        "query_range": 50,
        "query_range_label": "0.05",
        "udi_ratio": "0.4",
        "title": "查询范围 = 5%，更新率 = 40%"
    },
    {
        "query_range": 10,
        "query_range_label": "0.01",
        "udi_ratio": "0.2",
        "title": "查询范围 = 1%，更新率 = 20%"
    }
]


def check_rawdata_directory_exist(path):
    if os.path.isdir(path):
        data_path = os.path.join(path, RAW_DATA_DIR)
        if os.path.isdir(data_path):
            print(f"Processing the raw data in '{path}'.")
            return True

    print(f"The directory '{path}' is not valid.")
    sys.exit(1)


def create_directory(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        print(f"Output directory '{directory_path}' has been created.")
    else:
        print(
            f"WARNING: Output directory '{directory_path}' already exists.\n"
            f"Skip building the directory and overwrite the existing files."
        )


def latency_analysis(filename):
    """
    从原始输出文件中解析查询延迟和更新延迟。

    原始输出示例：
    RQ 568598300
    U  12345678
    D  12345678
    I  12345678

    单位：ns
    输出：ms
    """

    if not os.path.exists(filename):
        print(f"WARNING: Raw data file '{filename}' does not exist. Skip the analysis.")
        return [0, 0]

    rq_vec = []
    udi_vec = []

    with open(filename) as f:
        for line in f:
            a = line.split()

            if len(a) != 2:
                continue

            if line.startswith("Q ") or line.startswith("RQ "):
                rq_vec.append(int(a[-1]) / 1000000)
            elif line.startswith("U ") or line.startswith("D ") or line.startswith("I "):
                udi_vec.append(int(a[-1]) / 1000000)

    if len(rq_vec) != 0:
        rq_latency = round(sum(rq_vec) / len(rq_vec), 2)
    else:
        rq_latency = 0

    if len(udi_vec) != 0:
        udi_latency = round(sum(udi_vec) / len(udi_vec), 2)
    else:
        udi_latency = 0

    return [rq_latency, udi_latency]


def analyse_latency_rabit_ee_vs_cubit(directory_path):
    """
    分析 HiBI-EE 与 CUBIT-EE 在两组实验设置下的查询延迟和更新延迟。

    输出文件示例：
    eva_rabit_ee_vs_cubit_latency_10M_c_1024_w_16_ratio_0.4_range_0.05_GL_64.distilled
    eva_rabit_ee_vs_cubit_latency_10M_c_1024_w_16_ratio_0.2_range_0.01_GL_64.distilled
    """

    print("-" * 10)
    print("Analyse latency of HiBI-EE and CUBIT-EE.")

    for exp in EXPERIMENTS:
        q_range = exp["query_range"]
        q_label = exp["query_range_label"]
        udi_ratio = exp["udi_ratio"]

        output_file_name = os.path.join(
            directory_path,
            DISTILLED_DATA_DIR,
            "eva_rabit_ee_vs_cubit_latency_{}M_c_{}_w_{}_ratio_{}_range_{}_GL_{}.distilled".format(
                int(ROWS / M),
                CARDINALITY,
                WORKERS,
                udi_ratio,
                q_label,
                GROUP_LEN
            )
        )

        if os.path.exists(output_file_name):
            print(f"Output file '{output_file_name}' already exists. Skip the analysis.")
            continue

        output_file = open(output_file_name, "w")
        output_file.write("# Method \t RQ \t UDI (ms) \n")

        for approach, encoding, method_name in APPROACHES:
            src_file = os.path.join(
                directory_path,
                RAW_DATA_DIR,
                "eva_{}_{}_latency_{}M_c_{}_w_{}_ratio_{}_range_{}_GL_{}.rawdata".format(
                    approach,
                    encoding,
                    int(ROWS / M),
                    CARDINALITY,
                    WORKERS,
                    udi_ratio,
                    q_range,
                    GROUP_LEN
                )
            )

            ret = latency_analysis(src_file)

            output_file.write("{} \t\t {} \t\t {} \n".format(
                method_name,
                ret[0],
                ret[1]
            ))

            print("\tAnalyzing rawdata file : " + src_file)
            print("\tMethod : " + method_name)
            print("\tRange  : " + q_label)
            print("\tUDI    : " + udi_ratio)
            print("\tLatency results : RQ = " + str(ret[0]) + " ms, UDI = " + str(ret[1]) + " ms\n")

        print("Output file is created at " + output_file.name + "\n")
        output_file.close()


def draw_latency_rabit_ee_vs_cubit(directory_path):
    gnu_command = (
        "gnuplot -e 'directory_path=\""
        + directory_path
        + "\"' eva_scripts/gnuplot_scripts/rabit_ee_vs_cubit_latency.gnuplot"
    )

    print("Generating graph HiBI-EE vs. CUBIT-EE latency using command \n\t" + gnu_command)
    os.system(gnu_command)
    print("\tGraphs are generated in the directory : " + os.path.join(directory_path, GRAPHS_DIR) + "\n")


def convert_eps_to_png(directory_path, dpi=1200):
    if os.system("which gs") != 0:
        print("ghostscript is not installed. Skip converting eps files to png files.")
        return

    if dpi <= 1000:
        print(f"WARNING: DPI setting ({dpi}) is too low, using 1200 DPI instead.")
        dpi = 1200

    graphs_path = os.path.join(directory_path, GRAPHS_DIR)
    eps_files = os.listdir(graphs_path)

    print(f"Convert eps files in {graphs_path} to png files with {dpi} DPI.")

    for eps_file in eps_files:
        if eps_file.endswith(".eps"):
            png_file = eps_file.replace(".eps", ".png")
            eps_file_path = os.path.join(graphs_path, eps_file)
            png_file_path = os.path.join(graphs_path, png_file)

            gs_command = (
                f"gs -dSAFER -dBATCH -dNOPAUSE -dEPSCrop "
                f"-r{dpi} -sDEVICE=pngalpha "
                f"-sOutputFile={png_file_path} {eps_file_path}"
            )

            os.system(gs_command)
            print(f"Converted {eps_file} to {png_file} with {dpi} DPI")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python analyse_rabit_ee_vs_cubit_latency.py <directory_path> (clean|analyse)")
        sys.exit(1)

    directory_path = sys.argv[1]
    command = sys.argv[2]

    if command == "clean":
        os.system("rm -rf " + os.path.join(directory_path, DISTILLED_DATA_DIR))
        os.system("rm -rf " + os.path.join(directory_path, GRAPHS_DIR))
        sys.exit(0)

    if command != "analyse":
        print("Usage: python analyse_rabit_ee_vs_cubit_latency.py <directory_path> (clean|analyse)")
        sys.exit(1)

    check_rawdata_directory_exist(directory_path)

    create_directory(os.path.join(directory_path, DISTILLED_DATA_DIR))
    analyse_latency_rabit_ee_vs_cubit(directory_path)

    create_directory(os.path.join(directory_path, GRAPHS_DIR))
    draw_latency_rabit_ee_vs_cubit(directory_path)

    convert_eps_to_png(directory_path)

    print("All analyses are done.")