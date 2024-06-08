# snowball-hl

A partial implementation of a HL account export -> Snowball Analytics import tool.

## Usage

Download reports from HL in CSV format and place them in the `input` directory. Run the `convert.py` script to generate files in `output` that can be imported into Snowball Analaytics.

## Notes

* HL reports are not great and they require many clicks in the web interface to download. The following URL can be used to download a CSV file for a given date range: https://online.hl.co.uk/my-accounts/capital-transaction-history/filter//format/csv/period/30/startDate/2024-05-08/endDate/2024-06-07
* Reports do not contain standard identifiers for companies. Snowball supports importing ISIN and symbols which can be configured in config.json. If you run the script and there is an unknown stock name you will need to add the ISIN to the config file to get output.
* My HL account has relatively few transactions in there. It is likely that there are edge cases that are not handled. Please raise an issue if you find a bug.
* Strongly suggest importing data into a sandbox portfolio and checking that the output is as expected before importing into a live portfolio.
