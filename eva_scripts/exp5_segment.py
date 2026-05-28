import os
import subprocess
import shlex
import time
from decimal import Decimal

M = 1000000

# =========================
# Basic configuration
# =========================

approach = "rabit"
encoding = "AE"

cardinality = "1024"
rows = 10 * M
workers = 16
total = 200
word_size = 32

# 固定 IRE 区间大小
group_len = 16

# 分段数量与每段行数
# 注意：当分段数量为 1 时，将 rows-per-seg 设置为 10000100，
# 使其略大于总行数，避免边界情况下的段划分异常。
segment_settings = [
    (1, 10000100),
    (100, 100000),
    (400, 25000),
    (800, 12500),
    (1600, 6250),
    (3200, 3125),
    (6400, 1563)
]

segment_nums = [
    item[0] for item in segment_settings
]

segment_sizes = [
    item[1] for item in segment_settings
]

assert all(seg_size > 0 for seg_size in segment_sizes)

# 实验 1：固定查询范围，测试两个不同更新率
# 查询范围固定为 range_150
fixed_range = 150

udi_ratios = [
    Decimal("0.1"),
    Decimal("0.4")
]

# 实验 2：固定更新率，测试两个不同查询范围
# 更新率固定为 20%
fixed_udi_ratio = Decimal("0.2")

query_ranges = [
    50,     # 5%
    450     # 45%
]


def build_index_path(rows, cardinality, encoding, group_len):
    index_path = "BM_uniform_" + str(int(rows / M)) + "M_" + str(cardinality) + "_"

    if encoding == "EE":
        index_path = index_path + "EE_" + str(word_size)
    elif encoding == "RE":
        index_path = index_path + "RE_" + str(word_size)
    elif encoding == "AE":
        index_path = index_path + "AE_" + str(group_len) + "_" + str(word_size)
    else:
        print("ERROR: Unknown encoding mode!!!")
        exit(1)

    return index_path


def build_group_path(rows, cardinality, group_len):
    return "BM_" + str(int(rows / M)) + "M_" + str(cardinality) + "_GE_" + str(group_len) + "_" + str(word_size)


def run_segment_latency_exp(
    workers,
    approach,
    cardinality,
    total,
    udi_ratio,
    rows,
    encoding,
    group_len,
    q_range,
    segment_size,
    segment_num,
    out_dir
):
    """
    运行一次 HiBI/rabit latency 实验。

    udi_ratio 表示更新操作比例。
    number-of-queries = total * (1 - udi_ratio)
    number-of-udis    = total * udi_ratio

    segment_num 表示分段数量；
    segment_size 表示实际传入 --rows-per-seg 的每段行数。
    """

    queries_ratio = Decimal("1.0") - udi_ratio

    index_path = build_index_path(rows, cardinality, encoding, group_len)
    group_path = build_group_path(rows, cardinality, group_len)

    cmd = (
        "./build/nicolas "
        "--mode range "
        "--approach {} "
        "--workers {} "
        "--number-of-queries {} "
        "--number-of-udis {} "
        "--cardinality {} "
        "--index-path {} "
        "--number-of-rows {} "
        "--rows-per-seg {} "
        "--verbose true "
        "--encoding-scheme {} "
        "--group-path {} "
        "--GE-group-len {} "
        "--RQ-length {}"
    ).format(
        approach,
        workers,
        int(total * queries_ratio),
        int(total * udi_ratio),
        cardinality,
        index_path,
        rows,
        segment_size,
        encoding,
        group_path,
        group_len,
        q_range
    )

    output_file = (
        out_dir
        + "/eva_{}_latency_{}M_c_{}_w_{}_ratio_{}_range_{}_GL_{}_SEG_{}.rawdata"
        .format(
            approach,
            int(rows / M),
            cardinality,
            workers,
            str(udi_ratio),
            q_range,
            group_len,
            segment_size
        )
    )

    print("=" * 80)
    print("Running segment-number latency experiment")
    print("UDI ratio        :", udi_ratio)
    print("Query range      :", q_range)
    print("Segment number   :", segment_num)
    print("Rows per segment :", segment_size)
    print("Output file      :", output_file)
    print("Command          :", cmd)

    result = subprocess.run(shlex.split(cmd), capture_output=True, text=True)

    if result.stderr:
        print("stderr:")
        print(result.stderr)

    with open(output_file, "a") as f:
        f.write(result.stdout)

    print("Finished:", output_file)
    print()


def main():
    if not os.path.exists("eva_output"):
        os.mkdir("eva_output")

    timestamp = time.strftime("%y_%m_%d_%H_%M_%S", time.localtime())
    eva_directory_name = f"eva_output/eva_segment_size_latency_{timestamp}"
    os.mkdir(eva_directory_name)

    raw_data_dir = eva_directory_name + "/raw_data"
    os.mkdir(raw_data_dir)

    print("Output directory:", eva_directory_name)
    print("Raw data directory:", raw_data_dir)
    print()

    print("Segment settings:")
    for seg_num, seg_size in zip(segment_nums, segment_sizes):
        print(f"  segment number = {seg_num}, rows-per-seg = {seg_size}")
    print()

    # ======================================================
    # 实验一：固定查询范围为 range_150，测试不同更新率下的分段数量影响
    # ======================================================

    print("#" * 80)
    print("Experiment Group 1: fixed query range = 150, varying UDI ratio")
    print("#" * 80)

    for udi_ratio in udi_ratios:
        for segment_num, segment_size in zip(segment_nums, segment_sizes):
            run_segment_latency_exp(
                workers=workers,
                approach=approach,
                cardinality=cardinality,
                total=total,
                udi_ratio=udi_ratio,
                rows=rows,
                encoding=encoding,
                group_len=group_len,
                q_range=fixed_range,
                segment_size=segment_size,
                segment_num=segment_num,
                out_dir=raw_data_dir
            )

    # ======================================================
    # 实验二：固定更新率为 20%，测试不同查询范围下的分段数量影响
    # ======================================================

    print("#" * 80)
    print("Experiment Group 2: fixed UDI ratio = 20%, varying query range")
    print("#" * 80)

    for q_range in query_ranges:
        for segment_num, segment_size in zip(segment_nums, segment_sizes):
            run_segment_latency_exp(
                workers=workers,
                approach=approach,
                cardinality=cardinality,
                total=total,
                udi_ratio=fixed_udi_ratio,
                rows=rows,
                encoding=encoding,
                group_len=group_len,
                q_range=q_range,
                segment_size=segment_size,
                segment_num=segment_num,
                out_dir=raw_data_dir
            )

    print("All segment-number latency experiments are done.")
    print("Result directory:", eva_directory_name)
    print()
    print("Next step:")
    print("python analyse_segment_size_latency.py {} analyse".format(eva_directory_name))


if __name__ == "__main__":
    main()