from decimal import Decimal

class Transaction:
  def __init__(self, row):
    self.row = row

  def __getitem__(self, key):
    return self.row[key]

  def quantity(self):
    return Decimal(self.row['Quantity'])

  def unit_cost(self):
    return Decimal(self.row['Unit cost (p)'])

  def value(self):
    return Decimal(self.row['Value (£)'])
