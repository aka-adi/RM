# plot_simd_bitmap.gp
# 作用：读取 SIMD 位向量构建实验结果，并生成三张图
#
# 调用方式：
# gnuplot -e "datafile='results/simd_bitmap_result.csv'; outdir='graphs'; font_name='SimSun'" plot_simd_bitmap.gp

reset

if (!exists("datafile")) datafile = "results/simd_bitmap_result.csv"
if (!exists("outdir")) outdir = "graphs"
if (!exists("font_name")) font_name = "SimSun"

set encoding utf8
set datafile separator ","

set border lw 1.2
set grid ytics
set key outside top center horizontal
set style data linespoints

font_png = font_name . ",18"

set terminal pngcairo enhanced size 1400,900 font font_png

# CSV 列含义：
# 1  实验名称
# 2  数据分布
# 3  位向量长度_bits
# 4  位向量字数
# 5  置位数量
# 6  每字置位数
# 7  普通C耗时_ns
# 8  AVX512耗时_ns
# 9  加速比
# 10 普通C吞吐量_Mops每秒
# 11 AVX512吞吐量_Mops每秒
# 12 正确性

# ============================================================
# 图 1：不同置位数量下的 SIMD 加速比
# ============================================================

unset logscale
set logscale x 10

set output outdir . "/simd_density_speedup.png"

set title "不同置位数量下的 SIMD 位向量构建加速比"
set xlabel "位向量中 1 的个数"
set ylabel "加速比"

set xrange [10:1200000]
set yrange [0:*]

set xtics ("16" 16, "64" 64, "512" 512, "1K" 1000, "10K" 10000, "100K" 100000, "1M" 1000000)

set arrow 1 from graph 0, first 1 to graph 1, first 1 nohead dt 2 lw 1

plot datafile every ::1 using \
    (stringcolumn(1) eq "密度实验" && stringcolumn(2) eq "低冲突" ? $5 : 1/0):9 \
    with linespoints lw 2 pt 7 ps 1 title "低冲突", \
     datafile every ::1 using \
    (stringcolumn(1) eq "密度实验" && stringcolumn(2) eq "均匀随机" ? $5 : 1/0):9 \
    with linespoints lw 2 pt 5 ps 1 title "均匀随机", \
     datafile every ::1 using \
    (stringcolumn(1) eq "密度实验" && stringcolumn(2) eq "集中冲突_32位每字" ? $5 : 1/0):9 \
    with linespoints lw 2 pt 9 ps 1 title "高冲突"

unset arrow 1

# ============================================================
# 图 2：不同段大小下的构建吞吐量
# ============================================================

unset logscale
set logscale x 2

set output outdir . "/simd_segment_throughput.png"

set title "不同段大小下的位向量构建吞吐量"
set xlabel "段大小 / bits"
set ylabel "构建吞吐量 / Mops·s^{-1}"

set xrange [3000:40000000]
set yrange [0:*]

set xtics ("4K" 4096, "16K" 16384, "64K" 65536, "256K" 262144, \
           "1M" 1048576, "4M" 4194304, "16M" 16777216, "32M" 32768000)

plot datafile every ::1 using \
    (stringcolumn(1) eq "段大小实验" && stringcolumn(2) eq "低冲突" ? $3 : 1/0):10 \
    with linespoints lw 2 pt 7 ps 1 title "普通C-低冲突", \
     datafile every ::1 using \
    (stringcolumn(1) eq "段大小实验" && stringcolumn(2) eq "低冲突" ? $3 : 1/0):11 \
    with linespoints lw 2 pt 5 ps 1 title "AVX512-低冲突"

# ============================================================
# 图 3：不同冲突强度下的 SIMD 加速比
# ============================================================

unset logscale
set logscale x 2

set output outdir . "/simd_conflict_speedup.png"

set title "不同 word 内冲突强度下的 SIMD 加速比"
set xlabel "每个 32-bit word 内的置位数量"
set ylabel "加速比"

set xrange [0.8:40]
set yrange [0:*]

set xtics ("1" 1, "2" 2, "4" 4, "8" 8, "16" 16, "32" 32)

set arrow 1 from graph 0, first 1 to graph 1, first 1 nohead dt 2 lw 1

plot datafile every ::1 using \
    (stringcolumn(1) eq "冲突实验" ? $6 : 1/0):9 \
    with linespoints lw 2 pt 7 ps 1 title "集中冲突分布"

unset arrow 1
unset output