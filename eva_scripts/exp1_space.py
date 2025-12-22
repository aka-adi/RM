import os
import subprocess
import csv


def get_dir_size(path):
    """获取目录大小，单位为MB"""
    try:
        result = subprocess.run(
            ['du', '-sm', path],
            capture_output=True,
            text=True,
            check=True
        )
        return float(result.stdout.split()[0])
    except Exception as e:
        print(f"Error getting size for {path}: {e}")
        return None


def parse_folder_name(folder_name):
    """解析文件夹名称，提取相关信息"""
    parts = folder_name.split('_')
    
    # 确保是BM开头的文件夹
    if parts[0] != 'BM':
        return None
    
    # 提取数据集类型（如census1881、uniform等）
    dataset = parts[1]
    
    # 提取行数和基数
    rows = None
    base = None
    encoding = None
    len_param = None
    
    # 查找编码类型（AE/RE/EE）的位置
    encoding_index = -1
    for i, part in enumerate(parts):
        if part in ['AE', 'RE', 'EE']:
            encoding_index = i
            encoding = part
            # 如果是AE类型，获取下一个参数作为长度
            if part == 'AE' and i + 1 < len(parts):
                len_param = parts[i + 1]
            break
    
    if not encoding:
        return None
    
    # 提取行数和基数（位于数据集类型和编码类型之间）
    if encoding_index >= 4:
        rows = parts[2]  # 第3个部分是行数
        base = parts[3]  # 第4个部分是基数
    
    return dataset, encoding, len_param, rows, base


def main():
    base_dir = '/home/xxxw/RM'
    
    # 存储分类结果 - 新的结构: results[dataset][rows][base][category]
    results = {}
    
    # 遍历所有以BM开头的文件夹
    for item in os.listdir(base_dir):
        item_path = os.path.join(base_dir, item)
        if os.path.isdir(item_path) and item.startswith('BM'):
            # 获取文件夹大小
            size = get_dir_size(item_path)
            if size is None:
                continue
            
            # 解析文件夹名称
            parsed = parse_folder_name(item)
            if parsed is None:
                print(f"无法解析文件夹名称: {item}")
                continue
            
            dataset, encoding, len_param, rows, base = parsed
            
            # 按要求分类
            if encoding == 'AE':
                # AE类型按AE-len组合分类
                category = f"{encoding}-{len_param}"
            else:
                # RE和EE类型直接按编码分类
                category = encoding
            
            # 初始化分类字典 - 多层结构: dataset -> rows -> base -> category
            if dataset not in results:
                results[dataset] = {}
            if rows not in results[dataset]:
                results[dataset][rows] = {}
            if base not in results[dataset][rows]:
                results[dataset][rows][base] = {}
            if category not in results[dataset][rows][base]:
                results[dataset][rows][base][category] = []
            
            # 添加结果
            results[dataset][rows][base][category].append({
                'folder': item,
                'size_mb': size
            })
    
    # 准备CSV输出数据
    csv_data = []
    csv_data.append(['Dataset', 'Rows', 'Base', 'Encoding', 'Average_Size_MB'])
    
    # 输出美化的表格
    print("\n" + "=" * 80)
    print("{:<20} {:<10} {:<10} {:<15} {:<20}".format(
        'Dataset', 'Rows', 'Base', 'Encoding', 'Average_Size_MB'
    ))
    print("-" * 80)
    
    # 遍历新的多层结构
    for dataset in sorted(results.keys()):
        for rows in sorted(results[dataset].keys()):
            for base in sorted(results[dataset][rows].keys()):
                for category in sorted(results[dataset][rows][base].keys()):
                    items = results[dataset][rows][base][category]
                    # 计算平均大小
                    avg_size = sum(item['size_mb'] for item in items) / len(items)
                    
                    # 直接使用合并后的category作为Encoding值
                    encoding = category
                    
                    # 打印表格行
                    print("{:<20} {:<10} {:<10} {:<15} {:<20.2f}".format(
                        dataset, rows, base, encoding, avg_size
                    ))
                    
                    # 添加到CSV数据
                    csv_data.append([dataset, rows, base, encoding, f"{avg_size:.2f}"])
    
    print("=" * 80 + "\n")
    
    # 输出每个文件夹的详细信息（可选）
    print("各文件夹详细信息：")
    print("-" * 100)
    print("{:<50} {:<10} {:<10} {:<15} {:<20}".format('Folder_Name', 'Rows', 'Base', 'Encoding', 'Size_MB'))
    print("-" * 100)
    
    # 遍历所有文件夹并输出详细信息
    for dataset in sorted(results.keys()):
        for rows in sorted(results[dataset].keys()):
            for base in sorted(results[dataset][rows].keys()):
                for category in sorted(results[dataset][rows][base].keys()):
                    items = results[dataset][rows][base][category]
                    for item in sorted(items, key=lambda x: x['folder']):
                        print("{:<50} {:<10} {:<10} {:<15} {:<20.2f}".format(
                            item['folder'], rows, base, category, item['size_mb']
                        ))
    
    print("-" * 100)
    
    # 保存为CSV文件
    csv_filename = 'space_analysis.csv'
    with open(csv_filename, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerows(csv_data)
    
    print(f"\n结果已保存到CSV文件: {csv_filename}")


if __name__ == "__main__":
    main()