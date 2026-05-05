#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <stdbool.h>
#include "bitmap.h"

#define BIT_COUNT (31 * 5 * 991)  // 1048576 个位索引
#define BITMAP_WORDS 1024000  // 足够大的 bitmap
#define MIN_DIFF 32  // 元素最小差值

// 交换两个uint32_t值（内联函数提升效率）
static inline void swap_uint32(uint32_t* a, uint32_t* b) {
    uint32_t temp = *a;
    *a = *b;
    *b = temp;
}

// 插入排序（用于小数组优化）
static void insertion_sort_uint32(uint32_t* arr, size_t low, size_t high) {
    for (size_t i = low + 1; i <= high; i++) {
        uint32_t key = arr[i];
        size_t j = i - 1;
        
        // 无符号整数比较，无需考虑负数
        while (j >= low && arr[j] > key) {
            arr[j + 1] = arr[j];
            j--;
        }
        arr[j + 1] = key;
    }
}

// 三数取中法选择基准值（优化基准选择，避免最坏情况）
static size_t choose_pivot(uint32_t* arr, size_t low, size_t high) {
    size_t mid = low + (high - low) / 2;
    
    // 排序low、mid、high三个位置的值，取mid作为基准
    if (arr[low] > arr[mid]) {
        swap_uint32(&arr[low], &arr[mid]);
    }
    if (arr[low] > arr[high]) {
        swap_uint32(&arr[low], &arr[high]);
    }
    if (arr[mid] > arr[high]) {
        swap_uint32(&arr[mid], &arr[high]);
    }
    
    // 将基准值移到high-1位置（减少比较次数）
    swap_uint32(&arr[mid], &arr[high - 1]);
    return high - 1;
}

// 分区函数（核心逻辑）
static size_t partition_uint32(uint32_t* arr, size_t low, size_t high) {
    // 选择基准值
    size_t pivot_idx = choose_pivot(arr, low, high);
    uint32_t pivot = arr[pivot_idx];
    
    // 双指针分区
    size_t i = low;
    size_t j = high - 1;
    
    while (1) {
        // 左指针右移，找大于基准值的元素
        while (arr[++i] < pivot);
        // 右指针左移，找小于基准值的元素
        while (arr[--j] > pivot);
        
        if (i >= j) {
            break;
        }
        // 交换不符合分区规则的元素
        swap_uint32(&arr[i], &arr[j]);
    }
    
    // 将基准值放回正确位置
    swap_uint32(&arr[i], &arr[pivot_idx]);
    return i;
}

// 快速排序递归函数（对外暴露的核心接口）
void quicksort_uint32(uint32_t* arr, size_t low, size_t high) {
    // 小数组（长度≤16）使用插入排序，提升性能
    const size_t INSERTION_THRESHOLD = 16;
    while (high - low > INSERTION_THRESHOLD) {
        size_t pivot_pos = partition_uint32(arr, low, high);
        
        // 尾递归优化：优先处理较小的子数组，减少递归深度
        if (pivot_pos - low < high - pivot_pos) {
            quicksort_uint32(arr, low, pivot_pos - 1);
            low = pivot_pos + 1;
        } else {
            quicksort_uint32(arr, pivot_pos + 1, high);
            high = pivot_pos - 1;
        }
    }
    
    // 对剩余的小数组执行插入排序
    if (low < high) {
        insertion_sort_uint32(arr, low, high);
    }
}

// 简化接口：直接传入数组和长度（更易用）
void quicksort_uint32_array(uint32_t* arr, size_t len) {
    if (arr == NULL || len <= 1) {
        return;
    }
    quicksort_uint32(arr, 0, len - 1);
}


// 验证结果是否一样
bool check_equal(const uint32_t* a, const uint32_t* b, int n) {
    int diff = 0;
    int total_ones = 0;
    for (int i = 0; i < n; ++i) {
        if (a[i] != b[i]) {
            printf("第 %d 个 word 不同: %08X vs %08X\n", i, a[i], b[i]);
            diff++;
        }
        total_ones += __builtin_popcount(b[i]);
        }
    return diff == 0;
}

