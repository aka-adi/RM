############### HiBI-EE 与 CUBIT-EE 延迟对比 ###############

reset

set terminal epscairo enhanced color size 5.4in,2.6in font "Linux Libertine O,10"
set output sprintf("%s/graphs/Figure_rabit_ee_vs_cubit_latency.eps", directory_path)

F_RANGE_5_UDI_40 = sprintf("%s/distilled_data/eva_rabit_ee_vs_cubit_latency_10M_c_1024_w_16_ratio_0.4_range_0.05_GL_64.distilled", directory_path)
F_RANGE_1_UDI_20 = sprintf("%s/distilled_data/eva_rabit_ee_vs_cubit_latency_10M_c_1024_w_16_ratio_0.2_range_0.01_GL_64.distilled", directory_path)

unset logscale y
unset logscale y2

set xrange [0.4:2.6]

set xtics ("HiBI-EE" 1, "CUBIT-EE" 2) offset 0,0.4,0 font "Linux Libertine O,10"

set ytics nomirror offset 0.2,0,0 font "Linux Libertine O,10"
set y2tics nomirror offset -0.2,0,0 font "Linux Libertine O,10"

set format y "%.0f"
set format y2 "%.0f"

# 0.044 mm ≈ 0.125 pt
GRID_LW = 0.125

set style fill pattern border
set boxwidth 0.24 absolute

set multiplot layout 1,2 margins 0.10,0.94,0.18,0.86 spacing 0.13,0.02

############################
# 通用柱状图位置
############################

RQ_X(i) = (i + 1 - 0.15)
UDI_X(i) = (i + 1 + 0.15)

############################
# （a）查询范围 = 5%，更新率 = 40%
############################
set title "（a）查询范围 = 5%，更新率 = 40%" font "Linux Libertine O,10"

set yrange [0:*]
set y2range [0:*]

set xlabel offset 0,0.8,0 font "Linux Libertine O,10" "方法"
set ylabel offset 1.8,0,0 font "Linux Libertine O,10" "查询延迟（ms）"
unset y2label

set key font "Linux Libertine O,8" reverse top left Left width 1.0

plot \
    F_RANGE_5_UDI_40 using (RQ_X($0)):($2 > 0 ? $2 : 1/0) axes x1y1 title "查询延迟" with boxes lc rgb "#9dde67" lw GRID_LW fs pattern 1, \
    ''               using (UDI_X($0)):($3 > 0 ? $3 : 1/0) axes x1y2 title "更新延迟" with boxes lc rgb "#3139ae" lw GRID_LW fs pattern 2


############################
# （b）查询范围 = 1%，更新率 = 20%
############################
set title "（b）查询范围 = 1%，更新率 = 20%" font "Linux Libertine O,10"

set yrange [0:*]
set y2range [0:*]

set xlabel offset 0,0.8,0 font "Linux Libertine O,10" "方法"
unset ylabel
set y2label offset -1.8,0,0 font "Linux Libertine O,10" "更新延迟（ms）"
unset key

plot \
    F_RANGE_1_UDI_20 using (RQ_X($0)):($2 > 0 ? $2 : 1/0) axes x1y1 notitle with boxes lc rgb "#9dde67" lw GRID_LW fs pattern 1, \
    ''               using (UDI_X($0)):($3 > 0 ? $3 : 1/0) axes x1y2 notitle with boxes lc rgb "#3139ae" lw GRID_LW fs pattern 2

unset multiplot