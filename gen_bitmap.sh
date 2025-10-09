#!/bin/bash

# Script: gen_bitmap.sh
# Description: Script for bitmap generation from dataset_* files with configurable parameters
#
# Options:
#   -n : Total number of rows (default: 100000000)
#   -c : Cardinality (default: 100)
#	-e : Encoding type among EE, RE, and GE (default: EE)
#   -l : Length of groups when GE is specified (default: 10)
#
# Example usage:
#   ./gen_bitmap.sh -n 1000000 -c 200 -l 20 -e GE

n=100000000
c=100
g_len=10
e=EE

while getopts "n:c:l:e:" opt; do
	case $opt in
		n)
			n=$OPTARG
			;;
		c)
			c=$OPTARG
			;;
		l)
			g_len=$OPTARG
			;;
		e)
			e="$OPTARG"
			;;
		\?)
			echo "error input"
			exit 1
		;;
	esac
done

vn=`expr $n / 1000000`
index_path=BM_${vn}M_${c}
if echo $e | grep -q "RE"; then
	index_path=${index_path}_RE
else
	index_path=${index_path}_EE
fi
index_path=${index_path}_32
group_path=BM_${vn}M_${c}_GE_${g_len}_32

cmd="./build/nicolas --cardinality ${c} --index-path ${index_path} --group-path ${group_path} --number-of-rows $n --data-path dataset_${n}_${c} --mode build --encoding-scheme ${e} --GE-group-len ${g_len}"

echo $cmd
$cmd