uint32_t* allocate_aligned_array_c11(size_t size) {
    // 参数1：对齐大小（必须是2的幂），参数2：总字节数（必须是对齐大小的整数倍）
    uint32_t* ptr = (uint32_t*)aligned_alloc(64, ((size * sizeof(uint32_t) + 63) / 64) * 64);
    
    if (ptr == NULL) {
        perror("aligned_alloc failed");
        return NULL;
    }
    return ptr;
}

// 校验数组是否为升序有序
static bool is_sorted_asc(int *arr, int len) {
    if (len <= 1) return true;
    for (int i = 1; i < len; i++) {
        if (arr[i] < arr[i-1]) {
            return false;
        }
    }
    return true;
}

uint32_t* filter_and_append_invalid(uint32_t *arr, int arr_len, int *valid_count) {
    // 1. 校验输入合法性
    if (arr == NULL || valid_count == NULL || arr_len <= 0) {
        printf("错误：输入参数非法！\n");
        return NULL;
    }
    if (!is_sorted_asc(arr, arr_len)) {
        printf("错误：输入数组不是升序有序数组！\n");
        return NULL;
    }

    // 2. 分配内存（与原数组等长，存放所有元素）
    uint32_t *result = (uint32_t *)malloc(sizeof(uint32_t) * arr_len);
    if (result == NULL) {
        printf("错误：内存分配失败！\n");
        return NULL;
    }

    *valid_count = 0;
    int valid_found = 0;
    int last_valid = -MIN_DIFF - 1; // 保证第一个元素一定能被选中
    int start = 0;
    int *valid_indices = (int *)malloc(sizeof(int) * arr_len); // 记录有效元素下标
    if (valid_indices == NULL) {
        printf("错误：内存分配失败！\n");
        free(result);
        return NULL;
    }

    while (start < arr_len) {
        valid_found = 0;
        last_valid = arr[start] - MIN_DIFF - 1;
        for (int i = start; i < arr_len; ++i) {
            if (arr[i] - last_valid >= MIN_DIFF - 1) {
                valid_indices[*valid_count + valid_found++] = i;
                last_valid = arr[i];
                if (valid_found == MIN_DIFF) {
                    break;
                }
            }
        }
        if (valid_found < MIN_DIFF) {
            break;
        }
        // 拷贝本轮找到的MIN_DIFF个有效元素
        for (int k = 0; k < valid_found; ++k) {
            result[*valid_count] = arr[valid_indices[*valid_count]];
            (*valid_count)++;
        }
        // 下轮从第一个无效元素（即本轮最后一个有效元素的下一个）开始
        start = valid_indices[*valid_count - 1] + 1;
    }

    // 追加剩余无效元素
    int invalid_index = *valid_count;
    bool *is_valid = (bool *)calloc(arr_len, sizeof(bool));
    if (is_valid == NULL) {
        printf("错误：内存分配失败！\n");
        free(result);
        free(valid_indices);
        return NULL;
    }
    for (int i = 0; i < *valid_count; ++i) {
        is_valid[valid_indices[i]] = true;
    }
    for (int i = 0; i < arr_len; ++i) {
        if (!is_valid[i]) {
            result[invalid_index++] = arr[i];
        }
    }
    free(is_valid);
    free(valid_indices);
    return result;
}

