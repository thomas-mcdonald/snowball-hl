import csv
import re
import json
from decimal import Decimal
from transaction import ShareTransaction, Transaction
import os

def load_file(filename):
  with open(input_file, 'r', encoding='ISO-8859-1') as f:
    # HL exports have 5 lines of metadata before the actual data
    for _ in range(5):
      f.readline()
    reader = csv.DictReader(f)
    return [Transaction.from_row(row) for row in reader]

# discover any unmapped companies in the input file
def validate_company_mapping(input_file):
  data = load_file(input_file)
  missing_companies = set()
  for txn in data:
    if type(txn) is ShareTransaction:
      company_string = txn._extract_symbol_from_description()
      company_config = txn._find_company_config(config)
      if company_config is None:
        missing_companies.add(company_string)
  return missing_companies

def convert(input_file, output_file, config):
  data = load_file(input_file)
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

inputs = os.listdir(input_dir)
missings = set()
for filename in inputs:
  input_file = os.path.join(input_dir, filename)
  missing_companies = validate_company_mapping(input_file)
  missings = missings.union(missing_companies)

if missings:
  json_schema = [{ 'name': c, 'isin': None, 'ticker': None, 'symbol': None } for c in missings]
  print('The following companies are missing from configuration:')
  for company in missings:
    print(f'  {company}')
  print('Add the following to config.json and configure with correct ISIN or ticker / market keys:')
  print(json.dumps(json_schema, indent=2))
  exit(1)


for filename in inputs:
  input_file = os.path.join(input_dir, filename)
  output_file = os.path.join(output_dir, filename)
  convert(input_file, output_file, config)
