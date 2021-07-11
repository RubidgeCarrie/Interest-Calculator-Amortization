import pandas as pd


def interest_rate(id, interest_dict, transaction_date, closing_date, balance):
    """Returns interest rate as decimal (0-1)"""
    if balance < 0:
        rate = 0
    else:
        if pd.isnull(closing_date):
            if id in interest_dict.keys():
                temp_df = interest_dict[id]
                temp_df.sort_values(by = "start_date")
                for row in range(len(temp_df)):
                    date = temp_df.iloc[row].start_date
                    if transaction_date > date:
                        rate = temp_df.iloc[row].interest/100

            else:
                rate = 0.42

#  Checks closing date, if it is after the closing date, the rate is zero.
        else:
            if transaction_date <= closing_date:
                if id in interest_dict.keys():
                    temp_df = interest_dict[id]
                    for row in range(len(temp_df)):
                        date = temp_df.iloc[row].start_date
                        if transaction_date > date:
                            rate = temp_df.iloc[row].interest/100
                else:
                    rate = 0.42
            else:
                rate = 0
    return rate



def total_interest(amort_df, fin_year_start, fin_year_end, closing_date,
                    inception_date, account_nr):
    """Adds interest from start to end date"""

    interest = 0
    # If the account is opened before the financial period in question.
    if inception_date < fin_year_start:
        start_date = fin_year_start
    # If the account is opened after the financial peiod in question
    # the start date is given by the account inception date.
    else:
        start_date = inception_date

    end_date = fin_year_end

    # Interest is added from the start to the end of the financial period.
    for j in range(len(amort_df)):
        if ((amort_df['Date'].iloc[j] == fin_year_start) &
        (amort_df['Description'].iloc[j] == 'Month End Interest')):
            interest = interest
        else:
            if ((amort_df['Date'].iloc[j] >= start_date) &
                (amort_df['Date'].iloc[j] <= end_date)):
                interest  += amort_df['Interest'].iloc[j]
            else:
                interest = interest
    return interest
