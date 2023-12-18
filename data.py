import sqlite3
import csv

print("Check")
# Connect to your database
conn = sqlite3.connect("databases.db")
cursor = conn.cursor()

# Execute a SQL query
# cursor.execute("SELECT * FROM Key_value;")
cursor.execute("SELECT * FROM Workload;")

# Fetch and display results
print([description[0] for description in cursor.description])
rows = cursor.fetchall()
for row in rows:
    print(row)

# Write to CSV
with open("updated_features_data.csv", "w", newline="") as csv_file:
    csv_writer = csv.writer(csv_file, delimiter=",")

    header = [description[0] for description in cursor.description]
    csv_writer.writerow(header)

    csv_writer.writerows(rows)

# Close connection
conn.close()
