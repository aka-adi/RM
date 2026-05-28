import os
import sys
import re
import glob

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

# 固定 IRE 区间大小，对应 GL_16
AE_GROUP_SIZE_FIX = 16

# 分段数量与每段行数
# 注意：单段实验使用 SEG_10000100，与运行脚本保持一致。
SEGMENT_SETTINGS = [
    (1, 10000100),
    (100, 100000),
    (400, 25000),
    (800, 12500),
    (1600, 6250),
    (3200, 3125),
    (6400, 1563)
]

SEGMENT_NUMS = [
    item[0] for item in SEGMENT_SETTINGS
]

SEGMENT_SIZES = [
    item[1] for item in SEGMENT_SETTINGS
]

# =========================
# Experiment 1:
# 固定查询范围，测试两个不同更新率
# =========================

# distilled 文件名仍然保留 rangefix_0.15
SEGMENT_RANGE_FIX_LABEL = "0.15"

# rawdata 文件名中实际是 range_150
SEGMENT_RANGE_FIX_VALUE = 150

SEGMENT_UDI_RATIOS = ["0.1", "0.4"]

# =========================
# Experiment 2:
# 固定更新率，测试两个不同查询范围
# =========================

SEGMENT_UDI_FIX = "0.2"

# distilled 文件名仍然保留 range_0.05 和 range_0.45
SEGMENT_QUERY_RANGE_LABELS = ["0.05", "0.45"]

# rawdata 文件名中实际是 range_50 和 range_450
SEGMENT_QUERY_RANGE_VALUES = [50, 450]


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


def bitmap_size_analysis(filename):
    """
    从原始输出文件中解析 Bitmap size。

    原始输出示例：
    Bitmap size (MB): 545
    """

    if not os.path.exists(filename):
        print(f"WARNING: Raw data file '{filename}' does not exist. Skip bitmap size analysis.")
        return None

    pattern = re.compile(r"Bitmap size\s*\(MB\)\s*:\s*([0-9]+(?:\.[0-9]+)?)")

    with open(filename) as f:
        for line in f:
            match = pattern.search(line)

            if match:
                value = float(match.group(1))

                if value.is_integer():
                    return int(value)

                return value

    print(f"WARNING: Bitmap size is not found in '{filename}'.")
    return None


def find_bitmap_size_file_by_segment_size(directory_path, seg_size):
    """
    根据 SEG_xxx 在 raw_data 目录中寻找对应原始实验文件，
    并从中解析 Bitmap size。

    同一个分段大小会在不同更新率和不同查询范围下重复实验。
    由于 Bitmap size 主要由索引结构决定，通常与查询范围和更新率无关，
    因此找到任意一个包含 Bitmap size 的 rawdata 文件即可。
    """

    raw_data_path = os.path.join(directory_path, RAW_DATA_DIR)

    file_pattern = os.path.join(
        raw_data_path,
        "eva_rabit_latency_{}M_c_{}_w_{}_ratio_*_range_*_GL_{}_SEG_{}.rawdata".format(
            int(ROWS / M),
            CARDINALITY,
            WORKERS,
            AE_GROUP_SIZE_FIX,
            seg_size
        )
    )

    candidate_files = sorted(glob.glob(file_pattern))

    if len(candidate_files) == 0:
        print(f"WARNING: No rawdata file found for SEG_{seg_size}.")
        return None, None

    for filename in candidate_files:
        bitmap_size = bitmap_size_analysis(filename)

        if bitmap_size is not None:
            return bitmap_size, filename

    return None, None


