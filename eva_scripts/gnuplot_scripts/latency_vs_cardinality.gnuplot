############### Latency vs Cardinality: Left and Right Endpoints ###############

reset
set terminal postscript eps enhanced color size 7.2,3.2 font 'Linux Libertine O,22'
set output sprintf("%s/graphs/Figure_latency_vs_cardinality_endpoints.eps", directory_path)

F1 = sprintf("%s/distilled_data/eva_rabit_latency_10M_w_16_ratio_0.2_rangefix_0.15_GN_128_vary_cardinality.distilled", directory_path)
F2 = sprintf("%s/distilled_data/eva_rabit_latency_10M_w_16_ratio_0.2_rangefix_0.15_GN_64_vary_cardinality.distilled", directory_path)
F3 = sprintf("%s/distilled_data/eva_cubit-lk_latency_10M_w_16_ratio_0.2_rangefix_0.15_vary_cardinality.distilled", directory_path)
F4 = sprintf("%s/distilled_data/eva_ub_latency_10M_w_16_ratio_0.2_rangefix_0.15_vary_cardinality.distilled", directory_path)

stats F1 using 1 nooutput
F1_LAST = STATS_records - 1
stats F2 using 1 nooutput
F2_LAST = STATS_records - 1
stats F3 using 1 nooutput
F3_LAST = STATS_records - 1
stats F4 using 1 nooutput
F4_LAST = STATS_records - 1

set logscale y
set yrange [1:10000]
set ytics ("1" 1, "10" 10, "100" 100, "1000" 1000, "10000" 10000) font 'Linux Libertine O,16'
set mytics 10

set style fill solid 1.0 border -1
set boxwidth 0.22 absolute

set key font "Linux Libertine O,13" reverse outside top center Left width 1.2
set key maxrows 1

set multiplot layout 1,2 margins 0.08,0.98,0.18,0.86 spacing 0.08,0.02

#######################
# Left endpoint
#######################
set title "(a) Left endpoint" font 'Linux Libertine O,18'
set xrange [0.4:4.6]
set xtics offset 0,0.4,0 font 'Linux Libertine O,14' \
    ("IRE(C/128)" 1, "IRE(C/64)" 2, "CUBIT" 3, "UpBit" 4)

set ylabel offset 1.8,0,0 font 'Linux Libertine O,18' "Latency (ms, log scale)"
set xlabel offset 0,0.9,0 font 'Linux Libertine O,18' "Method"

plot \
    F1 every ::0::0 using (1-0.13):2 title "RQ" with boxes lc rgb "gray25" fs pattern 1, \
    F1 every ::0::0 using (1+0.13):($3>0?$3:1/0) title "UDI" with boxes lc rgb "gray70" fs pattern 2, \
    F2 every ::0::0 using (2-0.13):2 notitle with boxes lc rgb "gray25" fs pattern 1, \
    F2 every ::0::0 using (2+0.13):($3>0?$3:1/0) notitle with boxes lc rgb "gray70" fs pattern 2, \
    F3 every ::0::0 using (3-0.13):2 notitle with boxes lc rgb "gray25" fs pattern 1, \
    F3 every ::0::0 using (3+0.13):($3>0?$3:1/0) notitle with boxes lc rgb "gray70" fs pattern 2, \
    F4 every ::0::0 using (4-0.13):2 notitle with boxes lc rgb "gray25" fs pattern 1, \
    F4 every ::0::0 using (4+0.13):($3>0?$3:1/0) notitle with boxes lc rgb "gray70" fs pattern 2

#######################
# Right endpoint
#######################
set title "(b) Right endpoint" font 'Linux Libertine O,18'
unset ylabel
set xlabel offset 0,0.9,0 font 'Linux Libertine O,18' "Method"
set xtics offset 0,0.4,0 font 'Linux Libertine O,14' \
    ("IRE(C/128)" 1, "IRE(C/64)" 2, "CUBIT" 3, "UpBit" 4)
unset key

plot \
    F1 every ::F1_LAST::F1_LAST using (1-0.13):2 notitle with boxes lc rgb "gray25" fs pattern 1, \
    F1 every ::F1_LAST::F1_LAST using (1+0.13):($3>0?$3:1/0) notitle with boxes lc rgb "gray70" fs pattern 2, \
    F2 every ::F2_LAST::F2_LAST using (2-0.13):2 notitle with boxes lc rgb "gray25" fs pattern 1, \
    F2 every ::F2_LAST::F2_LAST using (2+0.13):($3>0?$3:1/0) notitle with boxes lc rgb "gray70" fs pattern 2, \
    F3 every ::F3_LAST::F3_LAST using (3-0.13):2 notitle with boxes lc rgb "gray25" fs pattern 1, \
    F3 every ::F3_LAST::F3_LAST using (3+0.13):($3>0?$3:1/0) notitle with boxes lc rgb "gray70" fs pattern 2, \
    F4 every ::F4_LAST::F4_LAST using (4-0.13):2 notitle with boxes lc rgb "gray25" fs pattern 1, \
    F4 every ::F4_LAST::F4_LAST using (4+0.13):($3>0?$3:1/0) notitle with boxes lc rgb "gray70" fs pattern 2

unset multiplot