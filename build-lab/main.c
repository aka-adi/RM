#define _POSIX_C_SOURCE 200809L

#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <stdbool.h>
#include <errno.h>
#include "bitmap.h"

#define BITS_PER_WORD 32U
#define ALIGN_BYTES 64U

#define DEFAULT_BITMAP_WORDS 1024000U
#define DEFAULT_BITMAP_BITS  (DEFAULT_BITMAP_WORDS * BITS_PER_WORD)

#define REPEAT 15
#define WARMUP 5
#define CHECK_ROUNDS 3

#define SORT_INDICES_BEFORE_BUILD 1
#define DEFAULT_OUTPUT_FILE "results/simd_bitmap_result.csv"

typedef enum {
    DIST_LOW_CONFLICT = 0,
    DIST_UNIFORM_RANDOM = 1,
    DIST_CLUSTERED = 2
} dist_kind_t;

typedef enum {
    METHOD_NORMAL = 0,
    METHOD_AVX512 = 1
} method_kind_t;

static const char* experiment_name_cn(const char* experiment) {
    if (strcmp(experiment, "density_sweep") == 0) {
        return "密度实验";
    }
    if (strcmp(experiment, "segment_size_sweep") == 0) {
        return "段大小实验";
    }
    if (strcmp(experiment, "conflict_sweep") == 0) {
        return "冲突实验";
    }
    return "未知实验";
}

static const char* dist_id_name(dist_kind_t dist) {
    switch (dist) {
        case DIST_LOW_CONFLICT:
            return "low_conflict";
        case DIST_UNIFORM_RANDOM:
            return "uniform_random";
        case DIST_CLUSTERED:
            return "clustered";
        default:
            return "unknown";
    }
}

static const char* dist_name_cn(dist_kind_t dist, int bits_per_word) {
    static char buf[64];

    switch (dist) {
        case DIST_LOW_CONFLICT:
            return "低冲突";
        case DIST_UNIFORM_RANDOM:
            return "均匀随机";
        case DIST_CLUSTERED:
            snprintf(buf, sizeof(buf), "集中冲突_%d位每字", bits_per_word);
            return buf;
        default:
            return "未知分布";
    }
}

static inline uint64_t now_ns(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000000000ULL + (uint64_t)ts.tv_nsec;
}

static inline size_t bitmap_words_for_bits(uint32_t bits) {
    return (bits + BITS_PER_WORD - 1) / BITS_PER_WORD;
}

static inline uint32_t min_u32(uint32_t a, uint32_t b) {
    return a < b ? a : b;
}

static inline uint32_t max_u32(uint32_t a, uint32_t b) {
    return a > b ? a : b;
}

/*
 * 可复现实验随机数。
 * 关键点：每轮实验都会重置 rng_state，从而保证普通 C 和 AVX512 使用完全相同的输入。
 */
static uint64_t rng_state = 88172645463325252ULL;

static inline void set_rng_seed(uint64_t seed) {
    rng_state = seed;
}

static inline uint64_t splitmix64_next(void) {
    uint64_t z = (rng_state += 0x9E3779B97F4A7C15ULL);
    z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ULL;
    z = (z ^ (z >> 27)) * 0x94D049BB133111EBULL;
    return z ^ (z >> 31);
}

static inline uint32_t rand_u32(void) {
    return (uint32_t)splitmix64_next();
}

static inline uint32_t rand_bounded(uint32_t bound) {
    if (bound == 0) {
        return 0;
    }

    uint32_t threshold = (uint32_t)(-bound % bound);

    while (1) {
        uint32_t r = rand_u32();
        if (r >= threshold) {
            return r % bound;
        }
    }
}

/*
 * 生成每一轮使用的固定随机种子。
 * 同一个 case 中，round 相同，则普通 C 和 AVX512 得到完全相同的 indices。
 */
