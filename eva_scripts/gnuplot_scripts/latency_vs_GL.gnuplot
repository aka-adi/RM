############### RQ vs Update Latency - Subplots ###############

reset

# 设置终端和输出文件 - 适合2x2布局的比例 (宽:高 ≈ 1.6:1)
set terminal eps size 10, 6.5 font 'Linux Libertine O,20'  # 调整为10x6.5更适合2x2布局
set output sprintf("%s/graphs/Figure_latency_2x2_subplots.eps", directory_path)

# 设置4个子图布局 (2行2列)
set multiplot layout 2,2
set tmargin 1.4
set bmargin 4.0  # 调整底部边距
set lmargin 4.0  # 调整左侧边距
set rmargin 3.0  # 调整右侧边距

# 子图1: 基数256
set xrange [1:40]
set yrange [0:700]
set logscale x
set xtics offset 0.2,0.4,0 font 'Linux Libertine O,20' (1, 2, 4, 8, 16, 32)
set ytics offset 0.2,0,0 font 'Linux Libertine O,20' (0, 200, 400, 600)
set xlabel "Interval length" font 'Linux Libertine O,20' offset 0,1.0
set ylabel "Latency(ms)" font 'Linux Libertine O,20' offset 1.5,0
set key font "Linux Libertine O,15" inside top right right
set label "a) Cardinality=256" at graph 0.5, -0.30 font 'Linux Libertine O,25' center  # 放在下方中央
plot sprintf("%s/distilled_data/eva_rabit_latency_10M_c_256_w_16_ratio_0.2.distilled", directory_path) u 1:3 t "RQ(C=256)" lc rgb "blue" lw 4 ps 1.5 pt 6 with linespoints,\
    sprintf("%s/distilled_data/eva_rabit_latency_10M_c_256_w_16_ratio_0.2.distilled", directory_path) u 1:4 t "Update(C=256)" lc rgb "red" lw 4 ps 1.5 pt 4 with linespoints axes x1y1

# 子图2: 基数512
set xrange [2:70]
set xtics offset 0.2,0.4,0 font 'Linux Libertine O,20' (2, 4, 8, 16, 32, 64)
set ytics offset 0.2,0,0 font 'Linux Libertine O,20' (0, 200, 400, 600)
unset label
set label "b) Cardinality=512" at graph 0.5, -0.30 font 'Linux Libertine O,25' center  # 放在下方中央
plot sprintf("%s/distilled_data/eva_rabit_latency_10M_c_512_w_16_ratio_0.2.distilled", directory_path) u 1:3 t "RQ(C=512)" lc rgb "blue" lw 4 ps 1.5 pt 6 with linespoints,\
    sprintf("%s/distilled_data/eva_rabit_latency_10M_c_512_w_16_ratio_0.2.distilled", directory_path) u 1:4 t "Update(C=512)" lc rgb "red" lw 4 ps 1.5 pt 4 with linespoints

# 子图3: 基数1024
set xrange [4:140]
set xtics offset 0.2,0.4,0 font 'Linux Libertine O,20' (4, 8, 16, 32, 64, 128)
set ytics offset 0.2,0,0 font 'Linux Libertine O,20' (0, 200, 400, 600)
unset label
set label "c) Cardinality=1024" at graph 0.5, -0.30 font 'Linux Libertine O,25' center  # 放在下方中央
plot sprintf("%s/distilled_data/eva_rabit_latency_10M_c_1024_w_16_ratio_0.2.distilled", directory_path) u 1:3 t "RQ(C=1024)" lc rgb "blue" lw 4 ps 1.5 pt 6 with linespoints,\
    sprintf("%s/distilled_data/eva_rabit_latency_10M_c_1024_w_16_ratio_0.2.distilled", directory_path) u 1:4 t "Update(C=1024)" lc rgb "red" lw 4 ps 1.5 pt 4 with linespoints

# 子图4: 基数2048
set xrange [8:270]
set xtics offset 0.2,0.4,0 font 'Linux Libertine O,20' (8, 16, 32, 64, 128, 256)
set ytics offset 0.2,0,0 font 'Linux Libertine O,20' (0, 200, 400, 600)
unset label
set label "d) Cardinality=2048" at graph 0.5, -0.30 font 'Linux Libertine O,25' center  # 放在下方中央
plot sprintf("%s/distilled_data/eva_rabit_latency_10M_c_2048_w_16_ratio_0.2.distilled", directory_path) u 1:3 t "RQ(C=2048)" lc rgb "blue" lw 4 ps 1.5 pt 6 with linespoints,\
    sprintf("%s/distilled_data/eva_rabit_latency_10M_c_2048_w_16_ratio_0.2.distilled", directory_path) u 1:4 t "Update(C=2048)" lc rgb "red" lw 4 ps 1.5 pt 4 with linespoints

unset multiplot