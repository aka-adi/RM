gcc -O3 -mavx512f -mavx512vl -march=native bitmap.c main.c -o bitmap_test
./bitmap_test