static uint64_t make_case_seed(const char* experiment,
                               uint32_t bitmap_bits,
                               uint32_t ones_count,
                               dist_kind_t dist,
                               int bits_per_word,
                               int round) {
    uint64_t h = 1469598103934665603ULL;

    for (const char* p = experiment; *p; ++p) {
        h ^= (unsigned char)(*p);
        h *= 1099511628211ULL;
    }

    h ^= (uint64_t)bitmap_bits;
    h *= 1099511628211ULL;

    h ^= (uint64_t)ones_count;
    h *= 1099511628211ULL;

    h ^= (uint64_t)dist;
    h *= 1099511628211ULL;

    h ^= (uint64_t)bits_per_word;
    h *= 1099511628211ULL;

    h ^= (uint64_t)round;
    h *= 1099511628211ULL;

    return h;
}

static uint32_t* allocate_aligned_u32(size_t n_words) {
    if (n_words == 0) {
        n_words = 1;
    }

    size_t bytes = n_words * sizeof(uint32_t);
    size_t aligned_bytes = (bytes + ALIGN_BYTES - 1) / ALIGN_BYTES * ALIGN_BYTES;

    void* ptr = NULL;
    int ret = posix_memalign(&ptr, ALIGN_BYTES, aligned_bytes);

    if (ret != 0 || ptr == NULL) {
        fprintf(stderr, "内存分配失败: %s\n", strerror(ret));
        return NULL;
    }

    return (uint32_t*)ptr;
}

static int cmp_u32(const void* a, const void* b) {
    uint32_t x = *(const uint32_t*)a;
    uint32_t y = *(const uint32_t*)b;
    return (x > y) - (x < y);
}

static int cmp_double(const void* a, const void* b) {
    double x = *(const double*)a;
    double y = *(const double*)b;
    return (x > y) - (x < y);
}

static double median_double(const double* arr, int n) {
    if (n <= 0) {
        return 0.0;
    }

    double* tmp = (double*)malloc(sizeof(double) * n);
    if (tmp == NULL) {
        return 0.0;
    }

    memcpy(tmp, arr, sizeof(double) * n);
    qsort(tmp, n, sizeof(double), cmp_double);

    double result;
    if ((n & 1) == 1) {
        result = tmp[n / 2];
    } else {
        result = (tmp[n / 2 - 1] + tmp[n / 2]) / 2.0;
    }

    free(tmp);
    return result;
}

static bool check_equal_limited(const uint32_t* a, const uint32_t* b, size_t n_words) {
    int diff_printed = 0;
    int diff_count = 0;

    for (size_t i = 0; i < n_words; ++i) {
        if (a[i] != b[i]) {
            if (diff_printed < 8) {
                printf("结果不一致：word=%zu, 普通C=%08X, AVX512=%08X\n",
                       i, a[i], b[i]);
                diff_printed++;
            }
            diff_count++;
        }
    }

    if (diff_count > diff_printed) {
        printf("还有 %d 个 word 不一致\n", diff_count - diff_printed);
    }

    return diff_count == 0;
}

static bool generate_low_conflict_indices(uint32_t* indices,
                                          uint32_t count,
                                          uint32_t bitmap_bits) {
    size_t bitmap_words = bitmap_words_for_bits(bitmap_bits);

    if ((size_t)count > bitmap_words) {
        return false;
    }

    uint32_t* word_pool = (uint32_t*)malloc(bitmap_words * sizeof(uint32_t));
    if (word_pool == NULL) {
        return false;
    }

    for (uint32_t i = 0; i < (uint32_t)bitmap_words; ++i) {
        word_pool[i] = i;
    }

    for (uint32_t i = 0; i < count; ++i) {
        uint32_t j = i + rand_bounded((uint32_t)bitmap_words - i);
        uint32_t tmp = word_pool[i];
        word_pool[i] = word_pool[j];
        word_pool[j] = tmp;
    }

    for (uint32_t i = 0; i < count; ++i) {
        uint32_t word = word_pool[i];
        uint32_t bit = rand_bounded(BITS_PER_WORD);
        uint32_t idx = word * BITS_PER_WORD + bit;

        if (idx >= bitmap_bits) {
            idx = bitmap_bits - 1;
        }

        indices[i] = idx;
    }

    free(word_pool);
    return true;
}

