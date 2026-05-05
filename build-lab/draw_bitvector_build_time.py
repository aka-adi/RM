import os
import sys

def draw_bitvector_build_time(directory_path):
    """
    调用 gnuplot 绘制 bitvector 构建时间对比图
    :param directory_path: gnuplot脚本和数据文件所在目录（如HiBI根目录）
    """
    gnuplot_script = os.path.join(directory_path, "bitvector_build_time.gnuplot")
    if not os.path.exists(gnuplot_script):
        print(f"[错误] 找不到 gnuplot 脚本: {gnuplot_script}")
        return
    # 切换到数据文件目录，保证数据文件路径正确
    cwd = os.getcwd()
    os.chdir(directory_path)
    gnu_command = f"gnuplot {gnuplot_script}"
    print(f"[信息] 正在执行: {gnu_command}")
    ret = os.system(gnu_command)
    os.chdir(cwd)
    if ret == 0:
        print("[成功] 已生成 bitvector_build_time_compare.eps")
    else:
        print("[失败] gnuplot 绘图失败，请检查数据文件和脚本。")

def convert_eps_to_png(directory_path, dpi=1200):
    # if ghostscript is not installed, return
    if os.system("which gs") != 0:
        print("ghostscript is not installed. Skip converting eps files to png files.")
        return    

    # 确保DPI大于1000
    if dpi <= 1000:
        print(f"WARNING: DPI setting ({dpi}) is too low, using 1200 DPI instead.")
        dpi = 1200
    
    eps_files = os.listdir(directory_path)
    print(f"Convert eps files in {directory_path} to png files with {dpi} DPI.")
    
    for eps_file in eps_files:
        if eps_file.endswith(".eps"):
            png_file = eps_file.replace(".eps", ".png")
            eps_file_path = os.path.join(directory_path, eps_file)
            png_file_path = os.path.join(directory_path, png_file)
            
            # 使用ghostscript将EPS转换为PNG
            gs_command = f"gs -dSAFER -dBATCH -dNOPAUSE -dEPSCrop -r{dpi} -sDEVICE=pngalpha -sOutputFile={png_file_path} {eps_file_path}"
            os.system(gs_command)
            print(f"Converted {eps_file} to {png_file} with {dpi} DPI")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法: python draw_bitvector_build_time.py <HiBI根目录路径>")
        sys.exit(1)
    directory_path = sys.argv[1]
    draw_bitvector_build_time(directory_path)
    convert_eps_to_png(directory_path)
