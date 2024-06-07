import csv
import datetime
import re
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
  txn = Transaction(row)
  return {
    'Currency': 'GBP',
    'Date': map_hl_date_to_date(row['Trade date']),
    'Event': map_hl_reference_to_event(row['Reference']),
    'FeeTax': map_hl_data_to_feetax(txn),
    'Price': map_hl_data_to_price(txn),
    'Quantity': map_hl_data_to_quantity(txn),
    'Symbol': map_hl_data_to_symbol(txn),
  }

def map_hl_data_to_feetax(data):
  if re.match(r'^B\d+$', data['Reference']):
    return data.value() - (data.unit_cost() * data.quantity() * 100)
  return 0

def map_hl_data_to_symbol(data):
  if data['Reference'] == 'MANAGE FEE' or data['Reference'] == 'Card Web':
    return 'GBP'
  elif re.match(r'^B\d+$', data['Reference']):
    description = data['Description']
    match = re.search(r'^(.*?)\s*\(', description)
    if match:
      return match.group(1)
    else:
      return None
  else:
    return None

def map_hl_data_to_price(data):
  if data['Reference'] == 'MANAGE FEE' or data['Reference'] == 'Card Web':
    return 1
  elif re.match(r'^B\d+$', data['Reference']):
    return data['Unit cost (p)']
  else:
    return None

def map_hl_data_to_quantity(data):
  if data['Reference'] == 'MANAGE FEE' or data['Reference'] == 'Card Web':
    return data['Value (£)']
  elif re.match(r'^B\d+$', data['Reference']):
    return data['Quantity']
  else:
    return None


def map_hl_reference_to_event(reference):
  if reference == 'MANAGE FEE':
    return 'Fee'
  elif reference == 'Card Web':
    return 'Cash_In'
  elif re.match(r'^B\d+$', reference):
    return 'Buy'
  else:
    raise ValueError(f"Unknown reference {reference}")

def map_hl_date_to_date(date):
  return datetime.datetime.strptime(date, '%d/%m/%Y').strftime('%Y-%m-%d')


convert('input/portfolio-summary (1).csv', 'output/portfolio-summary.csv')
