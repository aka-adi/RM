
#include <vector>
#include <utility>
#include <string>

void genEE( std::string data_path, std::string write_dir, uint64_t rows);

void genRE( std::string data_path, std::string write_dir, int cardinality, uint64_t rows);

void genGE( std::string data_path, std::string write_dir, int group_length, int cardinality, uint64_t rows);

void genGEbyEE( std::string ee_path, std::string write_dir, int group_length, int cardinality, uint64_t rows);
