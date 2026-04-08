#include <stdint.h>
#include <string.h>
#include <immintrin.h>
#include <stdio.h>

// 普通 C 版本：不使用 AVX
void bitmap_set_bits_normal(
    uint32_t* dst, 
    const uint32_t* indices, 
    int count
) {
    for (int i = 0; i < count; ++i) {
        uint32_t idx = indices[i];
        uint32_t w = idx / 32;
        uint32_t b = idx % 32;
        dst[w] |= 1U << b;
    }
}

void bitmap_set_bits_avx512(
    uint32_t* dst,
    const uint32_t* indices,
    int count
) {
    int i = 0;
    const __m512i one    = _mm512_set1_epi32(1);
    const __m512i low5   = _mm512_set1_epi32(0x1F);
    const __m512i zero   = _mm512_setzero_si512();

    for (; i + 15 < count; i += 16) {
        // 1) 计算 addr = idx / 32, bit = idx % 32
        __m512i idx  = _mm512_loadu_si512((const void*)(indices + i));
        __m512i addr = _mm512_srli_epi32(idx, 5);
        __m512i bit  = _mm512_and_si512(idx, low5);
        __m512i mask = _mm512_sllv_epi32(one, bit);

        // 2) 使用 vpconflictd 检测 addr 是否有重复
        //    conflicts 的每个 lane 非 0 表示该 lane 与之前某个 lane 地址重复
        __m512i conflicts = _mm512_conflict_epi32(addr);
        __mmask16 conflict_mask = _mm512_cmpneq_epi32_mask(conflicts, zero);

        if (conflict_mask == 0) {
            // 无冲突：gather -> OR -> scatter
            __m512i mem = _mm512_i32gather_epi32(addr, (const void*)dst, 4);
            __m512i out = _mm512_or_si512(mem, mask);
            _mm512_i32scatter_epi32((void*)dst, addr, out, 4);
        } else {
            for (int j = 0; j < 16; ++j) {
                uint32_t idx = indices[i + j];
                uint32_t w   = idx >> 5;        // idx / 32
                uint32_t b   = idx & 0x1F;      // idx % 32
                dst[w] |= (1u << b);
            }
        }
    }

    // 处理剩余不足 16 个
    for (; i < count; ++i) {
        uint32_t idx = indices[i];
        uint32_t w   = idx >> 5;        // idx / 32
        uint32_t b   = idx & 0x1F;      // idx % 32
        dst[w] |= (1u << b);
    }
}

