import pandas as pd

# Load the first CSV file
df1 = pd.read_csv("updated_heavier_data.csv")

# Load the second CSV file
df2 = pd.read_csv("data_with_stats.csv")

# Concatenate the two dataframes
combined_df = pd.concat([df1, df2])

# Drop duplicates, if any
combined_df_unique = combined_df.drop_duplicates(subset=["num_read", "num_write"])

# Save the combined unique data to a new CSV file
combined_df_unique.to_csv("combined_unique.csv", index=False)

print("Combined CSV with unique records saved as 'combined_unique.csv'")
