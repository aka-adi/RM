import os
import glob
import struct
import random
from datetime import datetime


def create_done_file(base_filename):
    """
    创建一个标记任务完成的done文件
    
    参数：
    base_filename: str - 基础文件名（不包含_done后缀）
    
    返回：
    bool - 如果成功创建done文件则返回True，如果文件已存在则返回False
    """
    done_filename = base_filename + "_done"
    
    # 检查done文件是否已存在
    if os.path.isfile(done_filename):
        print(f"Done file {done_filename} already exists. Task may be completed.")
        return False
    
    # 创建done文件并写入内容
    try:
        with open(done_filename, 'wb') as f:
            # 写入创建时间
            f.write("Created in ".encode("utf-8"))
            f.write(str(datetime.now()).encode("utf-8"))
        
        print(f"Done file {done_filename} has been created.")
        return True
    except Exception as e:
        print(f"Error creating done file: {e}")
        return False


def verify_data(output_filename, original_data):
    """
    验证写入文件的数据与原始数据是否一致
    
    参数：
    output_filename: str - 输出文件名
    original_data: list - 原始数据数组
    
    返回：
    bool - 如果数据一致返回True，否则返回False
    """
    try:
        # 读取文件数据（每个整数占4字节）
        file_data = []
        with open(output_filename, 'rb') as f:
            while True:
                data = f.read(4)  # 每次读取4字节（一个int）
                if not data:
                    break
                file_data.append(struct.unpack('i', data)[0])
        
        # 比较数据长度
        if len(file_data) != len(original_data):
            print(f"验证失败: 数据长度不一致，文件中 {len(file_data)} 个整数，原始数据 {len(original_data)} 个整数")
            return False
        
        # 比较数据内容
        for i, (file_val, orig_val) in enumerate(zip(file_data, original_data)):
            if file_val != orig_val:
                print(f"验证失败: 索引 {i} 处数据不一致，文件中 {file_val}，原始数据 {orig_val}")
                return False
        
        print(f"验证成功: 文件 {output_filename} 中的数据与原始数据完全一致")
        return True
    except Exception as e:
        print(f"验证过程中发生错误: {e}")
        return False


def process_data_files(input_realdata):
    """
    处理文件夹下所有数据文件，将数据存储为一维数组并保存到文件中
    
    参数:
    input_realdata: 数据文件名
    """
    input_dir = f"./realdata/{input_realdata}"
    # 检查输入目录是否存在
    if not os.path.exists(input_dir):
        print(f"错误: 输入目录 {input_dir} 不存在")
        return
    
    
    # 获取输入目录下所有符合命名规则的文件（census1881.csv*.txt）
    data_files = glob.glob(os.path.join(input_dir, f"{input_realdata}.csv*.txt"))
    
    if not data_files:
        print(f"警告: 在 {input_dir} 目录下未找到符合格式的文件")
        return
    
    print(f"找到 {len(data_files)} 个数据文件，开始处理...")
    
    # 首先确定最大行号
    max_row = 0
    for data_file in data_files:
        try:
            with open(data_file, 'r') as f:
                content = f.read().strip()
                if content:
                    row_numbers = [int(num) for num in content.split(',') if num.strip().isdigit()]
                    if row_numbers:
                        current_max = max(row_numbers)
                        if current_max > max_row:
                            max_row = current_max
        except Exception as e:
            print(f"警告: 读取文件 {os.path.basename(data_file)} 时发生错误: {e}")
    
    if max_row == 0:
        print("错误: 未找到有效的行号数据")
        return
    
    print(f"\n确定最大行号: {max_row}")
    
    # 创建一维数组（大小为max_row + 1，行号从1开始）
    data_array = [0] * (max_row + 1)  # 初始化为0，下标0未使用
    
    max_value = 0
    
    # 处理每个文件，填充数组
    for data_file in data_files:
        filename = os.path.basename(data_file)
        
        # 从文件名中提取值（格式：census1881.csvX.txt，提取X）
        try:
            value_part = filename.split('.')[1]  # 获取 csvX 部分
            value = int(value_part[3:]) + 1  # 去掉 'csv' 前缀，得到值
            if value > max_value:
                max_value = value
        except (IndexError, ValueError):
            print(f"警告: 无法从文件名 {filename} 中提取值，跳过该文件")
            continue
        
        try:
            with open(data_file, 'r') as f:
                content = f.read().strip()
                if content:
                    # 提取行号列表
                    row_numbers = [int(num) for num in content.split(',') if num.strip().isdigit()]
                    
                    # 将值填充到对应行号的数组位置
                    for row in row_numbers:
                        if 1 <= row <= max_row:  # 确保行号在有效范围内
                            data_array[row] = value
                        else:
                            print(f"警告: 行号 {row} 超出有效范围 (1-{max_row})，跳过")
                    
                    print(f"处理文件: {filename} (值: {value})，更新了 {len(row_numbers)} 个行号")
                    
        except Exception as e:
            print(f"错误: 处理文件 {filename} 时发生错误: {e}")
    
    # 数组第一个元素为0则舍弃
    while data_array[0] == 0:
        data_array = data_array[1:]
    while data_array[-1] == 0:
        data_array = data_array[:-1]
    
    max_row = len(data_array)
    
    # 数组写入文件中 - 使用struct.pack('i', value)方式
    output_filename = f"{input_realdata}_dataset_{max_row}_{max_value}"
    
    numsss = 0
    
    with open(output_filename, 'wb') as f:
        for value in data_array:
            if value != 0:
                numsss += 1
            f.write(struct.pack('i', value))
    
    print(f"\n数据已成功写入文件: {output_filename}")
    print(f"有效数据数量: {numsss}")
    
    # 验证数据正确性
    verify_data(output_filename, data_array)
    
    # 创建done文件
    create_done_file(output_filename)


def generate_random_data(filename, size, C):
    """
    生成随机数据并使用struct.pack('i', r.randint(1, C))方式写入文件
    
    参数:
    filename: str - 输出文件名
    size: int - 数据大小（元素数量）
    C: int - 随机数范围（1到C）
    """
    import random as r
    
    print(f"\n开始生成随机数据: {size}个元素，范围1-{C}")
    
    with open(filename, 'wb') as f:
        for _ in range(size):
            # 使用r.randint(1, C)生成随机整数，然后使用struct.pack('i', ...)写入
            f.write(struct.pack('i', r.randint(1, C)))
    
    print(f"随机数据已成功写入文件: {filename}")
    
    # 验证数据
    # 重新读取文件验证
    try:
        valid_count = 0
        with open(filename, 'rb') as f:
            while True:
                data = f.read(4)
                if not data:
                    break
                value = struct.unpack('i', data)[0]
                if 1 <= value <= C:
                    valid_count += 1
                else:
                    print(f"警告: 找到无效值 {value}")
        
        print(f"验证结果: 共读取 {valid_count} 个有效随机数")
    except Exception as e:
        print(f"验证随机数据时发生错误: {e}")


# 使用示例
if __name__ == "__main__":
    # 配置参数
    input_data = "census1881" 
    
    # 调用函数处理真实数据
    process_data_files(input_data)
    
    # 可选：生成随机数据示例
    # generate_random_data("random_data", 1000, 100)