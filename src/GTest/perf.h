bool perf_enabled = false;

#define WAIT_FOR_PERF_U (1000 * 50)

int gen_perf_process(char *tag);

int kill_perf_process(int perf_pid);
