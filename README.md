# snowball-hl

A partial implementation of a HL account export -> Snowball Analytics import tool.

## Usage

Note: HL does not provide well known identifiers for companies in their account activity reports. The most time consuming part of this process is mapping the company names in the HL report to the ISIN or ticker + market of the underlying stock. If you have an account that mostly trades funds, this is ok. If you're actively managing lots of stocks, it will be a pain.

1. Download reports from HL in CSV format and place them in the `input` directory.
2. Run the `convert.py` script to discover missing stocks in the configuration file.
3. Provide mappings in `config.json` for those stocks.
4. Re-run `convert.py` to generate files in `output` that can be imported into Snowball Analaytics.

## Notes

* HL reports are not great and they require many clicks in the web interface to download. The following URL can be used to download a CSV file for a given date range and generalises - login to a browser and page through this year by year to get transaction history: https://online.hl.co.uk/my-accounts/capital-transaction-history/filter//format/csv/period/30/startDate/2024-05-08/endDate/2024-06-07
* My HL account has relatively few transactions in there. It is likely that there are edge cases that are not handled. Please raise an issue if you find a bug.
* Strongly suggest importing data into a sandbox portfolio and checking that the output is as expected before importing into a live portfolio.
