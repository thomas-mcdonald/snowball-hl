import csv
import re
from decimal import Decimal
from transaction import Transaction

def convert(input_file, output_file):
  with open(input_file, 'r', encoding='ISO-8859-1') as f:
    # HL exports have 5 lines of metadata before the actual data
    for _ in range(5):
      f.readline()
    reader = csv.DictReader(f)
    data = [row for row in reader]

  output = [convert_row(row) for row in data]

  with open(output_file, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=output[0].keys())
    writer.writeheader()
    writer.writerows(output)

def convert_row(row):
  txn = Transaction.from_row(row)
  return {
    'Currency': 'GBP',
    'Date': txn.date(),
    'Event': txn.event(),
    'FeeTax': txn.feetax(),
    'Price': txn.price(),
    'Quantity': txn.quantity(),
    'Symbol': txn.symbol(),
  }

convert('input/portfolio-summary (1).csv', 'output/portfolio-summary.csv')
