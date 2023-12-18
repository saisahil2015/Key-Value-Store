# import pandas as pd
# import matplotlib.pyplot as plt

# # Load the data from the CSV file
# # df = pd.read_csv("autoscaling_client_metrics.csv")
# df = pd.read_csv("non-autoscaling_client_metrics.csv")

# # Sort the DataFrame by 'Client ID' or another metric if needed
# df.sort_values("Throughput", inplace=True)

# # Plotting
# plt.figure(figsize=(10, 6))
# plt.plot(df["Throughput"], df["Latency"], marker="o", linestyle="-")

# # Adding labels and title
# plt.xlabel("Throughput (operations per second)")
# plt.ylabel("Latency (seconds)")
# plt.title("Throughput vs Latency")

# # Show the plot with a grid
# plt.show()


# import pandas as pd
# import matplotlib.pyplot as plt

# # Load the data from the CSV file
# # df = pd.read_csv("autoscaling_client_metrics.csv")
# df = pd.read_csv("non-autoscaling_client_metrics.csv")

# # Sort the DataFrame by 'Client ID' or another metric if needed
# df.sort_values("Throughput", inplace=True)

# # Plotting
# plt.figure(figsize=(10, 6))
# plt.plot(df["Throughput"], df["Error Rate"], marker="o", linestyle="-")

# # Adding labels and title
# plt.xlabel("Throughput")
# plt.ylabel("Error Rate")
# plt.title("Throughput vs Error Rate")

# # Show the plot with a grid
# plt.show()


# import pandas as pd
# import matplotlib.pyplot as plt

# # Load the data from the CSV file
# df = pd.read_csv("multi-thread_reports/non-autoscaling_client_metrics.csv")
# # df = pd.read_csv(
# #     "multi-thread_reports/autoScalingWithFixedErrorRateAndLighterWorkloadThreshold.csv.csv"
# # )

# # Sort the DataFrame by 'Throughput'
# df.sort_values("Throughput", inplace=True)

# # # Calculate a moving average of the latency to smoothen the plot.
# # # Change the window size to adjust the amount of smoothing (larger window = more smoothing)
# # df["Latency_Smooth"] = df["Latency"].rolling(window=5).mean()

# # Plotting
# plt.figure(figsize=(10, 6))
# plt.plot(
#     df["Throughput"], df["Latency"], marker="o", linestyle="-"
# )  # Original data, more transparent
# # plt.plot(
# #     df["Throughput"], df["Latency_Smooth"], marker="", linestyle="-", color="red"
# # )  # Smoothed data

# # Adding labels and title
# plt.xlabel("Throughput (operations per second)")
# plt.ylabel("Latency (seconds)")
# plt.title("Throughput vs Latency")

# # Show the plot with a grid
# # plt.grid(True)
# plt.show()


# #THROUGHPUT VS LATENCY
# import pandas as pd
# import matplotlib.pyplot as plt

# # Load the data from the CSV files
# # df1 = pd.read_csv(
# #     "multi-thread_reports/non-autoscaling_client_metricsOnHeavierData.csv"
# # )
# # df2 = pd.read_csv("multi-thread_reports/autoscaling_client_metricsOnHeavierData.csv")
# df1 = pd.read_csv("./Final_Reports/Autoscaling/test12.csv")
# df2 = pd.read_csv("./Final_Reports/Autoscaling/test14.csv")
# df3 = pd.read_csv("./Final_Reports/Non-Autoscaling/test4.csv")

# # Sort the DataFrames by 'Throughput'
# df1.sort_values("Throughput", inplace=True)
# df2.sort_values("Throughput", inplace=True)
# df3.sort_values("Throughput", inplace=True)

# # Plotting
# plt.figure(figsize=(10, 6))

# # Plot data from the first CSV
# plt.plot(
#     df1["Throughput"],
#     df1["Latency"],
#     marker="o",
#     linestyle="-",
#     label="Autoscaling with Dynamic Threhsold",
# )

# # Plot data from the second CSV
# plt.plot(
#     df2["Throughput"],
#     df2["Latency"],
#     marker="x",
#     linestyle="-",
#     label="Autoscaling with Static Threshold",
# )

# plt.plot(
#     df3["Throughput"],
#     df3["Latency"],
#     marker="+",
#     linestyle="-",
#     label="Non-Autoscaling",
# )

# # Adding labels, title, and legend
# plt.xlabel("Throughput (operations per second)")
# plt.ylabel("Latency")
# plt.title(
#     "Throughput vs Latency for Heavier Workloads (Mean Writes > Mean Reads and Variable Key-Value Size)"
# )
# plt.legend()

# # Save the figure
# plt.savefig("scenario8", dpi=300, bbox_inches="tight")

# # Show the plot
# plt.show()


# # CLIENT ID VS ERROR RATE
# import pandas as pd
# import matplotlib.pyplot as plt

# # Load the data from the CSV files
# # df1 = pd.read_csv(
# #     "multi-thread_reports/non-autoscaling_client_metricsOnHeavierData.csv"
# # )
# # df2 = pd.read_csv("multi-thread_reports/autoscaling_client_metricsOnHeavierData.csv")
# df1 = pd.read_csv("./Final_Reports/Autoscaling/test1_cpuThreshold.csv")
# df2 = pd.read_csv("./Final_Reports/Autoscaling/test3_cpuThreshold.csv")
# df3 = pd.read_csv("./Final_Reports/Autoscaling/test2_cpuThreshold.csv")
# df4 = pd.read_csv("./Final_Reports/Autoscaling/test4_cpuThreshold.csv")