def analyse_latency_varying_segment_size_under_UDI(directory_path):
    """
    固定查询范围为 range_150，
    分别在更新率 0.1 和 0.4 下分析分段数量对 RQ / UDI 延迟的影响。
    """

    print("-" * 10)
    print("Analyse latency with varying segment number under different UDI ratios.")

    for udi in SEGMENT_UDI_RATIOS:
        experiment_name = "eva_rabit_latency_{}M_c_{}_w_{}_ratio_{}".format(
            int(ROWS / M),
            CARDINALITY,
            WORKERS,
            udi
        )

        output_file_name = os.path.join(
            directory_path,
            DISTILLED_DATA_DIR,
            experiment_name
            + f"_rangefix_{SEGMENT_RANGE_FIX_LABEL}"
            + f"_GL_{AE_GROUP_SIZE_FIX}"
            + "_vary_SEG.distilled"
        )

        if os.path.exists(output_file_name):
            print(f"Output file '{output_file_name}' already exists. Skip the analysis.")
            continue

        output_file = open(output_file_name, "w")
        output_file.write("# Number of segments \t RQ \t UDI (ms) \n")

        for seg_num, seg_size in zip(SEGMENT_NUMS, SEGMENT_SIZES):
            src_file = os.path.join(
                directory_path,
                RAW_DATA_DIR,
                experiment_name
                + f"_range_{SEGMENT_RANGE_FIX_VALUE}"
                + f"_GL_{AE_GROUP_SIZE_FIX}"
                + f"_SEG_{seg_size}.rawdata"
            )

            ret = latency_analysis(src_file)

            output_file.write("{} \t\t {} \t\t {} \n".format(
                seg_num,
                ret[0],
                ret[1]
            ))

            print("\tAnalyzing rawdata file : " + src_file)
            print("\tNumber of segments : " + str(seg_num))
            print("\tRows per segment   : " + str(seg_size))
            print("\tLatency results : RQ = " + str(ret[0]) + " ms, UDI = " + str(ret[1]) + " ms\n")

        print("Output file is created at " + output_file.name + "\n")
        output_file.close()


def analyse_latency_varying_segment_size_under_range(directory_path):
    """
    固定更新率为 ratio_0.2，
    分别在 range_50 和 range_450 下分析分段数量对 RQ / UDI 延迟的影响。
    """

    print("-" * 10)
    print("Analyse latency with varying segment number under different query ranges.")

    for rq_label, rq_value in zip(SEGMENT_QUERY_RANGE_LABELS, SEGMENT_QUERY_RANGE_VALUES):
        experiment_name = "eva_rabit_latency_{}M_c_{}_w_{}_ratio_{}".format(
            int(ROWS / M),
            CARDINALITY,
            WORKERS,
            SEGMENT_UDI_FIX
        )

        output_file_name = os.path.join(
            directory_path,
            DISTILLED_DATA_DIR,
            "eva_rabit_latency_{}M_c_{}_w_{}_ratiofix_{}_range_{}_GL_{}_vary_SEG.distilled".format(
                int(ROWS / M),
                CARDINALITY,
                WORKERS,
                SEGMENT_UDI_FIX,
                rq_label,
                AE_GROUP_SIZE_FIX
            )
        )

        if os.path.exists(output_file_name):
            print(f"Output file '{output_file_name}' already exists. Skip the analysis.")
            continue

        output_file = open(output_file_name, "w")
        output_file.write("# Number of segments \t RQ \t UDI (ms) \n")

        for seg_num, seg_size in zip(SEGMENT_NUMS, SEGMENT_SIZES):
            src_file = os.path.join(
                directory_path,
                RAW_DATA_DIR,
                experiment_name
                + f"_range_{rq_value}"
                + f"_GL_{AE_GROUP_SIZE_FIX}"
                + f"_SEG_{seg_size}.rawdata"
            )

            ret = latency_analysis(src_file)

            output_file.write("{} \t\t {} \t\t {} \n".format(
                seg_num,
                ret[0],
                ret[1]
            ))

            print("\tAnalyzing rawdata file : " + src_file)
            print("\tNumber of segments : " + str(seg_num))
            print("\tRows per segment   : " + str(seg_size))
            print("\tLatency results : RQ = " + str(ret[0]) + " ms, UDI = " + str(ret[1]) + " ms\n")

        print("Output file is created at " + output_file.name + "\n")
        output_file.close()


