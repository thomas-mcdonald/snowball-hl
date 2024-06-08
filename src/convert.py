import csv
import re
import json
from decimal import Decimal
from transaction import ShareTransaction, Transaction
import os

def convert(input_file, output_file, config):
  with open(input_file, 'r', encoding='ISO-8859-1') as f:
    # HL exports have 5 lines of metadata before the actual data
    for _ in range(5):
      f.readline()
    reader = csv.DictReader(f)
    data = [Transaction.from_row(row) for row in reader]

  # Validate configuration exists for all known companies in data
  missing_companies = set()
  for txn in data:
    if type(txn) is ShareTransaction:
      company_string = txn._extract_symbol_from_description()
      company_config = txn._find_company_config(config)
      if company_config is None:
        missing_companies.add(company_string)

  if missing_companies:
    raise ValueError(f'Could not find configuration for companies: {missing_companies}. Add mapping to config.json and run again.')

  output = [convert_txn(txn) for txn in data]

  with open(output_file, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=output[0].keys())
    writer.writeheader()
    writer.writerows(output)

def convert_txn(txn):
  return {
    'Currency': 'GBP',
    'Date': txn.date(),
    'Event': txn.event(),
    'FeeTax': txn.feetax(),
    'Market': txn.market(config),
    'Note': txn.note(),
    'Price': txn.price(),
    'Quantity': txn.quantity(),
    'Symbol': txn.symbol(config),
  }

with open('config.json', 'r') as f:
  config = json.load(f)

input_dir = 'input/'
output_dir = 'output/'

for filename in os.listdir(input_dir):
  input_file = os.path.join(input_dir, filename)
  output_file = os.path.join(output_dir, filename)
  convert(input_file, output_file, config)
