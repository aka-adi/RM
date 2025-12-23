import os
import subprocess
import shlex
import re
import time
from decimal import Decimal
M = 1000000

approaches = ['rabit', 'cubit-lk']
cardinalities = ['256', '512', '1024', '2048']
rows = 1*M
radio = [Decimal('1.0')]
ranges = 0.35
workers = 16
group_len = [2, 4, 8, 16, 32, 64, 128, 256]
total = 200
word_size = 32

def range_query(w, a, c, total, queries_ratio, rows, e, group_len, q_range, v, out_dir):
    index_path = "BM_uniform_" + str(int(rows / M)) + "M_" + str(c) + "_"
    if (e == "EE"):
        index_path = index_path + "EE_" + str(word_size)
    elif (e == "RE"):
        index_path = index_path + "RE_" + str(word_size)
    elif (e == "AE"):
        index_path = index_path + "AE_" + str(group_len) + "_" + str(word_size)
    else:
        print("ERROR: Unknow encoding mode!!!")

    group_path = "BM_" + str(int(rows / M)) + "M_" + str(c) + "_GE_" + str(group_len) + "_" + str(word_size)

    cmd = './build/nicolas --mode range --approach {} --workers {} --number-of-queries {} --number-of-udis {} --cardinality {} --index-path {} --number-of-rows {} --rows-per-seg 100000 --verbose {} --encoding-scheme {} --group-path {} --GE-group-len {} --RQ-length {}'.\
            format(a, w, int(total*queries_ratio), int(total*(1-queries_ratio)), c, index_path, rows, v, e, group_path, group_len, q_range)
    if (a == 'cubit-lk'):
        cmd = '../CUBIT/build/nicolas --mode range --approach {} --workers {} --number-of-queries {} --number-of-udis {} --cardinality {} --index-path {} --number-of-rows {} --rows-per-seg 100000 --verbose {} --encoding-scheme {} --range {}'.\
                format(a, w, int(total*queries_ratio), int(total*(1-queries_ratio)), c, index_path, rows, v, e, q_range)
    
    output_file = out_dir + '/eva_{}_{}_{}M_c_{}_w_{}_ratio_{}_range_{}_GL_{}.rawdata'.format(a, 'latency' if (v == 'true') else 'throughput', int(rows / M), c, w, 1 - queries_ratio, q_range, group_len)

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
    eva_directory_name = f"eva_output/eva_range_{timestamp}"
    os.mkdir(eva_directory_name)
    eva_directory_name = eva_directory_name + "/raw_data"
    os.mkdir(eva_directory_name)

    for a in approaches:
        e = ""
        if a == "rabit":
            e = "AE"
        elif a == "cubit-lk":
            e = "EE"
        elif a == "ub":
            e = "RE"
        else:
            print("ERROR: Unknow encoding mode!!!")
            exit(1)
        for c in cardinalities:
            for q in radio:
                r = int(ranges * float(c))
                if e == "AE":
                    for l in group_len:
                        range_query(workers, a, c, total, q, rows, e, l, r, 'false', eva_directory_name)
                        range_query(workers, a, c, total, q, rows, e, l, r, 'true', eva_directory_name)
                else:
                    l = 0
                    range_query(workers, a, c, total, q, rows, e, l, r, 'false', eva_directory_name)
                    range_query(workers, a, c, total, q, rows, e, l, r, 'true', eva_directory_name)

if __name__ == '__main__':
    main()
