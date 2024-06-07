import datetime
import re
from decimal import Decimal

class Transaction:
  def __init__(self, row):
    self.row = row

  def __getitem__(self, key):
    return self.row[key]

  @classmethod
  def from_row(cls, row):
    reference = row['Reference']
    if reference == 'MANAGE FEE':
      return FeeTransaction(row)
    elif reference == 'Card Web':
      return CashInTransaction(row)
    elif re.match(r'^B\d+$', reference):
      return BuyTransaction(row)

  def date(self):
    date = self.row['Trade date']
    return datetime.datetime.strptime(date, '%d/%m/%Y').strftime('%Y-%m-%d')

  def quantity(self):
    return Decimal(self.row['Quantity'])

  def unit_cost(self):
    return Decimal(self.row['Unit cost (p)'])

  def value(self):
    return Decimal(self.row['Value (£)'])

class CashInTransaction(Transaction):
  def __init__(self, row):
    super().__init__(row)

  def event(self):
    return 'Cash_In'

  def feetax(self):
    return 0

  def price(self):
    return 1

  def quantity(self):
    return self.value()

  def symbol(self):
    return 'GBP'

class FeeTransaction(Transaction):
  def __init__(self, row):
    super().__init__(row)

  def event(self):
    return 'Fee'

  def feetax(self):
    return self.value() * -1

  def price(self):
    return 0

  def quantity(self):
    return 0

  def symbol(self):
    return 'GBP'

class BuyTransaction(Transaction):
  def __init__(self, row):
    super().__init__(row)

  def event(self):
    return 'Buy'

  def feetax(self):
    return (self.value() * -1) - (self.unit_cost() * self.quantity() / 100).quantize(Decimal('0.01'))

  def price(self):
    # todo: may need special casing for UK / non-UK stocks
    return self.unit_cost() / 100

  def symbol(self):
    description = self['Description']
    match = re.search(r'^(.*?)\s*\(', description)
    if match:
      return match.group(1)
    else:
      raise ValueError(f"Could not extract symbol from description {description}")