static bool generate_uniform_random_indices(uint32_t* indices,
                                            uint32_t count,
                                            uint32_t bitmap_bits) {
    size_t bitmap_words = bitmap_words_for_bits(bitmap_bits);

    if (count > bitmap_bits) {
        return false;
    }

    uint32_t* used = allocate_aligned_u32(bitmap_words);
    if (used == NULL) {
        return false;
    }

    memset(used, 0, bitmap_words * sizeof(uint32_t));

    uint32_t filled = 0;

    while (filled < count) {
        uint32_t idx = rand_bounded(bitmap_bits);
        uint32_t word = idx >> 5;
        uint32_t bit = idx & 31U;
        uint32_t mask = 1U << bit;

        if ((used[word] & mask) == 0) {
            used[word] |= mask;
            indices[filled++] = idx;
        }
    }

    free(used);
    return true;
}

static bool generate_clustered_indices(uint32_t* indices,
                                       uint32_t count,
                                       uint32_t bitmap_bits,
                                       int bits_per_word) {
    size_t bitmap_words = bitmap_words_for_bits(bitmap_bits);

    if (count > bitmap_bits) {
        return false;
    }

    bits_per_word = (int)min_u32(max_u32((uint32_t)bits_per_word, 1U), 32U);

    uint32_t active_words =
        (count + (uint32_t)bits_per_word - 1) / (uint32_t)bits_per_word;

    if ((size_t)active_words > bitmap_words) {
        return false;
    }

    uint32_t* word_pool = (uint32_t*)malloc(bitmap_words * sizeof(uint32_t));
    if (word_pool == NULL) {
        return false;
    }

    for (uint32_t i = 0; i < (uint32_t)bitmap_words; ++i) {
        word_pool[i] = i;
    }

    for (uint32_t i = 0; i < active_words; ++i) {
        uint32_t j = i + rand_bounded((uint32_t)bitmap_words - i);
        uint32_t tmp = word_pool[i];
        word_pool[i] = word_pool[j];
        word_pool[j] = tmp;
    }

    uint32_t filled = 0;

    for (uint32_t w = 0; w < active_words && filled < count; ++w) {
        uint32_t word = word_pool[w];

        uint32_t bit_pool[32];
        for (uint32_t b = 0; b < BITS_PER_WORD; ++b) {
            bit_pool[b] = b;
        }

        for (uint32_t b = 0; b < (uint32_t)bits_per_word; ++b) {
            uint32_t j = b + rand_bounded(BITS_PER_WORD - b);
            uint32_t tmp = bit_pool[b];
            bit_pool[b] = bit_pool[j];
            bit_pool[j] = tmp;
        }

        for (int k = 0; k < bits_per_word && filled < count; ++k) {
            uint32_t idx = word * BITS_PER_WORD + bit_pool[k];

            if (idx < bitmap_bits) {
                indices[filled++] = idx;
            }
        }
    }

    free(word_pool);
    return filled == count;
}

static bool generate_indices(uint32_t* indices,
                             uint32_t count,
                             uint32_t bitmap_bits,
                             dist_kind_t dist,
                             int bits_per_word) {
    bool ok = false;

    switch (dist) {
        case DIST_LOW_CONFLICT:
            ok = generate_low_conflict_indices(indices, count, bitmap_bits);
            break;
        case DIST_UNIFORM_RANDOM:
            ok = generate_uniform_random_indices(indices, count, bitmap_bits);
            break;
        case DIST_CLUSTERED:
            ok = generate_clustered_indices(indices, count, bitmap_bits, bits_per_word);
            break;
        default:
            ok = false;
            break;
    }

#if SORT_INDICES_BEFORE_BUILD
    if (ok && count > 1) {
        qsort(indices, count, sizeof(uint32_t), cmp_u32);
    }
#endif

    return ok;
}

