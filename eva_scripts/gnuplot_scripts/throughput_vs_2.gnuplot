############### Throughput - Combined Subplots ###############

reset

# 设置终端和输出文件 - 适合2个水平子图的比例
set terminal eps size 9, 3.5 font 'Linux Libertine O,25'
set output sprintf("%s/graphs/Figure_throughput_combined_subplots.eps", directory_path)

# 设置2个子图布局 (1行2列)
set multiplot layout 1,2
set tmargin 2.0  # 增加顶部边距以容纳共享图例
set bmargin 4.0
set lmargin 5.9
set rmargin 1.6

# 子图1: Throughput vs Update Rate (左侧)
set xrange [0:45]
set yrange [5:1000]

set xtics offset 0,0.6,0 font 'Linux Libertine O,20' (0, 10, 20, 30, 40)
set ytics offset 0.2,0,0 font 'Linux Libertine O,20' (10, "10^2" 100, "10^3" 1000)

set xlabel offset 0,1.2,0 font 'Linux Libertine O,20' "Update rate（%）" 
set ylabel offset 2.0,0,0 font 'Linux Libertine O,20' "Throughput (op/s)"

# 添加子图标题
set label "a) Throughput vs Update Rate" at graph 0.5, -0.33 font 'Linux Libertine O,20' center

# 设置均匀分布的图例
set key font "Linux Libertine O,15" reverse outside top center Left width 3.5
set key maxrows 1

set logscale y

plot sprintf("%s/distilled_data/eva_rabit_throughput_10M_c_1000_w_16_GL_10_vary_UDI.distilled", directory_path) title "IRE(C/128)" lc rgb "blue" lw 8 ps 1.5 pt 6 with linespoints,\
     sprintf("%s/distilled_data/eva_rabit_throughput_10M_c_1000_w_16_GL_20_vary_UDI.distilled", directory_path) title "IRE(C/64)" lc rgb "dark-blue" lw 8 ps 1.5 pt 4 with linespoints,\
     sprintf("%s/distilled_data/eva_cubit-lk_throughput_10M_c_1000_w_16_vary_UDI.distilled", directory_path) notitle lc rgb "brown" lw 8 ps 1.5 pt 8 dt "-" with linespoints,\
     sprintf("%s/distilled_data/eva_ub_throughput_10M_c_1000_w_16_vary_UDI.distilled", directory_path) notitle  lc rgb "sea-green" lw 8 ps 1.5 pt 10 dt 9 with linespoints

unset label

# 子图2: Throughput vs Query Range (右侧)
set xrange [5:50]
set yrange [5:1000]

set xtics offset 0,0.5,0 font 'Linux Libertine O,20' (5, 15, 25, 35, 45)
set ytics offset 0.2,0,0 font 'Linux Libertine O,20' (10, "10^2" 100, "10^3" 1000)

set xlabel offset 0,1.3,0 font 'Linux Libertine O,20' "Query range (% of cardinality)" 
unset ylabel  # 移除右侧子图的ylabel以避免重叠

# 添加子图标题
set label "b) Throughput vs Query Range" at graph 0.5, -0.33 font 'Linux Libertine O,20' center

set logscale y

plot sprintf("%s/distilled_data/eva_rabit_throughput_10M_c_1000_w_16_ratio_0.2_GL_10_vary_QL.distilled", directory_path) notitle lc rgb "blue" lw 8 ps 1.5 pt 6 with linespoints,\
     sprintf("%s/distilled_data/eva_rabit_throughput_10M_c_1000_w_16_ratio_0.2_GL_20_vary_QL.distilled", directory_path) notitle lc rgb "dark-blue" lw 8 ps 1.5 pt 4 with linespoints,\
     sprintf("%s/distilled_data/eva_cubit-lk_throughput_10M_c_1000_w_16_ratio_0.2_vary_QL.distilled", directory_path) title "EE" lc rgb "brown" lw 8 ps 1.5 pt 8 dt "-" with linespoints,\
     sprintf("%s/distilled_data/eva_ub_throughput_10M_c_1000_w_16_ratio_0.2_vary_QL.distilled", directory_path) title "RE" lc rgb "sea-green" lw 8 ps 1.5 pt 10 dt 9 with linespoints

unset multiplot