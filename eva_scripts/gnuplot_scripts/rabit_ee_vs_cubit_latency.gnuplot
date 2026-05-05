reset

set terminal postscript eps enhanced color size 4,2.8 font 'Linux Libertine O,25'
set output sprintf("%s/graphs/Figure_rabit_ee_vs_cubit_latency.eps", directory_path)

set style data histograms
set style histogram clustered gap 1
set boxwidth 0.8 relative
set style fill solid 1.0 border -1

set xtics offset 0,0.6,0 font 'Linux Libertine O,20'
set ytics offset 0.2,0,0 font 'Linux Libertine O,20'
set format y "%.1t{/Symbol \264}10^{%T}"

set xlabel offset 0,1.2,0 font 'Linux Libertine O,20' "方案"
set ylabel offset 2.0,0,0 font 'Linux Libertine O,20' "查询延迟 (ms)"

set key font "Linux Libertine O,15" reverse outside top center Left width 2.5
set key maxrows 1

set lmargin 5.9
set rmargin 1.6
set tmargin 1.4
set bmargin 1.8

# 只画三组方案
plot sprintf("%s/distilled_data/rabit_ee_vs_cubit_latency.distilled", directory_path) \
    using 5:xtic(1) title "平均延迟" with histograms lc rgb "gray60", \
    '' using 6 title "P99延迟" with histograms lc rgb "black" fs pattern 4