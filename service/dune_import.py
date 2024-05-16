import csv
import sqlite3

# CSV filename and SQLite database filename
CSV_FILENAME = "data/result_average_amount_10.csv"
DB_FILENAME = "data/dune_data.db"

# Create SQLite connection and cursor
conn = sqlite3.connect(DB_FILENAME)
c = conn.cursor()

# Create table if not exists
# Ethereum address, Transaction count, Amount bridged, Average amount, Interacted Source Chains / Destination Chains / Contracts Count, Unique Active Days / Weeks / Months, LZ Age In Days
c.execute('''CREATE TABLE IF NOT EXISTS dune_items
             (ua TEXT, tc INTEGER, amt REAL, amt_avg REAL, cc TEXT, dwm TEXT, lzd INTEGER)''')

# Open CSV file and import data into SQLite database
with open(CSV_FILENAME, 'r') as csv_file:
    csv_reader = csv.reader(csv_file)
    # Skip the header row
    next(csv_reader)
    for row in csv_reader:
        # Extract values from CSV row
        ua, tc, amt, amt_avg, cc, dwm, lzd = row

        # Convert types as necessary
        tc = int(tc)
        amt = float(amt)
        amt_avg = float(amt_avg)
        lzd = int(lzd)

        # Insert data into SQLite database
        c.execute('''INSERT INTO dune_items (ua, tc, amt, amt_avg, cc, dwm, lzd) VALUES (?, ?, ?, ?, ?, ?, ?)''',
                  (ua, tc, amt, amt_avg, cc, dwm, lzd))

# Commit changes and close connection
conn.commit()
conn.close()

print("Data imported into SQLite database successfully.")
