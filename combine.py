import pandas as pd

df1 = pd.read_csv('data_with_stats.csv', index_col=0)
df2 = pd.read_csv('updated_heavier_data.csv', index_col=0)

last_index = df1.index[-1]
df2.index = range(last_index + 1, last_index + 1 + len(df2))

# Concatenate the two dataframes
combined_df = pd.concat([df1, df2])

# Write the combined dataframe to a new CSV file
combined_df.to_csv('combined.csv')