int lab_onlyone() {
    // 实验参数
    const int repeat = 15; // 每组运行次数
    const int test_sizes[] = {16, 32, 64, 256, 512, 1000, 5000, 10000, 100000, 300000, 500000, 700000, 900000, 1000000};
    const int num_sizes = sizeof(test_sizes) / sizeof(test_sizes[0]);
    FILE *fp = fopen("bitvector_build_time.dat", "w");
    if (!fp) {
        perror("fopen output file");
        return 1;
    }
    fprintf(fp, "#count normal_time(ns) avx512_time(ns) speedup correctness\n");
    for (int s = 0; s < num_sizes; ++s) {
        int cur_count = test_sizes[s];
        double normal_times[repeat], avx512_times[repeat];
        bool all_ok = true;
        for (int r = 0; r < repeat; ++r) {
            uint32_t* indices = allocate_aligned_array_c11(cur_count);
            uint32_t* dst_normal = allocate_aligned_array_c11(BITMAP_WORDS * sizeof(uint32_t));
            uint32_t* dst_avx512 = allocate_aligned_array_c11(BITMAP_WORDS * sizeof(uint32_t));
            uint32_t* used = allocate_aligned_array_c11(BITMAP_WORDS * sizeof(uint32_t));
            memset(used, 0, BITMAP_WORDS * sizeof(uint32_t));
            // 每个word只置位一个，word和bit都随机且不重复
            // 1. 生成所有word编号
            uint32_t* word_pool = (uint32_t*)malloc(BITMAP_WORDS * sizeof(uint32_t));
            for (uint32_t i = 0; i < BITMAP_WORDS; ++i) word_pool[i] = i;
            // 2. 洗牌，随机选cur_count个word
            for (uint32_t i = 0; i < (uint32_t)cur_count; ++i) {
                uint32_t j = i + rand() % (BITMAP_WORDS - i);
                uint32_t tmp = word_pool[i];
                word_pool[i] = word_pool[j];
                word_pool[j] = tmp;
            }
            for (uint32_t i = 0; i < (uint32_t)cur_count; ++i) {
                uint32_t word = word_pool[i];
                uint32_t bit = rand() % 32;
                indices[i] = word * 32 + bit;
                used[word] |= (1U << bit);
            }
            free(word_pool);
            memset(dst_normal, 0, BITMAP_WORDS * sizeof(uint32_t));
            memset(dst_avx512, 0, BITMAP_WORDS * sizeof(uint32_t));
            quicksort_uint32_array(indices, cur_count);
            struct timespec t1, t2, t3, t4;
            clock_gettime(CLOCK_MONOTONIC, &t1);
            bitmap_set_bits_normal(dst_normal, indices, cur_count);
            clock_gettime(CLOCK_MONOTONIC, &t2);
            double time_normal = (double)(t2.tv_sec - t1.tv_sec) * 1000000000.0 + (double)(t2.tv_nsec - t1.tv_nsec);
            clock_gettime(CLOCK_MONOTONIC, &t3);
            bitmap_set_bits_avx512(dst_avx512, indices, cur_count);
            clock_gettime(CLOCK_MONOTONIC, &t4);
            double time_avx512 = (double)(t4.tv_sec - t3.tv_sec) * 1000000000.0 + (double)(t4.tv_nsec - t3.tv_nsec);
            bool ok = check_equal(dst_normal, dst_avx512, BITMAP_WORDS);
            all_ok = all_ok & ok;
            normal_times[r] = time_normal;
            avx512_times[r] = time_avx512;
            free(indices);
            free(dst_normal);
            free(dst_avx512);
            free(used);
        }
        // 去掉最大最小值
        double min_n = normal_times[0], max_n = normal_times[0], sum_n = 0;
        double min_a = avx512_times[0], max_a = avx512_times[0], sum_a = 0;
        for (int r = 0; r < repeat; ++r) {
            if (normal_times[r] < min_n) min_n = normal_times[r];
            if (normal_times[r] > max_n) max_n = normal_times[r];
            if (avx512_times[r] < min_a) min_a = avx512_times[r];
            if (avx512_times[r] > max_a) max_a = avx512_times[r];
            sum_n += normal_times[r];
            sum_a += avx512_times[r];
        }
        double avg_n = (sum_n - min_n - max_n) / (repeat - 2);
        double avg_a = (sum_a - min_a - max_a) / (repeat - 2);
        fprintf(fp, "%d %.3f %.3f %.2f %s\n",
            cur_count, avg_n, avg_a, avg_n/avg_a, all_ok ? "YES" : "NO");
    }
    fclose(fp);
    return 0;
}