def analyse_latency_varying_segment_size(directory_path):
    print("-" * 10)
    print("Analyse the effect of segment number on latency.")

    analyse_latency_varying_segment_size_under_UDI(directory_path)
    analyse_latency_varying_segment_size_under_range(directory_path)


def analyse_bitmap_size_varying_segment_size(directory_path):
    """
    分析不同分段数量 / 分段大小下的 Bitmap size。

    输出文件：
    eva_rabit_bitmap_size_10M_c_1024_w_16_GL_16_vary_SEG.distilled

    输出格式：
    # Number of segments    Rows per segment    Bitmap size (MB)
    """

    print("-" * 10)
    print("Analyse bitmap size with varying segment number.")

    output_file_name = os.path.join(
        directory_path,
        DISTILLED_DATA_DIR,
        "eva_rabit_bitmap_size_{}M_c_{}_w_{}_GL_{}_vary_SEG.distilled".format(
            int(ROWS / M),
            CARDINALITY,
            WORKERS,
            AE_GROUP_SIZE_FIX
        )
    )

    if os.path.exists(output_file_name):
        print(f"Output file '{output_file_name}' already exists. Skip the analysis.")
        return

    output_file = open(output_file_name, "w")
    output_file.write("# Number of segments \t Rows per segment \t Bitmap size (MB) \n")

    for seg_num, seg_size in zip(SEGMENT_NUMS, SEGMENT_SIZES):
        bitmap_size, src_file = find_bitmap_size_file_by_segment_size(directory_path, seg_size)

        if bitmap_size is None:
            bitmap_size = 0

        output_file.write("{} \t\t {} \t\t {} \n".format(
            seg_num,
            seg_size,
            bitmap_size
        ))

        print("\tNumber of segments : " + str(seg_num))
        print("\tRows per segment   : " + str(seg_size))
        print("\tBitmap size        : " + str(bitmap_size) + " MB")

        if src_file is not None:
            print("\tSource rawdata file: " + src_file)

        print()

    print("Output file is created at " + output_file.name + "\n")
    output_file.close()


def draw_latency_varying_segment_size(directory_path):
    gnu_command = (
        "gnuplot -e 'directory_path=\""
        + directory_path
        + "\"' eva_scripts/gnuplot_scripts/latency_vs_segment_size.gnuplot"
    )

    print("Generating graph Latency vs. Segment Number using command \n\t" + gnu_command)
    os.system(gnu_command)
    print("\tGraphs are generated in the directory : " + os.path.join(directory_path, GRAPHS_DIR) + "\n")


def draw_bitmap_size_varying_segment_size(directory_path):
    gnu_command = (
        "gnuplot -e 'directory_path=\""
        + directory_path
        + "\"' eva_scripts/gnuplot_scripts/bitmap_size_vs_segment_size.gnuplot"
    )

    print("Generating graph Bitmap Size vs. Segment Number using command \n\t" + gnu_command)
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
        print("Usage: python analyse_segment_size_latency.py <directory_path> (clean|analyse)")
        sys.exit(1)

    directory_path = sys.argv[1]
    command = sys.argv[2]

    if command == "clean":
        os.system("rm -rf " + os.path.join(directory_path, DISTILLED_DATA_DIR))
        os.system("rm -rf " + os.path.join(directory_path, GRAPHS_DIR))
        sys.exit(0)

    if command != "analyse":
        print("Usage: python analyse_segment_size_latency.py <directory_path> (clean|analyse)")
        sys.exit(1)

    check_rawdata_directory_exist(directory_path)

    create_directory(os.path.join(directory_path, DISTILLED_DATA_DIR))
    analyse_latency_varying_segment_size(directory_path)
    analyse_bitmap_size_varying_segment_size(directory_path)

    create_directory(os.path.join(directory_path, GRAPHS_DIR))
    draw_latency_varying_segment_size(directory_path)
    draw_bitmap_size_varying_segment_size(directory_path)

    convert_eps_to_png(directory_path)

    print("All analyses are done.")