############### Throughput vs Cardinality ###############

reset

set terminal eps size 4, 2.8 font 'Linux Libertine O,25'
set output sprintf("%s/graphs/Figure_throughput_vs_cardinality.eps", directory_path)

set xrange [100:100000]
set yrange [0:500]

set xtics offset 0.2,0.4,0 font 'Linux Libertine O,25' ("10^2" 100, "10^3" 1000, "10^4" 10000, "10^5" 100000)
set ytics offset 0.2,0,0 font 'Linux Libertine O,25' ("10^{-1}" 0.1, 1, 10,"10^{2}" 100, "10^{3}" 1000)

set xlabel offset 0,1.2,0 font 'Linux Libertine O,25' "Cardinality" 
set ylabel offset 1.8,0,0  font 'Linux Libertine O,25' "Throughput (op/s)"

set key font "Linux Libertine O,25" reverse outside top center Left width 2.5 
set key maxrows 1

set lmargin 5.9
set rmargin 1.6
set tmargin 1.4
set bmargin 1.8

set logscale x
set logscale y

plot sprintf("%s/distilled_data/eva_rabit_dc-throughput_100M_w_16_ratio_0.1_rangefix_0.15_GL_50_vary_cardinality.distilled", directory_path) title "GE-(C/20)" lc rgb "blue" lw 8 ps 1.5 pt 6 with linespoints,\
     sprintf("%s/distilled_data/eva_rabit_dc-throughput_100M_w_16_ratio_0.1_rangefix_0.15_GL_100_vary_cardinality.distilled", directory_path) title "GE-(C/10)" lc rgb "dark-blue" lw 8 ps 1.5 pt 4 with linespoints,\
     sprintf("%s/distilled_data/eva_cubit-lk_dc-throughput_100M_w_16_ratio_0.1_rangefix_0.15_vary_cardinality.distilled", directory_path) notitle lc rgb "brown" lw 8 ps 1.5 pt 8 dt "-" with linespoints,\
     sprintf("%s/distilled_data/eva_ub_dc-throughput_100M_w_16_ratio_0.1_rangefix_0.15_vary_cardinality.distilled", directory_path) notitle lc rgb "sea-green" lw 8 ps 1.5 pt 10 dt 9 with linespoints