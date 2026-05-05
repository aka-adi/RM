import os
import subprocess
import shlex
import time
from decimal import Decimal
M = 1000000

approaches = [
    ('rabit', 'EE'),
    ('cubit-lk', 'EE'),
    ('rabit', 'AE')
]
cardinalities = ['1024']
rows = 10 * M
radio = [Decimal('0.8')]
ranges = [358]
workers = 16
group_len = [64]
total = 200
word_size = 32

def range_query(w, a, e, c, total, queries_ratio, rows, group_len, q_range, v, out_dir):
    index_path = f"BM_uniform_{int(rows / M)}M_{c}_"
    if e == "EE":
        index_path += f"EE_{word_size}"
    elif e == "AE":
        index_path += f"AE_{group_len}_{word_size}"
    else:
        print("ERROR: Unknow encoding mode!!!")
        return

    group_path = f"BM_{int(rows / M)}M_{c}_GE_{group_len}_{word_size}"

    if a == 'cubit-lk':
        cmd = f'../CUBIT/build/nicolas --mode range --approach {a} --workers {w} --number-of-queries {int(total*queries_ratio)} --number-of-udis {int(total*(1-queries_ratio))} --cardinality {c} --index-path {index_path} --number-of-rows {rows} --rows-per-seg 100000 --verbose {v} --encoding-scheme {e} --range {q_range}'
    else:
        cmd = f'./build/nicolas --mode range --approach {a} --workers {w} --number-of-queries {int(total*queries_ratio)} --number-of-udis {int(total*(1-queries_ratio))} --cardinality {c} --index-path {index_path} --number-of-rows {rows} --rows-per-seg 100000 --verbose {v} --encoding-scheme {e} --group-path {group_path} --GE-group-len {group_len} --RQ-length {q_range}'

    output_file = f'{out_dir}/eva_{a}_{e}_latency_{int(rows / M)}M_c_{c}_w_{w}_ratio_{1-queries_ratio}_range_{q_range}_GL_{group_len}.rawdata'
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
    eva_directory_name = f"eva_output/eva_rabit_ee_vs_cubit_{timestamp}"
    os.mkdir(eva_directory_name)
    eva_directory_name = eva_directory_name + "/raw_data"
    os.mkdir(eva_directory_name)

    for a, e in approaches:
        for c in cardinalities:
            for q in radio:
                for r in ranges:
                    for l in group_len:
                        range_query(workers, a, e, c, total, q, rows, l, r, 'true', eva_directory_name)

if __name__ == '__main__':
    main()
