import os
import glob
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
    if data_array[1] == 0:
        data_array = data_array[1:]
        max_row -= 1
    
    # 数组写入文件中
    output_filename = f"{input_realdata}_dataset_{max_row}_{max_value}"
    # 二进制写入
    with open(output_filename, 'wb') as f:
        f.write(bytearray(data_array))
    
    # 创建done文件
    create_done_file(output_filename)
    


# 使用示例
if __name__ == "__main__":
    # 配置参数
    input_data = "census1881" 
    
    # 调用函数
    process_data_files(input_data)