static void run_method_once(method_kind_t method,
                            uint32_t* dst,
                            uint32_t* indices,
                            int count) {
    if (method == METHOD_NORMAL) {
        bitmap_set_bits_normal(dst, indices, count);
    } else {
        bitmap_set_bits_avx512(dst, indices, count);
    }
}

static double time_method_once(method_kind_t method,
                               uint32_t* dst,
                               uint32_t* indices,
                               int count) {
    uint64_t t1 = now_ns();

    run_method_once(method, dst, indices, count);

    uint64_t t2 = now_ns();
    return (double)(t2 - t1);
}

/*
 * 单独测试某一种方法。
 *
 * 注意：
 * 1. warm-up 不计入结果；
 * 2. 每轮都重新生成输入；
 * 3. 计时不包含输入生成、排序、memset；
 * 4. 普通 C 和 AVX512 会分别调用该函数，但使用相同 seed 生成同一轮输入。
 */
static bool measure_method(const char* experiment,
                           uint32_t bitmap_bits,
                           uint32_t ones_count,
                           dist_kind_t dist,
                           int bits_per_word,
                           method_kind_t method,
                           double* times_out) {
    size_t bitmap_words = bitmap_words_for_bits(bitmap_bits);

    uint32_t* indices = allocate_aligned_u32(ones_count);
    uint32_t* dst = allocate_aligned_u32(bitmap_words);

    if (indices == NULL || dst == NULL) {
        free(indices);
        free(dst);
        return false;
    }

    /*
     * warm-up 阶段：预热指令路径、缓存和分支行为。
     * warm-up 使用负编号构造种子，避免与正式测量轮次重复。
     */
    for (int w = 0; w < WARMUP; ++w) {
        uint64_t seed = make_case_seed(experiment,
                                       bitmap_bits,
                                       ones_count,
                                       dist,
                                       bits_per_word,
                                       -1000 - w);

        set_rng_seed(seed);

        bool gen_ok = generate_indices(indices,
                                       ones_count,
                                       bitmap_bits,
                                       dist,
                                       bits_per_word);

        if (!gen_ok) {
            free(indices);
            free(dst);
            return false;
        }

        memset(dst, 0, bitmap_words * sizeof(uint32_t));

        run_method_once(method, dst, indices, (int)ones_count);
    }

    /*
     * 正式测量阶段。
     * 每轮重新生成输入，但普通 C 和 AVX512 在相同 round 下使用相同 seed。
     */
    for (int r = 0; r < REPEAT; ++r) {
        uint64_t seed = make_case_seed(experiment,
                                       bitmap_bits,
                                       ones_count,
                                       dist,
                                       bits_per_word,
                                       r);

        set_rng_seed(seed);

        bool gen_ok = generate_indices(indices,
                                       ones_count,
                                       bitmap_bits,
                                       dist,
                                       bits_per_word);

        if (!gen_ok) {
            free(indices);
            free(dst);
            return false;
        }

        memset(dst, 0, bitmap_words * sizeof(uint32_t));

        times_out[r] = time_method_once(method, dst, indices, (int)ones_count);
    }

    free(indices);
    free(dst);

    return true;
}

/*
 * 正确性检查单独进行，不混入计时流程。
 * 为避免正确性检查过度拖慢实验，这里只检查 CHECK_ROUNDS 轮。
 */
