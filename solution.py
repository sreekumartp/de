import sqlite3
import csv
from datetime import datetime
import re

# Create in-memory SQLite database
conn = sqlite3.connect(':memory:')
cursor = conn.cursor()

# Load customers
with open('customers.csv', 'r') as f:
    reader = csv.DictReader(f)
    cursor.execute('''
        CREATE TABLE customers (
            customer_id TEXT PRIMARY KEY,
            name TEXT,
            country TEXT,
            signup_date TEXT
        )
    ''')
    for row in reader:
        cursor.execute('''
            INSERT INTO customers VALUES (?, ?, ?, ?)
        ''', (row['customer_id'], row['name'], row['country'], row['signup_date']))

conn.commit()

# Get valid customer IDs for validation
cursor.execute('SELECT customer_id FROM customers')
valid_customers = set(row[0] for row in cursor.fetchall())

# Create orders table
cursor.execute('''
    CREATE TABLE orders (
        order_id TEXT,
        customer_id TEXT,
        order_date TEXT,
        amount REAL,
        status TEXT,
        FOREIGN KEY(customer_id) REFERENCES customers(customer_id)
    )
''')

def parse_amount(amount_str):
    """Parse amount string, removing currency symbols, commas, and whitespace"""
    if not amount_str:
        return None
    # Remove whitespace, currency symbols, and commas
    cleaned = re.sub(r'[\s$,]', '', amount_str)
    try:
        return float(cleaned)
    except ValueError:
        return None

def parse_date(date_str):
    """Parse date in multiple formats, return datetime if year is 2024"""
    if not date_str:
        return None
    date_str = date_str.strip()

    formats = [
        '%Y-%m-%d',  # 2024-01-05
        '%Y/%m/%d',  # 2024/01/09
        '%m/%d/%Y',  # 05/12/2024
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            if dt.year == 2024:
                return dt
            return None  # Not 2024
        except ValueError:
            continue
    return None  # Could not parse

# Track seen order_ids for deduplication
seen_orders = set()

# Load orders with cleaning
with open('orders.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        order_id = row.get('order_id', '').strip()
        customer_id = row.get('customer_id', '').strip()
        order_date = row.get('order_date', '').strip()
        amount_str = row.get('amount', '').strip()
        status = row.get('status', '').strip()

        # Skip if duplicate order_id
        if order_id in seen_orders:
            continue

        # Skip if missing or invalid customer_id
        if not customer_id or customer_id not in valid_customers:
            continue

        # Skip if status is not "completed" (case-insensitive)
        if status.upper() != 'COMPLETED':
            continue

        # Parse date - skip if not 2024
        parsed_date = parse_date(order_date)
        if parsed_date is None:
            continue

        # Parse amount
        amount = parse_amount(amount_str)
        if amount is None:
            continue

        # Insert cleaned order
        cursor.execute('''
            INSERT INTO orders (order_id, customer_id, order_date, amount, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (order_id, customer_id, parsed_date.strftime('%Y-%m-%d'), amount, status.upper()))

        seen_orders.add(order_id)

conn.commit()

# Query for top 5 customers by 2024 revenue
query = '''
    SELECT
        c.customer_id,
        c.name,
        SUM(o.amount) as net_revenue
    FROM customers c
    INNER JOIN orders o ON c.customer_id = o.customer_id
    GROUP BY c.customer_id, c.name
    ORDER BY net_revenue DESC
    LIMIT 5
'''

cursor.execute(query)
results = cursor.fetchall()

# Print results
print("customer_id,name,net_revenue")
for row in results:
    customer_id, name, net_revenue = row
    print(f"{customer_id},{name},{net_revenue:.2f}")

conn.close()
