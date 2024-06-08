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
    reference = row['Reference'].upper()
    if reference == 'MANAGE FEE':
      return FeeTransaction(row)
    elif reference == 'CARD WEB' or reference == 'FPC':
      return CashInTransaction(row)
    elif re.match(r'^B\d+$', reference) or re.match(r'^S\d+$', reference):
      return ShareTransaction(row)
    elif reference == 'INTEREST':
      return InterestTransaction(row)
    else:
      raise ValueError(f"Unknown transaction type {reference}")

  def date(self):
    date = self.row['Trade date']
    return datetime.datetime.strptime(date, '%d/%m/%Y').strftime('%Y-%m-%d')

  def market(self, config):
    return None

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

class ShareTransaction(Transaction):
  def __init__(self, row):
    super().__init__(row)

  def event(self):
    if self['Reference'][0] == 'S':
      return 'Sell'
    else:
      return 'Buy'

  def feetax(self):
    return (self.value() * -1) - (self.unit_cost() * self.quantity() / 100).quantize(Decimal('0.01'))

  def price(self):
    # todo: may need special casing for UK / non-UK stocks
    return self.unit_cost() / 100

  def market(self, config):
    company_config = self._find_company_config(config)
    if company_config:
      return company_config.get('market', None)
    else:
      raise ValueError(f'Could not find market mapping for "{company_string}". Add mapping to config.json and run again.')

  def symbol(self, config):
    company_config = self._find_company_config(config)
    if company_config:
      return company_config.get('isin', None) or company_config['ticker']
    else:
      raise ValueError(f'Could not find ISIN mapping for "{company_string}". Add mapping to config.json and run again.')

  def _find_company_config(self, config):
    company_string = self._extract_symbol_from_description()
    return next((c for c in config['companies'] if c['name'] == company_string), None)

  def _extract_symbol_from_description(self):
    description = self['Description']
    match = re.search(r'^(.*?)\s*\(', description)
    if match is None:
      # handle non-denominated stock names
      decimal = r'\d*\.?\d*'
      match = re.search(rf'^(.*?)\s*{decimal}\s*@\s*{decimal}', description)
    if match is None:
      raise ValueError(f"Could not extract symbol from description {description}")
    return match.group(1)