int lab_multiword() {
    // 实验参数
    const int repeat = 15;
    const int test_sizes[] = {10, 100, 1000, 10000, 100000, 1000000, 10000000};
    const int num_sizes = sizeof(test_sizes) / sizeof(test_sizes[0]);
    FILE *fp = fopen("bitvector_build_time.dat", "w");
    if (!fp) {
        perror("fopen output file");
        return 1;
    }
    fprintf(fp, "#count normal_time(ns) avx512_time(ns) speedup correctness\n");
    for (int s = 0; s < num_sizes; ++s) {
        int cur_count = test_sizes[s];
        double normal_times[repeat], avx512_times[repeat];
        bool all_ok = true;
        for (int r = 0; r < repeat; ++r) {
            uint32_t* indices = allocate_aligned_array_c11(cur_count);
            uint32_t* dst_normal = allocate_aligned_array_c11(BITMAP_WORDS * sizeof(uint32_t));
            uint32_t* dst_avx512 = allocate_aligned_array_c11(BITMAP_WORDS * sizeof(uint32_t));
            uint32_t* used = allocate_aligned_array_c11(BITMAP_WORDS * sizeof(uint32_t));
            memset(used, 0, BITMAP_WORDS * sizeof(uint32_t));
            // 每个word可置多位，bit位随机且不重复
            int filled = 0;
            while (filled < cur_count) {
                uint32_t word = rand() % BITMAP_WORDS;
                uint32_t bit = rand() % 32;
                uint32_t idx = word * 32 + bit;
                // 保证不重复
                if ((used[word] & (1U << bit)) == 0) {
                    indices[filled++] = idx;
                    used[word] |= (1U << bit);
                }
            }
            memset(dst_normal, 0, BITMAP_WORDS * sizeof(uint32_t));
            memset(dst_avx512, 0, BITMAP_WORDS * sizeof(uint32_t));
            // quicksort_uint32_array(indices, cur_count);
            struct timespec t1, t2, t3, t4;
            clock_gettime(CLOCK_MONOTONIC, &t1);
            bitmap_set_bits_normal(dst_normal, indices, cur_count);
            clock_gettime(CLOCK_MONOTONIC, &t2);
            double time_normal = (double)(t2.tv_sec - t1.tv_sec) * 1000000000.0 + (double)(t2.tv_nsec - t1.tv_nsec);
            clock_gettime(CLOCK_MONOTONIC, &t3);
            bitmap_set_bits_avx512(dst_avx512, indices, cur_count);
            clock_gettime(CLOCK_MONOTONIC, &t4);
            double time_avx512 = (double)(t4.tv_sec - t3.tv_sec) * 1000000000.0 + (double)(t4.tv_nsec - t3.tv_nsec);
            bool ok = check_equal(dst_normal, dst_avx512, BITMAP_WORDS);
            all_ok = all_ok & ok;
            normal_times[r] = time_normal;
            avx512_times[r] = time_avx512;
            free(indices);
            free(dst_normal);
            free(dst_avx512);
            free(used);
        }
        // 去掉最大最小值
        double min_n = normal_times[0], max_n = normal_times[0], sum_n = 0;
        double min_a = avx512_times[0], max_a = avx512_times[0], sum_a = 0;
        for (int r = 0; r < repeat; ++r) {
            if (normal_times[r] < min_n) min_n = normal_times[r];
            if (normal_times[r] > max_n) max_n = normal_times[r];
            if (avx512_times[r] < min_a) min_a = avx512_times[r];
            if (avx512_times[r] > max_a) max_a = avx512_times[r];
            sum_n += normal_times[r];
            sum_a += avx512_times[r];
        }
        double avg_n = (sum_n - min_n - max_n) / (repeat - 2);
        double avg_a = (sum_a - min_a - max_a) / (repeat - 2);
        fprintf(fp, "%d %.3f %.3f %.2f %s\n",
            cur_count, avg_n, avg_a, avg_n/avg_a, all_ok == true ? "YES" : "NO");
    }
    fclose(fp);
    return 0;
}

int main() {

    // lab_onlyone();
    lab_multiword();
    return 0;
}
