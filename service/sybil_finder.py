import os
import requests
import csv
from dotenv import load_dotenv
import time
import sqlite3

# Load environment variables
load_dotenv()


def retrieve_dune_addresses():
    # Define Dune API endpoint and headers
    API_KEY = os.getenv("DUNE_TOKEN")
    QUERY = os.getenv("DUNE_QUERY")
    ENDPOINT = f"https://api.dune.com/api/v1/execution/{QUERY}/results/csv"
    FILENAME = "data/result_average_amount_10.csv"
    LIMIT = 3000

    # Initialize offset and total count
    offset = 1434000
    last_count = LIMIT

    # Open the file in write mode
    with open(FILENAME, 'w', newline='') as f_out:
        writer = csv.writer(f_out)

        while last_count >= LIMIT:
            # Make request with current offset
            response = requests.get(ENDPOINT, headers={"X-Dune-API-Key": API_KEY}, params={"limit": LIMIT, "offset": offset})

            # Check if the request was successful
            if response.status_code == 200:
                # Write the response content to the CSV file
                lines = response.text.strip().split('\n')
                reader = csv.reader(lines)
                rows = list(reader)

                # If this is the first chunk, write the header
                if offset == 0:
                    writer.writerows([rows[0]])

                # Write data excluding the header
                writer.writerows(rows[1:])

                # Update the total count
                last_count = len(rows)

                # Update offset for the next request
                offset += LIMIT
                time.sleep(3)
            else:
                print(f"Failed to retrieve data. Status code: {response.status_code}")
                print(f"Last offset: {offset}")
                break

    print("Data retrieval completed.")


def check_sybil(file_name):
    # Load addresses from files
    def load_addresses(file_path):
        with open(file_path, 'r') as file:
            return set(file.read().splitlines())

    addresses_to_check = load_addresses(file_name)
    sybil_addresses = load_addresses('sybil.txt')
    not_sybil_addresses = load_addresses('not_sybil.txt')

    # Filter addresses not in sybil.txt or not_sybil.txt
    filtered_addresses = [address for address in addresses_to_check if address not in sybil_addresses and address not in not_sybil_addresses]

    # Write filtered addresses to result.txt
    with open('result.txt', 'w') as file:
        file.write('\n'.join(filtered_addresses))


def find_common_items(file1, file2):
    try:
        # Read the first file and store items in a set
        with open(file1, 'r', encoding='utf-8') as f1:
            items1 = set(f1.read().splitlines())

        # Read the second file and store items in a set
        with open(file2, 'r', encoding='utf-8') as f2:
            items2 = set(f2.read().splitlines())

        # Find the intersection of both sets
        common_items = items1.intersection(items2)

        # Return the common items
        return common_items
    except FileNotFoundError:
        return "One or more files could not be found."
    except Exception as e:
        return f"An error occurred: {str(e)}"


def filter_addresses(db_path, file1, file2, output_file, output_table):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Read the file contents into sets
        with open(file1, 'r', encoding='utf-8') as f1:
            items1 = set(f1.read().splitlines())

        with open(file2, 'r', encoding='utf-8') as f2:
            items2 = set(f2.read().splitlines())

        # Intersection of both files to find common addresses
        common_addresses = items1.intersection(items2)

        # Query the database for entries with these addresses
        query = "SELECT * FROM dune_items WHERE ua IN ({})".format(
            ','.join('?' for _ in common_addresses))
        cursor.execute(query, list(common_addresses))
        results = cursor.fetchall()

        # Write the addresses to the output file
        with open(output_file, 'w', encoding='utf-8') as f:
            for result in results:
                f.write(result[0] + '\n')

        # Create the new table with the same structure
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {output_table} LIKE dune_items")
        conn.commit()

        # Insert filtered data into the new table
        insert_query = f"INSERT INTO {output_table} VALUES (?,?,?,?,?,?,?)"
        cursor.executemany(insert_query, results)
        conn.commit()

        return "Process completed successfully."
    except Exception as e:
        return f"An error occurred: {str(e)}"
    finally:
        # Close the database connection
        conn.close()
