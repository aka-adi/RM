import sys
import numpy as np

def tail_U(filename):
    u_values = []
    with open(filename, 'r') as f:
        for line in f:
            if line.startswith('I '):
                parts = line.strip().split()
                if len(parts) == 2:
                    try:
                        value = float(parts[1])
                        u_values.append(value)
                    except ValueError:
                        continue
    if not u_values:
        print("No 'U' lines found.")
    else:
        print(f"99th percentile U latency: {np.percentile(u_values, 99)}")
        print(f"Mean U latency: {np.mean(u_values)}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python tail_U.py <rawdata_file>")
        sys.exit(1)
    tail_U(sys.argv[1])