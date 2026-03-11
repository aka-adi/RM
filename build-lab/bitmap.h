#pragma once

void bitmap_set_bits_normal(
    uint32_t* dst, 
    const uint32_t* indices, 
    int count
);
void bitmap_set_bits_avx512(
    uint32_t* dst, 
    const uint32_t* indices, 
    int count
);