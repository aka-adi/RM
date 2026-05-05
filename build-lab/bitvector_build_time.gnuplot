############### Bitvector Build Time Comparison ###############

reset

set terminal eps size 4, 2.8 font 'Linux Libertine O,25'
set output 'bitvector_build_time_compare.eps'


set logscale x
set xrange [9.9:*]
set yrange [0.8:2.0]
set ytics 1,0.2,2 offset 0.2,0,0 font 'Linux Libertine O,20'

set xtics (10, 100, 1000, 10000, 100000, 1000000, 10000000) offset 0,0.6,0 font 'Linux Libertine O,20'
set mxtics 8
set format x '10^{%T}'
set format y
set ytics offset 0.2,0,0 font 'Linux Libertine O,20'

set xlabel offset 0,1.2,0 font 'Linux Libertine O,20' "位向量中1的个数" 
set ylabel offset 2.0,0,0  font 'Linux Libertine O,20' "加速比 (AVX512/普通)"

set key font "Linux Libertine O,15" reverse outside top center Left width 2.5
set key maxrows 1

set lmargin 5.9
set rmargin 1.6
set tmargin 1.4
set bmargin 1.8

plot \
    'bitvector_build_time.dat' using 1:4 title "加速比 (AVX512/普通)" lc rgb "purple" lw 8 ps 1.5 pt 7 with linespoints
