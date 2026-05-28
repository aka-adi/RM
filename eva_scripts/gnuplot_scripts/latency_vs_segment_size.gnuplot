############### 分段数量对延迟的影响 ###############

reset

set terminal epscairo enhanced color size 7.2in,5.2in font "Linux Libertine O,10"
set output sprintf("%s/graphs/Figure_latency_vs_segment_size.eps", directory_path)

F_UDI_LOW  = sprintf("%s/distilled_data/eva_rabit_latency_10M_c_1024_w_16_ratio_0.1_rangefix_0.15_GL_16_vary_SEG.distilled", directory_path)
F_UDI_HIGH = sprintf("%s/distilled_data/eva_rabit_latency_10M_c_1024_w_16_ratio_0.4_rangefix_0.15_GL_16_vary_SEG.distilled", directory_path)

F_RANGE_LOW  = sprintf("%s/distilled_data/eva_rabit_latency_10M_c_1024_w_16_ratiofix_0.2_range_0.05_GL_16_vary_SEG.distilled", directory_path)
F_RANGE_HIGH = sprintf("%s/distilled_data/eva_rabit_latency_10M_c_1024_w_16_ratiofix_0.2_range_0.45_GL_16_vary_SEG.distilled", directory_path)

unset logscale y
unset logscale y2

set xrange [0.4:7.6]
set xtics ("1" 1, "100" 2, "400" 3, "800" 4, "1600" 5, "3200" 6, "6400" 7) \
    offset 0,0.4,0 font "Linux Libertine O,10"

set ytics nomirror offset 0.2,0,0 font "Linux Libertine O,10"
set y2tics nomirror offset -0.2,0,0 font "Linux Libertine O,10"

set format y "%.0f"
set format y2 "%.0f"

# 0.044 mm ≈ 0.125 pt
GRID_LW = 0.125

# 只使用纹理填充，不使用实心颜色填充
set style fill pattern border
set boxwidth 0.24 absolute

set multiplot layout 2,2 margins 0.08,0.96,0.10,0.90 spacing 0.13,0.12

############################
# 通用柱状图位置
############################

RQ_X(i) = (i + 1 - 0.15)
UDI_X(i) = (i + 1 + 0.15)

############################
# （a）低更新率
############################
set title "（a）更新率 = 10%" font "Linux Libertine O,10"

set yrange [0:*]
set y2range [0:*]

set xlabel offset 0,0.8,0 font "Linux Libertine O,10" "分段数量"
set ylabel offset 1.9,0,0 font "Linux Libertine O,10" "查询延迟（ms）"
unset y2label

set key font "Linux Libertine O,8" reverse top left Left width 1.0

plot \
    F_UDI_LOW using (RQ_X($0)):($2 > 0 ? $2 : 1/0) axes x1y1 title "查询延迟" with boxes lc rgb "#9dde67" lw GRID_LW fs pattern 1, \
    ''        using (UDI_X($0)):($3 > 0 ? $3 : 1/0) axes x1y2 title "更新延迟" with boxes lc rgb "#3139ae" lw GRID_LW fs pattern 2


############################
# （b）高更新率
############################
set title "（b）更新率 = 40%" font "Linux Libertine O,10"

set yrange [0:*]
set y2range [0:*]

set xlabel offset 0,0.8,0 font "Linux Libertine O,10" "分段数量"
unset ylabel
set y2label offset -1.9,0,0 font "Linux Libertine O,10" "更新延迟（ms）"
unset key

plot \
    F_UDI_HIGH using (RQ_X($0)):($2 > 0 ? $2 : 1/0) axes x1y1 notitle with boxes lc rgb "#9dde67" lw GRID_LW fs pattern 1, \
    ''         using (UDI_X($0)):($3 > 0 ? $3 : 1/0) axes x1y2 notitle with boxes lc rgb "#3139ae" lw GRID_LW fs pattern 2


############################
# （c）小查询范围
############################
set title "（c）查询范围 = 5%" font "Linux Libertine O,10"

set yrange [0:*]
set y2range [0:*]

set xlabel offset 0,0.8,0 font "Linux Libertine O,10" "分段数量"
set ylabel offset 1.9,0,0 font "Linux Libertine O,10" "查询延迟（ms）"
unset y2label
unset key

plot \
    F_RANGE_LOW using (RQ_X($0)):($2 > 0 ? $2 : 1/0) axes x1y1 notitle with boxes lc rgb "#9dde67" lw GRID_LW fs pattern 1, \
    ''          using (UDI_X($0)):($3 > 0 ? $3 : 1/0) axes x1y2 notitle with boxes lc rgb "#3139ae" lw GRID_LW fs pattern 2


############################
# （d）大查询范围
############################
set title "（d）查询范围 = 45%" font "Linux Libertine O,10"

set yrange [0:*]
set y2range [0:*]

set xlabel offset 0,0.8,0 font "Linux Libertine O,10" "分段数量"
unset ylabel
set y2label offset -1.9,0,0 font "Linux Libertine O,10" "更新延迟（ms）"
unset key

plot \
    F_RANGE_HIGH using (RQ_X($0)):($2 > 0 ? $2 : 1/0) axes x1y1 notitle with boxes lc rgb "#9dde67" lw GRID_LW fs pattern 1, \
    ''           using (UDI_X($0)):($3 > 0 ? $3 : 1/0) axes x1y2 notitle with boxes lc rgb "#3139ae" lw GRID_LW fs pattern 2

unset multiplot