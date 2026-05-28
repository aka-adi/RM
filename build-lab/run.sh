#!/usr/bin/env bash

SRC_FILE=${SRC_FILE:-main.c}
BITMAP_SRC=${BITMAP_SRC:-bitmap.c}
BIN_FILE=${BIN_FILE:-simd_bitmap_lab}

RESULT_DIR=${RESULT_DIR:-results}
GRAPH_DIR=${GRAPH_DIR:-graphs}
CSV_FILE=${CSV_FILE:-${RESULT_DIR}/simd_bitmap_result.csv}

PLOT_SCRIPT=${PLOT_SCRIPT:-plot_simd_bitmap.gp}

FONT_NAME=${FONT_NAME:-SimSun}

mkdir -p "${RESULT_DIR}"
mkdir -p "${GRAPH_DIR}"

echo "==== 编译 SIMD 位向量构建实验程序 ===="

gcc -O3 \
    -std=c11 \
    -Wall \
    -Wextra \
    -march=native \
    -mavx512f \
    -mavx512cd \
    -o "${BIN_FILE}" \
    "${SRC_FILE}" \
    "${BITMAP_SRC}"

echo "==== 运行实验程序 ===="

"./${BIN_FILE}" "${CSV_FILE}"

echo "==== 调用 Gnuplot 生成图片 ===="

gnuplot -e "datafile='${CSV_FILE}'; outdir='${GRAPH_DIR}'; font_name='${FONT_NAME}'" "${PLOT_SCRIPT}"

echo "==== 完成 ===="
echo "实验结果文件: ${CSV_FILE}"
echo "图1: ${GRAPH_DIR}/simd_density_speedup.png"
echo "图2: ${GRAPH_DIR}/simd_segment_throughput.png"
echo "图3: ${GRAPH_DIR}/simd_conflict_speedup.png"