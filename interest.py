from datetime import timedelta
import pandas as pd
import numpy as np
from utils import *
from datetime import datetime
from pandas.tseries.offsets import MonthEnd

def amortization(account, df, start_year, end_year, interest_dict, acc_dict, additional_loan_ls,
                refund_payment_ls,  payment_ls,
                interest_func = interest_rate):
    """ Creates an amortization table and calculates interest from it
        for the relevant period

        Args:
        account (srt): account number
        df (dataframe): dataframe with columns [ 'transaction_date','transaction_amount','description']**.
        start_year (int): financial year to start from eg: 2019.
        end_year (int): financial year to end in eg: 2020.
        interest_dict (dict): loan id is the key, the value is a df with column ['id', 'interest', 'start_date']
        which give when interest has changed.
        acc_dict (dict): contains keys:  'inception_date', 'closing_date', 'principle_amount'
        additional_loan_ls (ls): transaction events to be treated as addition to outstanding.
        refund_payment_ls (ls): transaction events to be treated as refund of payment.
        payment_ls (ls): transaction events to be treated as payments.
        interest_func (str):  Returns interest rate, taking into account account closures (interest rate=0)
                              and interest rate changes.

        ** df should contain all paymnets that are treated as refunds,
        additional loan amounts and normal payments. Account transfers
        should be excluded and the date reconciled with closing date before using
        this function.

        Returns:
        DataFrame, Integer

    """

    closing_date = acc_dict['closing_date']
    principle_amount =acc_dict['principle_amount']
    inception_date = acc_dict['inception_date']


    #Create list of all end dates between the start of the loan and the financial year end.
    date_ls = pd.date_range(inception_date, end_date, freq='MS').to_pydatetime().tolist()

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#######################  ADDING ROWS TO DATAFRAME FOR THE AMORTIZATION TABLE #####################################
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

    # For all old accounts.
    if acc_dict['inception_date'] < start_date:
        start_row = [[start_date, "Financial year start", 0]]
        df = df.append(pd.DataFrame(start_row, columns =
        ["transaction_date","description","transaction_amount"]), ignore_index= True)


    # Add row for account closing date.
    if (pd.isnull(closing_date) == False):
        closing_row  = [[ closing_date, 0,  "Closing Date"]]
        df = df.append(pd.DataFrame(closing_row, columns =
        ['transaction_date','transaction_amount','description']), ignore_index= True)

    # Add row for interest rate changes.
    if id in interest_dict.keys():
            temp_df = interest_dict[id]
            temp_df.sort_values(by = "start_date")
            for row in range(len(temp_df)):
                date = temp_df.iloc[row].start_date
                new_row = [[date, 0, "Interest Rate Change"]]
                df = df.append(pd.DataFrame(new_row, columns =
                ['transaction_date','transaction_amount','description']), ignore_index= True)

    # Sort all added rows.
    df = df.sort_values(["transaction_date"])

    # To keep in order.
    index_ls = [i+1 for i in range(len(df))]
    df['index'] = index_ls

    # Adding a line in the dataframe for each month end date from laon inception to financial year end.
    for date in date_ls:
        row = [[date, 0, "Month End Interest", 0]]
        df = df.append(pd.DataFrame(row, columns =
        ['transaction_date','transaction_amount','description', 'index']), ignore_index= True)

    # Sort all added rows.
    df = df.sort_values(["transaction_date", "index"])

    # Create an interest location list so that we may add up all days between these calculations.
    int_loc_ls = [0]

    # Times cannot be saved in numpy array so we create list to append later.
    time_ls = []
    time_ls.append(acc_dict['inception_date'])
    for t in range(len(df)-1):
        time_ls.append(df['transaction_date'].iloc[t+1])

    # Payment description list for appending to df later.
    description_ls = []

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
################### CREATING THE AMORTIZATION TABLE ROW BY ROW, STARTING WITH THE FIRST ROW #########################
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

    # Create amortization table.
    table = np.zeros([len(df+1), 6])

    # Creating first line of table.

    # Opening_balance.
    table[0,0] = principle_amount
    # Payment
    table[0,1] = 0
    # Days - leave blank -- table[0,2].
    # Rate - make 0.
    table[0,3] = 0
    # Interest -leave blank -- table[0,4].
    # Closing_balance = opening_balance - payment + interest.
    table[0,5] =  table[0,0] - table[0,1] + table[0,4]
    # List for descriptions since we cannot put them in numpy array.
    description_ls.append("Account Inception")

    # Keep track of location of Month end interest in table to sum interest to that point.
    int_loc_ls = [0]
    # Running through each event, skipping first which is the Disbursement.
    for j in range(len(df)-1):
        # # Check for refunds first
        if df['description'].iloc[j+1] in refund_payment_ls:

             # Opening balance.
            table[j+1,0] = table[j,5]
            # Payment.
            table[j+1,1] = 0
            # Days.
            table[j+1,2] = (time_ls[j+1] - time_ls[j]).days
            # Rate = 0 if after closing date, otherwise rate is 42% unless it is changed in the interest changes data.
            table[j+1,3] = interest_func(id, interest_dict, df['transaction_date'].iloc[j+1], closing_date, table[j+1,0])
            # Interest = opening balance*(interest/365)*days.
            table[j+1,4] = round(table[j+1,0]*(table[j+1,3]/365),2)*table[j+1, 2]
            # Closing balance = opening_balance - payment
            table[j+1, 5] = table[j+1,0]  - table[j+1,1]
            # Payment description.
            description_ls.append(df['description'].iloc[j+1])

        #  Check if it is an additional loan or refund on some of outstanding amount.
        elif df['description'].iloc[j+1] in (additional_loan_ls):
            # Calculate interest on the outstanding amount, then update the outstanding amount
            # Opening balance - start with previous closing bance.
            table[j+1,0] = table[j,5]
            # Payment.
            table[j+1,1] = 0
            # Days.
            table[j+1,2] = (time_ls[j+1] - time_ls[j]).days
            # Rate = 0 if after closing date, otherwise rate is 42% unless it is changed in the interest changes data.
            table[j+1,3] = interest_func(id, interest_dict, df['transaction_date'].iloc[j+1], closing_date, table[j+1,0])
            # Interest = opening balance*(interest/365)*days.
            table[j+1,4] = round(table[j+1,0]*(table[j+1,3]/365),2)*table[j+1, 2]
            # Opening balance - redo this time add additional amount/ remove incentive.
            table[j+1,0] = table[j,5] + df['transaction_amount'].iloc[j+1]
            # Closing balance = opening_balance - payment
            table[j+1,5] = table[j+1,0] - table[j+1,1]
            # Payment description.
            description_ls.append(df['description'].iloc[j+1])

        elif df['description'].iloc[j+1] in ["Month End Interest"]:

            # Opening balance.
            table[j+1,0] = table[j,5]
            # Payment.
            table[j+1,1] = df['transaction_amount'].iloc[j+1]
            # Days.
            table[j+1,2] = (time_ls[j+1] - time_ls[j]).days
            # Rate = 0 if after closing date, otherwise rate is 42% unless it is changed in the interest changes data.
            table[j+1,3] = interest_func(id, interest_dict, df['transaction_date'].iloc[j+1], closing_date, table[j+1,0])
            # Interest = opening balance*(interest/365)*days.
            table[j+1,4] = round(table[j+1,0]*(table[j+1,3]/365),2)*table[j+1, 2]
            # Accrued interest from last month end, not including current date.
            last_loc = int_loc_ls[-1]
            current_loc = j+1
            int_accrued = np.sum(table[last_loc+1:current_loc, 4])
            # Closing balance = opening balance - payment + interest accrued
            table[j+1, 5] = table[j+1,0] - table[j+1,1] + int_accrued + table[j+1, 4]
            # Payment description.
            description_ls.append(df['description'].iloc[j+1])
            # Add location in table of Month End Interest.
            int_loc_ls.append(current_loc)

            # For every normal payment.
        else:
            # Opening balance.
            table[j+1,0] = table[j,5]
            # Payment.
            table[j+1,1] = df['transaction_amount'].iloc[j+1]
            # Days.
            table[j+1,2] = (time_ls[j+1] - time_ls[j]).days
            # Rate = 0 if after closing date, otherwise rate is 42% unless it is changed in the interest changes data.
            table[j+1,3] = interest_func(id, interest_dict, df['transaction_date'].iloc[j+1], closing_date, table[j+1,0])
            # Interest = opening balance*(interest/365)*days.
            table[j+1,4] = round(table[j+1,0]*(table[j+1,3]/365),2)*table[j+1, 2]
            # Closing balance = opening_balance - payment
            table[j+1,5] = table[j+1,0] - table[j+1,1]
            # Payment description.
            description_ls.append(df['description'].iloc[j+1])


    amort_df = pd.DataFrame(data=table, columns=["Opening Balance", "Payment"
    ,"Days", "Rate", "Interest", "Closing Balance"])
    amort_df['Date'] = time_ls
    amort_df['Description'] = description_ls
    interest = total_interest(amort_df, start_date, end_date, closing_date,
    acc_dict['inception_date'], account)

    return amort_df, interest
