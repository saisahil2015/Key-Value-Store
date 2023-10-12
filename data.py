import sqlite3

print("Check")
# Connect to your database
conn = sqlite3.connect("databases.db")
cursor = conn.cursor()

# Execute a SQL query
# cursor.execute("SELECT * FROM Key_value;")
cursor.execute("SELECT * FROM Workload;")

# Fetch and display results
rows = cursor.fetchall()
for row in rows:
    print(row)

# Close connection
conn.close()
