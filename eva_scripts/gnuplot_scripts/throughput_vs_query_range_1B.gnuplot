############### Throughput vs Query Range ###############

reset
set terminal eps size 4, 2.8 font 'Linux Libertine O,25'
set output sprintf("%s/graphs/Figure_throughput_vs_query_range.eps", directory_path)

set xrange [5:45]
set yrange [0.1:100]

set xtics offset 0,0.5,0 font 'Linux Libertine O,25' (5, 15, 25, 35, 45)
set ytics offset 0.3,0,0 font 'Linux Libertine O,25' ("10^{-1}" 0.1, 1, "10" 10, "10^2" 100)

set xlabel offset 0,1.3,0 font 'Linux Libertine O,25' "Query range (% of cardinality)"
set ylabel offset 1.8,0,0  font 'Linux Libertine O,25' "Throughput (op/s)"

set key font "Linux Libertine O,25" reverse outside top center Left width 2.5
set key maxrows 1

set lmargin 5.9
set rmargin 1.6
set tmargin 1.4
set bmargin 1.8

set logscale y

plot sprintf("%s/distilled_data/eva_rabit_throughput_1000M_c_1000_w_16_ratio_0.2_GL_50_vary_QL.distilled", directory_path) notitle lc rgb "blue" lw 8 ps 1.5 pt 6 with linespoints,\
     sprintf("%s/distilled_data/eva_rabit_throughput_1000M_c_1000_w_16_ratio_0.2_GL_100_vary_QL.distilled", directory_path) notitle lc rgb "dark-blue" lw 8 ps 1.5 pt 4 with linespoints,\
     sprintf("%s/distilled_data/eva_cubit-lk_throughput_1000M_c_1000_w_16_ratio_0.2_vary_QL.distilled", directory_path) title "EE" lc rgb "brown" lw 8 ps 1.5 pt 8 dt "-" with linespoints,\
     sprintf("%s/distilled_data/eva_ub_throughput_1000M_c_1000_w_16_ratio_0.2_vary_QL.distilled", directory_path) title "RE" lc rgb "sea-green" lw 8 ps 1.5 pt 10 dt 9 with linespoints

