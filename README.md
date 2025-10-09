
### Brief history of RABIT

Despite widespread endorsement of bitmap indexing for range queries (RQs) in many classic textbooks, its use has long been restricted to read-only, low-cardinality attributes. For example, Oracle database manuals suggest that "[DBAs] should keep in mind that bitmap indexes are usually easier to destroy and re-create than to maintain" [1], and Sybase IQ's bitmap indexes are "recommended for up to 1,000 distinct values" [2].

We therefore conduct a comprehensive study on existing bitmap indexing techniques. Our analysis reveals three key limitations: (1) the prevailing encoding schemes (equality encoding and range encoding) are ill-suited for RQs; (2) current bitvector merge operations are inefficient for RQs; and (3) the most efficient bitmap indexes for RQs (those based on range encoding) incur prohibitively high update costs.

We thus introduce RABIT, the first bitmap index designed for RQs on frequently updated, high-cardinality attributes in HTAP DBMSs. RABIT significantly expands the applicability of bitmap indexing, making it suitable for attributes of any cardinality in tables ranging from read-only to frequently updated. We demonstrate its capabilities by integrating RABIT into both DuckDB and an in-house DBMS inspired by PostgreSQL, using an HTAP workload. Our evaluation shows that RABIT delivers substantial performance improvements over both tree indexes and optimized scan techniques.

[1] https://docs.oracle.com/en/database/oracle/oracle-database/23/dwhsg/index.html

[2] https://infocenter.sybase.com/help/index.jsp?topic=/com.sybase.infocenter.dc00170.1510/html/iqapgv1/CIHECEAI.htm


------


### About this project

#### How is this project organized?

The core code resides in the src/bitmaps folder, which contains the baselines, including In-place (src/naive), UCB (src/ucb), UpBit (src/ub), and our algorithm RABIT (src/bitmaps/rabit).  

The file src/bitmaps/rabit/table.cpp contains the implementation of our algorithms. In particular, Rabit::evaluate() and Rabit::range() implement point and range queries, respectively. Our code currently support three types of encoding schemes, EE, RE, and our GE. The directory src/GTest contains our unit tests. 

It is worth noting that the function rcu_read_lock() is part of the Read-Copy-Update (RCU) synchronization mechanism, which we use to synchronize RQs and UDIs and for safe memory reclamation. Even though the name of the function includes the term "lock", it does not actually involve any locks or latches. In fact, on some platforms, compilers optimize this function entirely away, rendering it effectively no-op [3]. 

[3] https://docs.kernel.org/RCU/whatisRCU.html


#### How to generate the required datasets for evaluation?

Please use the following scripts to generate required datasets:

```sh
python3 gen_dataset.py
./gen_bitmap.sh
```

To generate the datasets used in Section 5.1 (GE is Optimal for RQs), please run the first provided script. The second script will create the corresponding bitmap indexes using different encoding schemes.

It is worth noting that the datasets are large and may take about 20 minutes to generate all of them. If you'd like to skip the generation process, you can download a pre-generated copy from our repository: https://github.com/junchangwang/Bitmap-dataset (optional acceleration resource).


#### How to run RABIT and replicate key experiments?

RABIT relies on c++17, python3, liburcu(-dev), and the Boost library. 

First, use the following command to compile the entire project. 

```sh
./build.sh 
```

Then, reproduce the key results by using the following command. 

```sh
./eva_scripts/run_RQ.py
./eva_scripts/analyse_RQ.py
```

The above command writes the experimental results to the directory ./eva_output, which contains three subdirectories. The raw_data/ subdirectory holds the output of our program, and graphs/ contains the evaluation figures generated.
