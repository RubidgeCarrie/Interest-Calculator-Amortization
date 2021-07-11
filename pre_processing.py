def data_preprocessing(transaction_df, interest_df, loanbook_df):
    """ Takes in dataframes and outputs two dictionaries
    Args:
    transaction_df (df): transaction level data for each account with columns ['id', 'transaction_date','transaction_amount','description']
    interest_df (df): dataframe with row for each account id with the date of an interest rate change with columns ['id', 'interest', 'start_date']
    loanbook_df (df): account information for each account with columns ['id', 'inception_date', 'closing_date', 'principle_amount']
    Returns interest_dict (dict),df_dict (dict), acc_dict(dict)
    """

    # Create dictionary where id's are the keys and values are data frames with the interest and date.
    temp_ls = list(interest_df.groupby(['id'],as_index=False))
    interest_dict = {temp_ls[i][0]:temp_ls[i][1] for i in range(len(temp_ls))}

    # Groupby the account and create a dictionary with keys that are account id's and values that are their transaction data.
    temp_ls = list(transaction_df.groupby(['id'],as_index=False))
    df_dict = {temp_ls[i][0]:temp_ls[i][1] for i in range(len(temp_ls))}

    # Dictionary of dictionaries for each account with account info.
    acc_dict = {}
    for account in loanbook_df['id'].tolist():
        row = loanbook_df[loanbook_df['id'] == account]
        acc_dict[account]={}
        for column in loanbook_df.columns[1:]:
            acc_dict[account][column] = row[column].values[0]


    return interest_dict, df_dict, acc_dict
