############### Throughput vs Cardinality ###############

reset

set terminal eps size 4, 2.8 font 'Linux Libertine O,25'
set output sprintf("%s/graphs/Figure_throughput_vs_cardinality.eps", directory_path)

set xrange [256:2700]
set yrange [10:300]

set xtics offset 0.2,0.4,0 font 'Linux Libertine O,20' ("2^8" 256, "2^9" 512, "2^{10}" 1024, "2^{11}" 2048)
set ytics offset 0.2,0,0 font 'Linux Libertine O,20' (10, 50, 100, 200)

set xlabel offset 0,1.2,0 font 'Linux Libertine O,20' "Cardinality" 
set ylabel offset 2.8,0,0  font 'Linux Libertine O,20' "Throughput (op/s)"

set key font "Linux Libertine O,15" reverse inside right box
set key maxrows 4
#set key offset 0,0.4  # 将图例向上偏移1.0个单位
set key samplen 2.0  # 减小图例中线条样本的长度
set key spacing 0.8  # 减小图例项之间的间距
set key width 0.2     # 固定图例宽度

set lmargin 5.9
set rmargin 1.6
set tmargin 1.4
set bmargin 1.8

set logscale x
#set logscale y

plot sprintf("%s/distilled_data/eva_rabit_throughput_10M_w_16_ratio_0.2_rangefix_0.15_GN_128_vary_cardinality.distilled", directory_path) title "IRE(C/128)" lc rgb "blue" lw 8 ps 1.2 pt 6 with linespoints,\
     sprintf("%s/distilled_data/eva_rabit_throughput_10M_w_16_ratio_0.2_rangefix_0.15_GN_64_vary_cardinality.distilled", directory_path) title "IRE(C/64)" lc rgb "dark-blue" lw 8 ps 1.2 pt 4 with linespoints,\
     sprintf("%s/distilled_data/eva_cubit-lk_throughput_10M_w_16_ratio_0.2_rangefix_0.15_vary_cardinality.distilled", directory_path) title "EE" lc rgb "brown" lw 8 ps 1.2 pt 8 dt "-" with linespoints,\
     sprintf("%s/distilled_data/eva_ub_throughput_10M_w_16_ratio_0.2_rangefix_0.15_vary_cardinality.distilled", directory_path) title "RE" lc rgb "sea-green" lw 8 ps 1.2 pt 10 dt 9 with linespoints