____
## INSTALLING PACKAGES
___
1. `pip install -r Requirements.txt `

--------------------------------------
## RUNNING THE INTEREST CALCULATION
--------------------------------------

There are four scripts used:

- `interest_main.py`
	- Main python script that calls `pre_processing.py`, `interest.py` and `utils.py`.
- `pre_processing.py`
    - Creates dictionaries for each account with account specific transaction, interest, closing date and principal amount information.
- `interest.py`
    - Adds lines to the transaction data for month ends, interest rate changes, financial year ends, closing dates and account inceptions.
    - Creates the amortization tables and calls  functions from `utils.py`.
- `utils.py`
    - Calculates the interest rate taking into account interest rate changes and closing dates.
    - Calculates the total interest accumulated over the period.

-------------------------------------
## THE MODEL
-------------------------------------

This model calculates interest on a loan compounded monthly using transaction level data and takes into account:

1. Closing dates - these are found in the data pre-processing procedure and put into a dictionary with the account number being the key.

2. Interest rate changes - these are in a dictionary with the key being the account number and the value being
a df giving the dates of interest rate changes and the interest rate.

3. Start date - here the start date is taken from the first line in the transaction data but it could be input from the dataset, a line would just need to be added for it in the dataframe in `interest.py`.