static bool check_correctness_for_case(const char* experiment,
                                       uint32_t bitmap_bits,
                                       uint32_t ones_count,
                                       dist_kind_t dist,
                                       int bits_per_word) {
    size_t bitmap_words = bitmap_words_for_bits(bitmap_bits);

    uint32_t* indices = allocate_aligned_u32(ones_count);
    uint32_t* dst_normal = allocate_aligned_u32(bitmap_words);
    uint32_t* dst_avx512 = allocate_aligned_u32(bitmap_words);

    if (indices == NULL || dst_normal == NULL || dst_avx512 == NULL) {
        free(indices);
        free(dst_normal);
        free(dst_avx512);
        return false;
    }

    bool all_ok = true;

    for (int r = 0; r < CHECK_ROUNDS; ++r) {
        uint64_t seed = make_case_seed(experiment,
                                       bitmap_bits,
                                       ones_count,
                                       dist,
                                       bits_per_word,
                                       r);

        set_rng_seed(seed);

        bool gen_ok = generate_indices(indices,
                                       ones_count,
                                       bitmap_bits,
                                       dist,
                                       bits_per_word);

        if (!gen_ok) {
            all_ok = false;
            break;
        }

        memset(dst_normal, 0, bitmap_words * sizeof(uint32_t));
        memset(dst_avx512, 0, bitmap_words * sizeof(uint32_t));

        bitmap_set_bits_normal(dst_normal, indices, (int)ones_count);
        bitmap_set_bits_avx512(dst_avx512, indices, (int)ones_count);

        bool ok = check_equal_limited(dst_normal, dst_avx512, bitmap_words);
        all_ok = all_ok && ok;
    }

    free(indices);
    free(dst_normal);
    free(dst_avx512);

    return all_ok;
}

static void print_csv_header(FILE* fp) {
    fprintf(fp,
            "实验ID,实验名称,分布ID,数据分布,位向量长度_bits,位向量字数,"
            "置位数量,每字置位数,warmup次数,重复次数,"
            "普通C中位耗时_ns,AVX512中位耗时_ns,加速比,"
            "普通C吞吐量_Mops每秒,AVX512吞吐量_Mops每秒,正确性\n");
}

static void run_case(FILE* fp,
                     const char* experiment,
                     uint32_t bitmap_bits,
                     uint32_t ones_count,
                     dist_kind_t dist,
                     int bits_per_word) {
    size_t bitmap_words = bitmap_words_for_bits(bitmap_bits);

    if (ones_count == 0 || ones_count > bitmap_bits) {
        return;
    }

    double normal_times[REPEAT];
    double avx512_times[REPEAT];

    bool normal_ok = measure_method(experiment,
                                    bitmap_bits,
                                    ones_count,
                                    dist,
                                    bits_per_word,
                                    METHOD_NORMAL,
                                    normal_times);

    bool avx512_ok = measure_method(experiment,
                                    bitmap_bits,
                                    ones_count,
                                    dist,
                                    bits_per_word,
                                    METHOD_AVX512,
                                    avx512_times);

    bool correctness_ok = false;

    if (normal_ok && avx512_ok) {
        correctness_ok = check_correctness_for_case(experiment,
                                                    bitmap_bits,
                                                    ones_count,
                                                    dist,
                                                    bits_per_word);
    }

    double normal_median = normal_ok ? median_double(normal_times, REPEAT) : 0.0;
    double avx512_median = avx512_ok ? median_double(avx512_times, REPEAT) : 0.0;

    double speedup = avx512_median > 0.0 ? normal_median / avx512_median : 0.0;

    double normal_mups =
        normal_median > 0.0 ? (double)ones_count / normal_median * 1000.0 : 0.0;

    double avx512_mups =
        avx512_median > 0.0 ? (double)ones_count / avx512_median * 1000.0 : 0.0;

    fprintf(fp,
            "%s,%s,%s,%s,%u,%zu,%u,%d,%d,%d,%.3f,%.3f,%.4f,%.4f,%.4f,%s\n",
            experiment,
            experiment_name_cn(experiment),
            dist_id_name(dist),
            dist_name_cn(dist, bits_per_word),
            bitmap_bits,
            bitmap_words,
            ones_count,
            bits_per_word,
            WARMUP,
            REPEAT,
            normal_median,
            avx512_median,
            speedup,
            normal_mups,
            avx512_mups,
            correctness_ok ? "正确" : "错误");

    printf("实验名称: %s, 数据分布: %s, 位向量长度: %u bits, 置位数量: %u, "
           "普通C中位耗时: %.3f ns, AVX512中位耗时: %.3f ns, 加速比: %.2fx, 正确性: %s\n",
           experiment_name_cn(experiment),
           dist_name_cn(dist, bits_per_word),
           bitmap_bits,
           ones_count,
           normal_median,
           avx512_median,
           speedup,
           correctness_ok ? "正确" : "错误");
}

