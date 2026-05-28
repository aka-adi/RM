import os
import subprocess
import shlex
import time
from decimal import Decimal

M = 1000000

# =========================
# Basic configuration
# =========================

approaches = [
    ("rabit", "EE"),
    ("cubit-lk", "EE")
]

cardinalities = ["1024"]

rows = 10 * M
workers = 16
total = 200
word_size = 32

# EE 实验中 group_len 不参与编码，但为了保持文件命名和脚本接口统一，保留 GL_64
group_lens = [
    64
]

# 固定分段大小
rows_per_seg = 100000

# 实验设置：
# 查询范围 5%，更新率 40% -> range_50, ratio_0.4
# 查询范围 1%，更新率 20% -> range_10, ratio_0.2
experiments = [
    {
        "query_range": 50,
        "query_range_label": "0.05",
        "udi_ratio": Decimal("0.4")
    },
    {
        "query_range": 10,
        "query_range_label": "0.01",
        "udi_ratio": Decimal("0.2")
    }
]


def build_index_path(rows, cardinality, encoding, group_len):
    index_path = f"BM_uniform_{int(rows / M)}M_{cardinality}_"

    if encoding == "EE":
        index_path += f"EE_{word_size}"
    elif encoding == "AE":
        index_path += f"AE_{group_len}_{word_size}"
    else:
        print("ERROR: Unknown encoding mode!!!")
        exit(1)

    return index_path


def build_group_path(rows, cardinality, group_len):
    return f"BM_{int(rows / M)}M_{cardinality}_GE_{group_len}_{word_size}"


def range_query(
    workers,
    approach,
    encoding,
    cardinality,
    total,
    udi_ratio,
    rows,
    group_len,
    q_range,
    verbose,
    out_dir
):
    """
    运行一次 range-query latency 实验。

    udi_ratio 表示 UDI 更新操作比例。
    query_ratio = 1 - udi_ratio。
    """

    query_ratio = Decimal("1.0") - udi_ratio

    index_path = build_index_path(rows, cardinality, encoding, group_len)
    group_path = build_group_path(rows, cardinality, group_len)

    number_of_queries = int(total * query_ratio)
    number_of_udis = int(total * udi_ratio)

    if approach == "cubit-lk":
        cmd = (
            "../CUBIT/build/nicolas "
            "--mode range "
            "--approach {} "
            "--workers {} "
            "--number-of-queries {} "
            "--number-of-udis {} "
            "--cardinality {} "
            "--index-path {} "
            "--number-of-rows {} "
            "--rows-per-seg {} "
            "--verbose {} "
            "--encoding-scheme {} "
            "--range {}"
        ).format(
            approach,
            workers,
            number_of_queries,
            number_of_udis,
            cardinality,
            index_path,
            rows,
            rows_per_seg,
            verbose,
            encoding,
            q_range
        )
    else:
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
            "--verbose {} "
            "--encoding-scheme {} "
            "--group-path {} "
            "--GE-group-len {} "
            "--RQ-length {}"
        ).format(
            approach,
            workers,
            number_of_queries,
            number_of_udis,
            cardinality,
            index_path,
            rows,
            rows_per_seg,
            verbose,
            encoding,
            group_path,
            group_len,
            q_range
        )

    output_file = (
        out_dir
        + "/eva_{}_{}_latency_{}M_c_{}_w_{}_ratio_{}_range_{}_GL_{}.rawdata"
        .format(
            approach,
            encoding,
            int(rows / M),
            cardinality,
            workers,
            str(udi_ratio),
            q_range,
            group_len
        )
    )

    print("=" * 80)
    print("Running latency experiment")
    print("Approach         :", approach)
    print("Encoding         :", encoding)
    print("Query ratio      :", query_ratio)
    print("UDI ratio        :", udi_ratio)
    print("Query range      :", q_range)
    print("Rows per segment :", rows_per_seg)
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
    eva_directory_name = f"eva_output/eva_rabit_ee_vs_cubit_{timestamp}"
    os.mkdir(eva_directory_name)

    raw_data_dir = eva_directory_name + "/raw_data"
    os.mkdir(raw_data_dir)

    print("Output directory:", eva_directory_name)
    print("Raw data directory:", raw_data_dir)
    print()

    for approach, encoding in approaches:
        for cardinality in cardinalities:
            for exp in experiments:
                for group_len in group_lens:
                    range_query(
                        workers=workers,
                        approach=approach,
                        encoding=encoding,
                        cardinality=cardinality,
                        total=total,
                        udi_ratio=exp["udi_ratio"],
                        rows=rows,
                        group_len=group_len,
                        q_range=exp["query_range"],
                        verbose="true",
                        out_dir=raw_data_dir
                    )

    print("All experiments are done.")
    print("Result directory:", eva_directory_name)
    print()
    print("Next step:")
    print("python analyse_rabit_ee_vs_cubit_latency.py {} analyse".format(eva_directory_name))


if __name__ == "__main__":
    main()