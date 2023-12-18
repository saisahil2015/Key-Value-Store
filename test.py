from test_autoscaling import run_clients
from test_autoscaling_static import run_clients_static
from test_nonautoscaling import run_clients_nonAutoscaling


LIGHT_WOKLOAD_TEST = "workload.txt"
HEAVY_WOKLOAD_TEST = "new_workload.txt"


STATS_FILE_NAME = "test8.csv"
OVERALL_STATS_FILE_NAME = "test8_overall.csv"
RESOURCE_USAGE_FILE_NAME = "test1_resource_usage.csv"
DYNAMIC_CPU_FILE_NAME = "test1_cpuThreshold.csv"


# run_clients_static(
#     HEAVY_WOKLOAD_TEST,
#     STATS_FILE_NAME,
#     OVERALL_STATS_FILE_NAME,
#     RESOURCE_USAGE_FILE_NAME,
# )


run_clients_nonAutoscaling(
    HEAVY_WOKLOAD_TEST,
    STATS_FILE_NAME,
    OVERALL_STATS_FILE_NAME,
)


# run_clients(
#     HEAVY_WOKLOAD_TEST,
#     STATS_FILE_NAME,
#     OVERALL_STATS_FILE_NAME,
#     RESOURCE_USAGE_FILE_NAME,
#     DYNAMIC_CPU_FILE_NAME,
# )