static void lab_density_sweep(FILE* fp) {
    const uint32_t test_sizes[] = {
        16, 32, 64, 256, 512, 1000,
        5000, 10000, 100000, 300000,
        500000, 700000, 900000, 1000000
    };

    const int num_sizes = sizeof(test_sizes) / sizeof(test_sizes[0]);

    for (int i = 0; i < num_sizes; ++i) {
        uint32_t ones = test_sizes[i];

        run_case(fp,
                 "density_sweep",
                 DEFAULT_BITMAP_BITS,
                 ones,
                 DIST_LOW_CONFLICT,
                 1);

        run_case(fp,
                 "density_sweep",
                 DEFAULT_BITMAP_BITS,
                 ones,
                 DIST_UNIFORM_RANDOM,
                 0);

        run_case(fp,
                 "density_sweep",
                 DEFAULT_BITMAP_BITS,
                 ones,
                 DIST_CLUSTERED,
                 32);
    }
}

static void lab_segment_size_sweep(FILE* fp) {
    const uint32_t segment_bits_list[] = {
        4096,
        16384,
        65536,
        262144,
        1048576,
        4194304,
        16777216,
        DEFAULT_BITMAP_BITS
    };

    const int num_segments = sizeof(segment_bits_list) / sizeof(segment_bits_list[0]);

    for (int i = 0; i < num_segments; ++i) {
        uint32_t segment_bits = segment_bits_list[i];

        uint32_t ones = segment_bits / 100;
        if (ones < 16) {
            ones = 16;
        }

        run_case(fp,
                 "segment_size_sweep",
                 segment_bits,
                 ones,
                 DIST_LOW_CONFLICT,
                 1);

        run_case(fp,
                 "segment_size_sweep",
                 segment_bits,
                 ones,
                 DIST_UNIFORM_RANDOM,
                 0);

        run_case(fp,
                 "segment_size_sweep",
                 segment_bits,
                 ones,
                 DIST_CLUSTERED,
                 32);
    }
}

static void lab_conflict_sweep(FILE* fp) {
    const int bpw_list[] = {1, 2, 4, 8, 16, 32};
    const int num_bpw = sizeof(bpw_list) / sizeof(bpw_list[0]);

    const uint32_t ones = 262144;

    for (int i = 0; i < num_bpw; ++i) {
        int bpw = bpw_list[i];

        run_case(fp,
                 "conflict_sweep",
                 DEFAULT_BITMAP_BITS,
                 ones,
                 DIST_CLUSTERED,
                 bpw);
    }
}

int main(int argc, char** argv) {
    const char* output_file = DEFAULT_OUTPUT_FILE;

    if (argc >= 2) {
        output_file = argv[1];
    }

    FILE* fp = fopen(output_file, "w");
    if (fp == NULL) {
        fprintf(stderr, "无法打开输出文件: %s\n", output_file);
        fprintf(stderr, "请确认 results 目录已经存在。\n");
        return 1;
    }

    printf("开始 SIMD 位向量构建实验\n");
    printf("结果输出文件: %s\n", output_file);
    printf("warm-up 次数: %d\n", WARMUP);
    printf("正式重复次数: %d\n", REPEAT);
    printf("统计指标: 中位数\n");
    printf("构建前是否排序: %s\n", SORT_INDICES_BEFORE_BUILD ? "是" : "否");
    printf("计时范围: 仅包含 bitmap_set_bits_normal / bitmap_set_bits_avx512\n");

    print_csv_header(fp);

    lab_density_sweep(fp);
    lab_segment_size_sweep(fp);
    lab_conflict_sweep(fp);

    fclose(fp);

    printf("实验完成，结果已写入: %s\n", output_file);

    return 0;
}