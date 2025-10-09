############### Throughput vs Query Range ###############

reset

set terminal eps size 4, 2.8 font 'Linux Libertine O,25'
set output sprintf("%s/graphs/Figure_throughput_vs_UDI.eps", directory_path)

set xrange [0:50]
set yrange [1:1000]


set xtics offset 0,0.6,0 font 'Linux Libertine O,25' (0, 10, 20, 30, 40, 50)
set ytics offset 0.2,0,0 font 'Linux Libertine O,25' (1, 10, "10^2" 100, "10^3" 1000)

set xlabel offset 0,1.2,0 font 'Linux Libertine O,25' "UDI ratio (% of queries)" 
set ylabel offset 1.0,0,0  font 'Linux Libertine O,25' "Throughput (op/s)"

set key font "Linux Libertine O,25" reverse outside top center Left width 2.5
set key maxrows 1

set lmargin 5.9
set rmargin 1.6
set tmargin 1.4
set bmargin 1.8

set logscale y

plot sprintf("%s/distilled_data/eva_rabit_throughput_100M_c_1000_w_16_GL_50_vary_UDI.distilled", directory_path) title "GE-50" lc rgb "blue" lw 8 ps 1.5 pt 6 with linespoints,\
     sprintf("%s/distilled_data/eva_rabit_throughput_100M_c_1000_w_16_GL_100_vary_UDI.distilled", directory_path) title "GE-100" lc rgb "dark-blue" lw 8 ps 1.5 pt 4 with linespoints,\
     sprintf("%s/distilled_data/eva_cubit-lk_throughput_100M_c_1000_w_16_vary_UDI.distilled", directory_path) notitle lc rgb "brown" lw 8 ps 1.5 pt 8 dt "-" with linespoints,\
     sprintf("%s/distilled_data/eva_ub_throughput_100M_c_1000_w_16_vary_UDI.distilled", directory_path) notitle lc rgb "sea-green" lw 8 ps 1.5 pt 10 dt 9 with linespoints
          # sprintf("%s/distilled_data/eva_rabit_throughput_100M_c_1000_w_16_GL_200_vary_UDI.distilled", directory_path) title "GE-200" lc rgb "light-blue" lw 8 ps 1.5 pt 6 with linespoints,\