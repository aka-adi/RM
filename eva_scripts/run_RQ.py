import os
import subprocess
import shlex
import re
import time
from decimal import Decimal
M = 1000000

approaches = ['rabit', 'cubit-lk', 'ub']
cardinalities = ['1000']
rows = 100*M
radio = [Decimal('0'), Decimal('0.1'), Decimal('0.2'), Decimal('0.4'), Decimal('0.8'), Decimal('0.9'), Decimal('1.0')]
ranges = [50, 100, 150, 200, 250, 300, 350, 400, 450]
workers = 16
group_len = [100, 200, 400]
total = 200
word_size = 32


# def run_throughput(cmd_args):
#     #print(f"Running command: {' '.join(cmd_args)}")
#     result = subprocess.run(cmd_args, capture_output=True, text=True)

#     pattern = r"\d+\.?\d*"
#     find_pattern = r"Throughput"

#     output_lines = result.stdout.splitlines()
#     c_line=0
#     while output_lines[c_line].find(find_pattern) == -1:
#         c_line += 1
#     number_array = []
#     while c_line < len(output_lines):
#         tenth_line = output_lines[c_line]
#         numbers = re.findall(pattern, tenth_line)
#         number_array.append(numbers[0])
#         c_line += 3
#     assert len(number_array) == workers
#     average_number = 0.0
#     for i in range(1, len(number_array) - 1):
#         average_number += float(number_array[i])
#     average_number = average_number / (len(number_array) - 2)
#     return average_number

def range_query(w, a, c, total, queries_ratio, rows, e, group_len, q_range, v, out_dir):
    index_path = "BM_" + str(int(rows / M)) + "M_" + str(c) + "_"
    if (e == "EE"):
        index_path = index_path + "EE_" + str(word_size)
    elif (e == "RE"):
        index_path = index_path + "RE_" + str(word_size)
    elif (e == "GE"):
        index_path = index_path + "EE_" + str(word_size)
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
            e = "GE"
        elif a == "cubit-lk":
            e = "EE"
        elif a == "ub":
            e = "RE"
        else:
            print("ERROR: Unknow encoding mode!!!")
            exit(1)
        for c in cardinalities:
            for q in radio:
                for r in ranges:
                    if e == "GE":
                        for l in group_len:
                            range_query(workers, a, c, total, q, rows, e, l, r, 'false', eva_directory_name)
                            range_query(workers, a, c, total, q, rows, e, l, r, 'true', eva_directory_name)
                    else:
                        l = 0
                        range_query(workers, a, c, total, q, rows, e, l, r, 'false', eva_directory_name)
                        range_query(workers, a, c, total, q, rows, e, l, r, 'true', eva_directory_name)

if __name__ == '__main__':
    main()
