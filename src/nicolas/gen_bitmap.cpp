#include <iostream>
#include <sys/mman.h>
#include <mutex>
#include <vector>
#include <random>
#include <chrono>
#include <unistd.h>
#include <stdio.h>
#include <signal.h>
#include <thread>
#include <fstream>
#include <urcu.h>
#include <utility>
#include <filesystem>
#include <stdlib.h>

#include "fastbit/bitvector_base.h"
#include "fastbit/bitvector.h"
using namespace std;

std::vector<std::pair<int, uint64_t>> get_sort_data(std::string path) {
	int *src;
	int fdes = open(path.c_str(), OPEN_READONLY);
	struct stat statbuf;
	fstat(fdes, &statbuf);
	src = (int *) mmap(0, statbuf.st_size, PROT_READ, MAP_PRIVATE, fdes, 0);

	std::vector<std::pair<int, uint64_t> > fileData(statbuf.st_size / sizeof(int));

	for(int i = 0; i < fileData.size(); i++) {
		fileData[i].first = src[i] - 1;
		fileData[i].second = i;
	}

	std::sort(fileData.begin(), fileData.end(), [](std::pair<int, uint64_t> a, std::pair<int, uint64_t> b) {if(a.first == b.first) return a.second < b.second; return a.first < b.first;});

	for(int i = 0; i < fileData.size(); i++) {
		assert(fileData[i].first == src[fileData[i].second] - 1);
	}

	return std::move(fileData);
}

std::string CheckDir(std::string dir_path) {
	// Check if the directory exists
	if (!std::filesystem::exists(dir_path)) {
		// Create the directory
		if (std::filesystem::create_directory(dir_path)) {
			std::cout << "Directory created: " << dir_path << std::endl;
		} else {
			std::cerr << "Failed to create directory: " << dir_path << std::endl;
			exit(1);
		}
	} else {
		std::cout << "Directory already exists: " << dir_path << std::endl;
	}
	return dir_path + (dir_path.back() == '/' ? "" : "/");
}


void genEE( std::string data_path, std::string write_dir, uint64_t rows) {

	write_dir = CheckDir(write_dir);

	Table_config c;
	c.enable_fence_pointer = false;

	auto data_v = std::move(get_sort_data(data_path));

	ibis::bitvector* curr_btv = new ibis::bitvector;
	curr_btv->adjustSize(0, rows);
	curr_btv->decompress();

	int curr_val = data_v[0].first;

	for(int i = 0; i < data_v.size(); i++) {
		if(curr_val != data_v[i].first) {
			stringstream ss;
			ss << write_dir << curr_val << ".bm";
			curr_btv->compress();
			curr_btv->write(ss.str().c_str());
			curr_btv->clear();
			curr_btv->adjustSize(0, rows);
			curr_btv->decompress();
			curr_val = data_v[i].first;
		}

		curr_btv->setBit(data_v[i].second, 1, &c);
	}

	stringstream ss;
	ss << write_dir << curr_val << ".bm";
	curr_btv->compress();
	curr_btv->write(ss.str().c_str());

	delete curr_btv;

}

void genRE( std::string data_path, std::string write_dir, int cardinality, uint64_t rows) {

	char name[] = "/tmp/tmpbitmapXXXXXX";
	auto tmp_path = mkdtemp(name);
	std::cout << tmp_path << std::endl;
	string ee_path(tmp_path, tmp_path + strlen(tmp_path));
	ee_path = CheckDir(ee_path);
	genEE(data_path, ee_path, rows);

	write_dir = CheckDir(write_dir);

	ibis::bitvector* curr_btv = new ibis::bitvector;

	for(int i = 0; i < cardinality; i++) {
		ibis::bitvector btv((ee_path + to_string(i) + ".bm").c_str());
		*curr_btv |= btv;

		curr_btv->compress();
		stringstream ss;
		ss << write_dir << i << ".bm";
		curr_btv->write(ss.str().c_str());
	}
	delete curr_btv;
	unlink(tmp_path);

}

void genGE( std::string data_path, std::string write_dir, int group_length, int cardinality, uint64_t rows) {

	char name[] = "/tmp/tmpbitmapXXXXXX";
	auto tmp_path = mkdtemp(name);
	string ee_path(tmp_path, tmp_path + strlen(tmp_path));
	ee_path = CheckDir(ee_path);
	genEE(data_path, ee_path, rows);

	write_dir = CheckDir(write_dir);

	for(int i = 0; i < cardinality; i += group_length) {

		ibis::bitvector curr_btv;

		for(int j = 0; j + i < cardinality && j < group_length; j++) {
			stringstream ss;
			ss << ee_path << j + i << ".bm";
			ibis::bitvector btv(ss.str().c_str());
			curr_btv |= btv;
		}

		stringstream w;
		w << write_dir << i << ".bm";
		curr_btv.compress();
		curr_btv.write(w.str().c_str());
	}
	unlink(tmp_path);

}

void genGEbyEE( std::string ee_path, std::string write_dir, int group_length, int cardinality, uint64_t rows) {

	write_dir = CheckDir(write_dir);
	ee_path = CheckDir(ee_path);

	for(int i = 0; i < cardinality; i += group_length) {

		ibis::bitvector curr_btv;

		for(int j = 0; j + i < cardinality && j < group_length; j++) {
			stringstream ss;
			ss << ee_path << j + i << ".bm";
			ibis::bitvector btv(ss.str().c_str());
			curr_btv |= btv;
		}

		stringstream w;
		w << write_dir << i << ".bm";
		curr_btv.compress();
		curr_btv.write(w.str().c_str());
	}

}
