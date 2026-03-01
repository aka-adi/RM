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
    for (; i + 15 < count; i += 16) {
        __m512i idx = _mm512_load_si512((const __m512i*)(indices + i));

        // idx / 32
        __m512i addr = _mm512_srli_epi32(idx, 5);

        // idx % 32
        __m512i bit  = _mm512_and_si512(idx, _mm512_set1_epi32(0x1F));

        __m512i one  = _mm512_set1_epi32(1);

        __m512i mask = _mm512_sllv_epi32(one, bit);

        //  gather: dst[addr[0..15]] -> 向量
        __m512i mem  = _mm512_i32gather_epi32(addr, (const __m512i*)dst, 4);

        __m512i out  = _mm512_or_si512(mem, mask);
        //  scatter: 向量 -> dst[addr[0..15]]
        _mm512_i32scatter_epi32(dst, addr, out, 4);

    // 剩余不足16个
    for (; i < count; i++) {
        uint32_t idx = indices[i];
        uint32_t w = idx / 32;
        uint32_t b = idx % 32;
        dst[w] |= 1U << b;
    }
}
}



