############### 分段数量对位图大小的影响 ###############

reset

set terminal epscairo enhanced color size 3.8in,2.4in font "Linux Libertine O,10"
set output sprintf("%s/graphs/Figure_bitmap_size_vs_segment_size.eps", directory_path)

F_BITMAP = sprintf("%s/distilled_data/eva_rabit_bitmap_size_10M_c_1024_w_16_GL_16_vary_SEG.distilled", directory_path)

############################
# 自动设置 y 轴范围，使空间差异更明显
############################

stats F_BITMAP using 3 nooutput

Y_MIN = STATS_min
Y_MAX = STATS_max
Y_RANGE = Y_MAX - Y_MIN

Y_PAD = (Y_RANGE > 0 ? Y_RANGE * 0.35 : Y_MAX * 0.05)
Y_LOW = (Y_MIN - Y_PAD > 0 ? Y_MIN - Y_PAD : 0)
Y_HIGH = Y_MAX + Y_PAD

unset logscale x
unset logscale y

set xrange [0.55:7.45]
set yrange [Y_LOW:Y_HIGH]

############################
# 坐标轴与文字
############################

set xlabel offset 0,0.8,0 font "Linux Libertine O,10" "分段数量"
set ylabel offset 1.6,0,0 font "Linux Libertine O,10" "位图大小（MB）"

set xtics ("1" 1, "100" 2, "400" 3, "800" 4, "1600" 5, "3200" 6, "6400" 7) \
    offset 0,0.35,0 font "Linux Libertine O,10"

set ytics nomirror offset 0.2,0,0 font "Linux Libertine O,10"

set format y "%.0f"

set border linewidth 0.8
set tics out

set lmargin 6.2
set rmargin 1.0
set tmargin 1.0
set bmargin 2.2

############################
# 图例与网格
############################

unset key

set grid ytics lc rgb "#dddddd" lw 0.35

############################
# 柱状图样式
############################

BAR_COLOR = "#3139ae"

# 0.044 mm ≈ 0.125 pt
GRID_LW = 0.125

# 单指标柱状图，柱子稍窄，避免过粗
set boxwidth 0.38 absolute

# 只使用蓝色网状纹理，不使用实心填充
set style fill pattern border

############################
# 绘图
############################

plot \
    F_BITMAP using ($0 + 1):($3 > 0 ? $3 : 1/0) \
    with boxes lc rgb BAR_COLOR lw GRID_LW fs pattern 2 notitle