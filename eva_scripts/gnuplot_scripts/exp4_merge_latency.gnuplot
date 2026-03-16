############### Latency Analysis for Exp4 Merge ###############

reset

set terminal eps size 4, 2.8 font 'Linux Libertine O,25'
set output sprintf("%s/graphs/Figure_exp4_merge_latency.eps", directory_path)

set xrange [-0.5:2.5]
set yrange [250:350]

set xtics offset 0,0.6,0 font 'Linux Libertine O,20'
set ytics offset 0.2,0,0 font 'Linux Libertine O,20'

set xlabel offset 0,1.2,0 font 'Linux Libertine O,20' "merge threads"
set ylabel offset 2.0,0,0  font 'Linux Libertine O,20' "number of logs"

set key font "Linux Libertine O,15" reverse outside top center Left width 2.5
set key maxrows 1

set lmargin 5.9
set rmargin 1.6
set tmargin 1.4
set bmargin 1.8

set style data histograms
set style fill solid 0.7 border -1
set boxwidth 0.4 relative

plot sprintf("%s/distilled_data/exp4_merge_latency_merged.distilled", directory_path) using 2:xtic(1) title "Insert" with boxes lc rgb "black"
