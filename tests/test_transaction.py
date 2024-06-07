from src.transaction import BuyTransaction

def test_buy_transaction_symbol_extraction_before_denomination():
  txn = BuyTransaction({
    'Description': 'Vanguard FTSE Developed World ex-UK Equity Index Accumulation (GBP) 1 @  44955.97380'
  })
  assert txn._extract_symbol_from_description() == 'Vanguard FTSE Developed World ex-UK Equity Index Accumulation'
  txn = BuyTransaction({
    'Description': 'Vanguard FTSE Developed World ex-UK Equity Index Accumulation (GBP) 1.00 @  44955.97380'
  })
  assert txn._extract_symbol_from_description() == 'Vanguard FTSE Developed World ex-UK Equity Index Accumulation'

  txn = BuyTransaction({
    'Description': 'Microsoft Corporation Comm Stk US$ 0.0000125 (Crest Depository Interest) 10 @  10000.37'
  })
  assert txn._extract_symbol_from_description() == 'Microsoft Corporation Comm Stk US$ 0.0000125'

def test_buy_transaction_symbol_extraction_without_denomination():
  txn = BuyTransaction({
    'Description': 'Ocado Group plc Ordinary 2p 39 @  200.315'
  })
  assert txn._extract_symbol_from_description() == 'Ocado Group plc Ordinary 2p'

  txn = BuyTransaction({
    'Description': 'Ocado Group plc Ordinary 2p 39.5 @  2000.315'
  })
  assert txn._extract_symbol_from_description() == 'Ocado Group plc Ordinary 2p'
