############### Latency vs Query Range ###############

### Query latency ###

reset

set terminal eps size 4, 2.5 font 'Linux Libertine O,25'
set output sprintf("%s/graphs/Figure_query_latency_vs_query_range.eps", directory_path)

set xrange [0:50]
set yrange [0:2600]

set xtics offset 0,0.2,0 font ',25'
set ytics offset 0.5,0,0 font ',25'

set xlabel offset 0,0.6,0 font 'Linux Libertine O,29' "Number of worker threads"
set ylabel offset -1.1,0,0 "Query latency (ms)" font 'Linux Libertine O,29'

set key font ",25" reverse Left top left

set lmargin 5.5
set rmargin 0.2
set tmargin 0.2
set bmargin 1.8

plot sprintf("%s/distilled_data/eva_rabit_latency_100M_c_1000_w_16_ratio_0.8.distilled", directory_path) using 1:2 title "CUBIT" lc rgb "blue" lw 8 ps 1.5 pt 6 with linespoints


####################################
### Range Query latency ###

reset

set terminal eps size 4, 2.5 font 'Linux Libertine O,25'
set output sprintf("%s/graphs/Figure_RQ_latency_vs_query_range.eps", directory_path)

set xrange [0:50]
set yrange [0:2600]

set xtics offset 0,0.2,0 font ',25'
set ytics offset 0.5,0,0 font ',25'

set xlabel offset 0,0.6,0 font 'Linux Libertine O,29' "Number of worker threads"
set ylabel offset -1.1,0,0 "Range Query latency (ms)" font 'Linux Libertine O,29'

set key font ",25" reverse Left top left

set lmargin 5.5
set rmargin 0.2
set tmargin 0.2
set bmargin 1.8

plot sprintf("%s/distilled_data/eva_rabit_latency_100M_c_1000_w_16_ratio_0.8.distilled", directory_path) using 1:3 title "CUBIT" lc rgb "blue" lw 8 ps 1.5 pt 6 with linespoints


####################################
### Update latency ###

reset

set terminal eps size 4, 2.5 font 'Linux Libertine O,25'
set output sprintf("%s/graphs/Figure_Update_latency_vs_query_range.eps", directory_path)

set xrange [0:50]
set yrange [0:5]

set xtics offset 0,0.2,0 font ',25'
set ytics offset 0.5,0,0 font ',25'

set xlabel offset 0,0.6,0 font 'Linux Libertine O,29' "Number of worker threads"
set ylabel offset -1.1,0,0 "Update latency (ms)" font 'Linux Libertine O,29'

set key font ",25" reverse Left top left

set lmargin 5.5
set rmargin 0.2
set tmargin 0.2
set bmargin 1.8

plot sprintf("%s/distilled_data/eva_rabit_latency_100M_c_1000_w_16_ratio_0.8.distilled", directory_path) using 1:4 title "CUBIT" lc rgb "blue" lw 8 ps 1.5 pt 6 with linespoints


####################################
### Delete ###

reset

set terminal eps size 4, 2.5 font 'Linux Libertine O,25'
set output sprintf("%s/graphs/Figure_delete_latency_vs_query_range.eps", directory_path)

set xrange [0:50]
set yrange [0:5]

set xtics offset 0,0.2,0 font ',25'
set ytics offset 0.5,0,0 font ',25'

set xlabel offset 0,0.6,0 font 'Linux Libertine O,29' "Number of worker threads"
set ylabel offset -1.1,0,0 "Delete latency (ms)" font 'Linux Libertine O,29'

set key font ",25" reverse Left top left

set lmargin 5.5
set rmargin 0.2
set tmargin 0.2
set bmargin 1.8

plot sprintf("%s/distilled_data/eva_rabit_latency_100M_c_1000_w_16_ratio_0.8.distilled", directory_path) using 1:5 title "CUBIT" lc rgb "blue" lw 8 ps 1.5 pt 6 with linespoints


####################################
### Insert latency ###

reset

set terminal eps size 4, 2.5 font 'Linux Libertine O,25'
set output sprintf("%s/graphs/Figure_RQ_latency_vs_query_range.eps", directory_path)

set xrange [0:50]
set yrange [0:0.05]

set xtics offset 0,0.2,0 font ',25'
set ytics offset 0.5,0,0 font ',25'

set xlabel offset 0,0.6,0 font 'Linux Libertine O,29' "Number of worker threads"
set ylabel offset -1.1,0,0 "Insert latency (ms)" font 'Linux Libertine O,29'

set key font ",25" reverse Left top left

set lmargin 5.5
set rmargin 0.2
set tmargin 0.2
set bmargin 1.8

plot sprintf("%s/distilled_data/eva_rabit_latency_100M_c_1000_w_16_ratio_0.8.distilled", directory_path) using 1:6 title "CUBIT" lc rgb "blue" lw 8 ps 1.5 pt 6 with linespoints


# plot  "../dat/figure_nbub-lk_latency_core.dat" every 5::0::30 title "CUBIT" lc rgb "blue" lw 8 ps 1.5 pt 6 with linespoints,\
#       "../dat/figure_ub_latency_core.dat" every 5::0::30 title "UpBit^{+}" lc rgb "sea-green" lw 8 ps 1.5 pt 10 dt 9 with linespoints,\
#       "../dat/figure_naive_latency_core.dat" every 5::0::30 title "In-place^{+}" lc rgb "black" lw 8 ps 1.5 pt 12 dt 5 with linespoints,\
#       "../dat/figure_ucb_latency_core.dat" every 5::0::30 title "UCB^{+}" lc rgb "brown" lw 8 ps 1.5 pt 8 dt "-" with linespoints