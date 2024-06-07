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
    elif reference == 'INTEREST':
      return InterestTransaction(row)
    else:
      raise ValueError(f"Unknown transaction type {reference}")

  def date(self):
    date = self.row['Trade date']
    return datetime.datetime.strptime(date, '%d/%m/%Y').strftime('%Y-%m-%d')

  def note(self):
    return None

  def quantity(self):
    cleaned_str = self.row['Quantity'].replace(',', '')
    return Decimal(cleaned_str)

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

  def symbol(self, _):
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

  def symbol(self, _):
    return 'GBP'

class InterestTransaction(Transaction):
  def __init__(self, row):
    super().__init__(row)

  def event(self):
    return 'Cash_Gain'

  def feetax(self):
    return 0

  def note(self):
    return self['Description']

  def price(self):
    return 1

  def quantity(self):
    return self.value()

  def symbol(self, _):
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

  def symbol(self, config):
    description = self['Description']
    match = re.search(r'^(.*?)\s*\(', description)
    if match is None:
      raise ValueError(f"Could not extract symbol from description {description}")

    override = next((c for c in config['companies'] if c['name'] == match.group(1)), None)
    if override:
      return override['isin']
    else:
      raise ValueError(f'Could not find ISIN mapping for "{match.group(1)}". Add mapping to config.json and run again.')
