import os
import subprocess
import shlex
import time
from decimal import Decimal
M = 1000000

approaches = ['rabit']
cardinalities = ['1024']
rows = 100*M
radio = [Decimal('0.4')]
ranges = 0.35
workers = 16
merge_workers_list = [1, 2, 4]
group_len = [64]
total = 2000
word_size = 32

def range_query(w, mw, a, c, total, queries_ratio, rows, e, group_len, q_range, v, out_dir):
    index_path = "BM_uniform_" + str(int(rows / M)) + "M_" + str(c) + "_"
    if (e == "AE"):
        index_path = index_path + "AE_" + str(group_len) + "_" + str(word_size)
    else:
        print("ERROR: Only AE encoding supported in this script.")

    group_path = "BM_" + str(int(rows / M)) + "M_" + str(c) + "_GE_" + str(group_len) + "_" + str(word_size)

    cmd = './build/nicolas --mode range --approach {} --workers {} --merge-threads {} --number-of-queries {} --number-of-udis {} --cardinality {} --index-path {} --number-of-rows {} --rows-per-seg 100000 --verbose {} --encoding-scheme {} --group-path {} --GE-group-len {} --RQ-length {}'.\
            format(a, w, mw, int(total*queries_ratio), int(total*(1-queries_ratio)), c, index_path, rows, v, e, group_path, group_len, q_range)

    output_file = out_dir + '/eva_{}_{}_{}M_c_{}_w_{}_mw_{}_ratio_{}_range_{}_GL_{}.rawdata'.format(a, 'latency' if (v == 'true') else 'throughput', int(rows / M), c, w, mw, 1 - queries_ratio, q_range, group_len)

    print(cmd)
    result = subprocess.run(shlex.split(cmd), capture_output=True, text=True)
    print(result.stderr)
    with open(output_file, 'a') as f:
        f.write(result.stdout)
    return

def main():
    if not os.path.exists('eva_output'):
        os.mkdir('eva_output')

    timestamp = time.strftime("%y_%m_%d_%H_%M_%S", time.localtime())
    eva_directory_name = f"eva_output/eva_merge_workers_{timestamp}"
    os.mkdir(eva_directory_name)
    eva_directory_name = eva_directory_name + "/raw_data"
    os.mkdir(eva_directory_name)

    for a in approaches:
        e = "AE"
        for c in cardinalities:
            for q in radio:
                r = int(ranges * float(c))
                for l in group_len:
                    for mw in merge_workers_list:
                        range_query(workers, mw, a, c, total, q, rows, e, l, r, 'true', eva_directory_name)

if __name__ == '__main__':
    main()