############### RQ vs Update Latency - Subplots ###############

reset

# 设置终端和输出文件 - 更宽的尺寸以容纳4个水平子图
set terminal eps size 12, 3.5 font 'Linux Libertine O,20'
set output sprintf("%s/graphs/Figure_latency_horizontal_subplots.eps", directory_path)

# 设置4个子图布局 (1行4列)
set multiplot layout 1,4
set tmargin 1.4
set bmargin 2.0
set lmargin 6.0
set rmargin 1.4

# 子图1: 基数256
set xrange [1:40]
set yrange [0:700]
set logscale x
set xtics offset 0.2,0.4,0 font 'Linux Libertine O,20' (1, 2, 4, 8, 16, 32)
set ytics offset 0.2,0,0 font 'Linux Libertine O,20' (0, 200, 400, 600)
set xlabel "区间长度" font 'Linux Libertine O,20' offset 0,1.0
set ylabel "延迟(毫秒)" font 'Linux Libertine O,20' offset 1.5,0
set key font "Linux Libertine O,15" inside top right right
plot sprintf("%s/distilled_data/eva_rabit_latency_10M_c_256_w_16_ratio_0.2.distilled", directory_path) u 1:3 t "RQ(C=256)" lc rgb "blue" lw 4 ps 1.5 pt 6 with linespoints,\
    sprintf("%s/distilled_data/eva_rabit_latency_10M_c_256_w_16_ratio_0.2.distilled", directory_path) u 1:4 t "Update(C=256)" lc rgb "red" lw 4 ps 1.5 pt 4 with linespoints axes x1y1

# 子图2: 基数512
set xrange [2:70]
set xtics offset 0.2,0.4,0 font 'Linux Libertine O,20' (2, 4, 8, 16, 32, 64)
set ytics offset 0.2,0,0 font 'Linux Libertine O,20' (0, 200, 400, 600)
unset xlabel
unset ylabel
plot sprintf("%s/distilled_data/eva_rabit_latency_10M_c_512_w_16_ratio_0.2.distilled", directory_path) u 1:3 t "RQ(C=512)" lc rgb "blue" lw 4 ps 1.5 pt 6 with linespoints,\
    sprintf("%s/distilled_data/eva_rabit_latency_10M_c_512_w_16_ratio_0.2.distilled", directory_path) u 1:4 t "Update(C=512)" lc rgb "red" lw 4 ps 1.5 pt 4 with linespoints

# 子图3: 基数1024
set xrange [4:140]
set xtics offset 0.2,0.4,0 font 'Linux Libertine O,20' (4, 8, 16, 32, 64, 128)
set ytics offset 0.2,0,0 font 'Linux Libertine O,20' (0, 200, 400, 600)
plot sprintf("%s/distilled_data/eva_rabit_latency_10M_c_1024_w_16_ratio_0.2.distilled", directory_path) u 1:3 t "RQ(C=1024)" lc rgb "blue" lw 4 ps 1.5 pt 6 with linespoints,\
    sprintf("%s/distilled_data/eva_rabit_latency_10M_c_1024_w_16_ratio_0.2.distilled", directory_path) u 1:4 t "Update(C=1024)" lc rgb "red" lw 4 ps 1.5 pt 4 with linespoints

# 子图4: 基数2048
set xrange [8:270]
set xtics offset 0.2,0.4,0 font 'Linux Libertine O,20' (8, 16, 32, 64, 128, 256)
set ytics offset 0.2,0,0 font 'Linux Libertine O,20' (0, 200, 400, 600)
unset xlabel
unset ylabel
plot sprintf("%s/distilled_data/eva_rabit_latency_10M_c_2048_w_16_ratio_0.2.distilled", directory_path) u 1:3 t "RQ(C=2048)" lc rgb "blue" lw 4 ps 1.5 pt 6 with linespoints,\
    sprintf("%s/distilled_data/eva_rabit_latency_10M_c_2048_w_16_ratio_0.2.distilled", directory_path) u 1:4 t "Update(C=2048)" lc rgb "red" lw 4 ps 1.5 pt 4 with linespoints

unset multiplot