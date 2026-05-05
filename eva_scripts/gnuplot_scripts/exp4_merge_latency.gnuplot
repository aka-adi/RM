reset

set terminal postscript eps enhanced color size 4, 2.8 font 'Linux Libertine O,25'
set output sprintf("%s/graphs/Figure_exp4_merge_latency.eps", directory_path)

set yrange [10:150]

set xtics offset 0,0.6,0 font 'Linux Libertine O,20'
set ytics offset 0.2,0,0 font 'Linux Libertine O,20'

set xlabel offset 0,1.2,0 font 'Linux Libertine O,20' "合并阈值"
set ylabel offset 2.0,0,0 font 'Linux Libertine O,20' "延迟(ms)"

set key font "Linux Libertine O,15" reverse outside top center Left width 2.5
set key maxrows 1

set lmargin 5.9
set rmargin 1.6
set tmargin 1.4
set bmargin 1.8

set style data histograms
set style histogram clustered gap 1
set boxwidth 0.8 relative

# 样式1：灰色实心
set style line 1 lc rgb "gray60" lw 1

# 样式2：黑色，用于黑白条纹
set style line 2 lc rgb "black" lw 1

plot sprintf("%s/distilled_data/exp4_merge_latency_merged.distilled", directory_path) \
    using 2:xtic(1) title "查询延迟" with histograms ls 1 fs solid 1.0 border lc rgb "black", \
    '' using 3 title "更新延迟" with histograms ls 2 fs pattern 4 border lc rgb "black"