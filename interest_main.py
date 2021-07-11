# import packages and other files.
from utils import *
from interest import *

def main(interest_source_path, transaction_source_path, loanbook_source_path, start_date, end_date, additional_loan_ls, refund_payment_ls, payment_ls):
    """
    Calculates the amortization table and total interest accumulated over a given period, for each account, using transaction level data.
    Args:
    interest_source_path: path to interest table that gives the interest rate at dates the rate changes, for each account with columns ['id', 'interest', 'start_date'].
    transaction_source_path: path to transaction level data with columns ['id', 'transaction_date','transaction_amount','description'].
    loanbook_source_path: path to account information with columns ['id', 'inception_date', 'closing_date', 'principle_amount'].
    start_date: (datetime) Start of the period over which the interest is to be calculated.
    end_date: (datetime) End of the period over which the interest is to be calculated.
    additional_loan_ls (ls): transaction events to be treated as addition to outstanding.
    refund_payment_ls (ls): transaction events to be treated as refund of payment.
    payment_ls (ls): transaction events to be treated as payments.

    returns dataframes

    """
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    ############################################ INITIAL SETUP OF DATA ####################################################
    #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

    # Import data.
    interest_df = pd.read_excel(interest_source_path)
    transaction_df = pd.read_csv(transaction_source_path)
    loanbook_df = pd.read_csv(loanbook_source_path)


    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    ##############################  CREATING DICTIONARIES OF ACCOUNT SPECIFIC INFORMATION #################################
    #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

    interest_dict, df_dict, acc_dict = data_preprocessing(transaction_df, interest_df, loanbook_df)

    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    #######################  RUNNING THROUGH EACH ACCOUNT AND CREATING AN AMORTIZATION TABLE ##############################
    #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

    amort_ls = []
    account_ls = []
    interest_recalc = []
    result_dict = {}
    loan_status_ls = []
    # Running through each account to create an amortization table and sum interest from start_date to end_date
    for account in df_dict.keys():
        df = df_dict[account]
        account_dict = acc_dict[account]
        amort_df, interest = amortization(account, df, start_year, end_year, interest_dict,
        account_dict, additional_loan_ls, refund_payment_ls, payment_ls, interest_value)
        amort_ls.append(amort_df)
        account_ls.append(account)
        interest_recalc.append(interest)
        result_dict[account] = amort_df
        loan_status_ls.append(loan_status)

    # Joining amortization tables for all accounts together and including account ids.
    for i in range(len(amort_ls)):
        data = amort_ls[i]
        temp_ls =  [account_ls[i] for j in range(len(data))]
        data['Account'] = temp_ls
    all_amorts = pd.concat(amort_ls)

    # Creating a dataframe with the final results.
    df_final = pd.DataFrame()
    df_final['Account'] =  account_ls
    df_final['Interest'] = interest_recalc

    return all_amorts, df_final