# df5 = pd.read_csv("./Final_Reports/Autoscaling/test9_cpuThreshold.csv")
# df6 = pd.read_csv("./Final_Reports/Autoscaling/test11_cpuThreshold.csv")
# df7 = pd.read_csv("./Final_Reports/Autoscaling/test10_cpuThreshold.csv")
# df8 = pd.read_csv("./Final_Reports/Autoscaling/test12_cpuThreshold.csv")


# # df3 = pd.read_csv("./Final_Reports/Non-Autoscaling/test4.csv")

# # Sort the DataFrames by 'Throughput'
# df1.sort_values("Index", inplace=True)
# df2.sort_values("Index", inplace=True)
# df3.sort_values("Index", inplace=True)
# df4.sort_values("Index", inplace=True)
# df5.sort_values("Index", inplace=True)
# df6.sort_values("Index", inplace=True)
# df7.sort_values("Index", inplace=True)
# df8.sort_values("Index", inplace=True)

# # Plotting
# plt.figure(figsize=(10, 6))

# # # Plot data from the first CSV
# plt.plot(
#     df1["Index"],
#     df1["CPU Threshold"],
#     # marker="o",
#     linestyle="-",
#     label="Lighter Workload (Mean Writes > Mean Reads)",
# )


# plt.plot(
#     df2["Index"],
#     df2["CPU Threshold"],
#     # marker="o",
#     linestyle="-",
#     label="Lighter Workload (Mean Reads > Mean Writes)",
# )

# plt.plot(
#     df3["Index"],
#     df3["CPU Threshold"],
#     # marker="o",
#     linestyle="-",
#     label="Heavier Workload (Mean Writes > Mean Reads)",
# )

# plt.plot(
#     df4["Index"],
#     df4["CPU Threshold"],
#     # marker="o",
#     linestyle="-",
#     label="Heavier Workload (Mean Reads > Mean Writes)",
# )

# # plt.plot(
# #     df5["Index"],
# #     df5["CPU Threshold"],
# #     # marker="o",
# #     linestyle="-",
# #     label="Lighter Workload (Mean Reads > Mean Writes)",
# # )

# # plt.plot(
# #     df6["Index"],
# #     df6["CPU Threshold"],
# #     # marker="o",
# #     linestyle="-",
# #     label="Lighter Workload (Mean Writes > Mean Reads)",
# # )

# # plt.plot(
# #     df7["Index"],
# #     df7["CPU Threshold"],
# #     # marker="o",
# #     linestyle="-",
# #     label="Heavier Workload (Mean Reads > Mean Writes)",
# # )


# # plt.plot(
# #     df8["Index"],
# #     df8["CPU Threshold"],
# #     # marker="o",
# #     linestyle="-",
# #     label="Heavier Workload (Mean Writes > Mean Reads)",
# # )

# # Adding labels, title, and legend
# plt.xlabel("Index")
# plt.ylabel("CPU Thresholds")
# plt.title(
#     "Evolution of CPU Thresholds for Dynamic Threshold Autoscaling Across Scenarios for Same Key-Value Sizes"
# )
# plt.legend()

# # Save the figure
# plt.savefig("cpuThresholdPlot_Same", dpi=300, bbox_inches="tight")

# # Show the plot
# plt.show()


# import pandas as pd
# import matplotlib.pyplot as plt

# # Load the data from the CSV files
# # df1 = pd.read_csv(
# #     "multi-thread_reports/non-autoscaling_client_metricsOnHeavierData.csv"
# # )
# # df2 = pd.read_csv("multi-thread_reports/autoscaling_client_metricsOnHeavierData.csv")
# df1 = pd.read_csv("./Final_Reports/Autoscaling/test4_resource_usage.csv")


# # df3 = pd.read_csv("./Final_Reports/Non-Autoscaling/test4.csv")

# # Sort the DataFrames by 'Throughput'
# df1.sort_values("Index", inplace=True)

# df1["Average CPU Usage"] *= 100
# df1["Average Memory Usage"] /= 15
# df1["Average Memory Usage"] *= 100

# # Plotting
# plt.figure(figsize=(10, 6))

# # # Plot data from the first CSV
# plt.plot(
#     df1["Index"],
#     df1["Average CPU Usage"],
#     # marker="o",
#     linestyle="-",
#     label="Average CPU Usage (%)",
# )
# plt.plot(
#     df1["Index"],
#     df1["Average Memory Usage"],
#     # marker="o",
#     linestyle="-",
#     label="Average Memory Usage (%)",
# )


# # Adding labels, title, and legend
# plt.xlabel("Index")
# plt.ylabel("Resource Usage")
# plt.title(
#     "Resource Usage for Heavier Workloads with Variable Key-Value Size (Mean Writes > Mean Reads)"
# )
# plt.legend()

# # Save the figure
# plt.savefig("resource_usage_plots", dpi=300, bbox_inches="tight")

# # Show the plot
# plt.show()


import pandas as pd
import matplotlib.pyplot as plt

# Initialize an empty list to store the number of containers for each test
num_containers_per_test = []

# Loop through each test file and extract the number of containers
for i in range(1, 17):
    file_name = f"./Final_Reports/Autoscaling/test{i}_overall.csv"
    df = pd.read_csv(file_name)
    # Assuming 'Num Containers' is the last value in the column
    num_containers = df["Num Containers Launched"].iloc[-1]
    num_containers_per_test.append(num_containers)

# Plotting the number of containers for each test
plt.figure(figsize=(10, 6))
plt.bar(range(1, 17), num_containers_per_test, color="blue")

plt.xlabel("Test Number")
plt.ylabel("Number of Containers")
plt.title("Number of Containers Launched in Each Test")
plt.xticks(range(1, 17))  # Set x-axis ticks to show each test number

plt.savefig("num_containers_per_test.png", dpi=300, bbox_inches="tight")
# plt.grid()
plt.show()
