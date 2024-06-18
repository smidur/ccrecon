import pandas as pd

raw_dataframe = pd.read_csv('opera_trx_codes/raw_trx_codes.csv', sep='|', dtype='str')


class TransactionCodes:
    def __init__(self, df=raw_dataframe):
        # take only needed columns
        df = df[['TRX_CODE', 'D3']]

        # rename columns for convenience
        columns_new_names = ['code', 'descr']
        df.columns = columns_new_names

        # drop NaN
        df = df.dropna()

        # make column strings lowercase
        df['descr'] = df['descr'].apply(lambda x: x.lower() if isinstance(x, str) else x)

        # correcting some misspelled words
        misspelled_words = ['off line', 'on line', 'pele-link', 'nis ', ' nis ', ' nis', r' \- ', r' \-',
                            'american express', r'^mc', 'master card', 'isrcard', ' isr ', 'dolar-',
                            'diners club', 'pos-mastercard', 'pos-', 'e-shop', 'euro']
        correct_words = ['offline', 'online', 'pelelink', 'ils ', ' ils ', ' ils', ' ', ' ',
                         'amex', 'mastercard', 'mastercard', 'isracard', ' isracard ', 'usd',
                         'diners', 'pos mastercard', 'pos', 'eshop', 'eur']

        for misspelled, correct in zip(misspelled_words, correct_words):
            df['descr'] = df['descr'].str.replace(misspelled, correct, regex=True)

        # create new column for: currency(-ies);
        all_usd_variations = [' usd ', ' usd', 'usd ']
        df['usd'] = df['descr'].apply(
            lambda x: True if any(usd_var in x for usd_var in all_usd_variations) else False)

        # create new column for: transaction type(s);
        cards = ['visa', 'mastercard', 'isracard', 'amex', 'diners', 'union pay']
        df['card'] = df['descr'].apply(lambda x: True if any(card in x for card in cards) else False)
        df['online'] = df['descr'].apply(lambda x: True if 'online' in x else False)
        df['pos'] = df['descr'].apply(lambda x: True if 'deposit' not in x and 'pos' in x else False)
        df['parking'] = df['descr'].apply(lambda x: True if 'parking' in x else False)

        # other way of doing it but using numpy (import numpy as np) :
        # df['in_usd'] = np.where(df['descr'].str.contains(' usd '), True, False)

        # get rid of redundant words in description columns
        df['descr'] = df['descr'].str.replace(r'/[ ]*online[ ]*/', ' ', regex=True)
        df['descr'] = df['descr'].str.replace(r'[ ]*ils[ ]*|[ ]*usd[ ]*', ' ', regex=True)
        df['descr'] = df['descr'].str.replace(r'[ ]*pos[ ]+', '', regex=True)
        df['descr'] = df['descr'].str.replace(r'[ ]*offline[ ]*', '', regex=True)

        # trim whitespaces
        df['descr'] = df['descr'].apply(lambda x: x.strip() if isinstance(x, str) else x)

        df_cards_columns = ['code', 'descr', 'usd', 'online', 'pos', 'parking']
        df_cards = df.loc[df['card']]
        df_cards = df_cards[df_cards_columns]

        df_visa = df_cards.loc[df_cards['descr'].str.contains('visa')]

        df_mastercard = df_cards.loc[
            df_cards['descr'].str.contains('mastercard') |
            df_cards['descr'].str.contains('isracard')
            ]

        df_amex = df_cards.loc[df['descr'].str.contains('amex')]

        df_diners = df_cards.loc[df_cards['descr'].str.contains('diners')]

        # df_union_pay = df_cards.loc[df_cards['descr'].str.contains('union')]

        df_pos = df_cards.loc[df_cards['pos']]

        df_offline = df_cards.loc[df_cards['online'] == False]

        df_online = df_cards.loc[df_cards['online']]

        # check if anything left to sort out
        # ~  means NOT IN
        # df_other = df.loc[~df['descr'].isin(df_cards['descr'])]

        self.df_cards = df_cards
        self.df_visa = df_visa
        self.df_mastercard = df_mastercard
        self.df_amex = df_amex
        self.df_diners = df_diners
        self.df_pos = df_pos
        self.df_online = df_online
        self.df_offline = df_offline

    def save_to_csv(self):
        self.df_cards.to_csv('cards.csv', sep='|', index=False, encoding='utf-8')
        self.df_visa.to_csv('cards_visa.csv', sep='|', index=False, encoding='utf-8')
        self.df_mastercard.to_csv('cards_mastercard.csv', sep='|', index=False, encoding='utf-8')
        self.df_amex.to_csv('cards_amex.csv', sep='|', index=False, encoding='utf-8')
        self.df_diners.to_csv('cards_diners.csv', sep='|', index=False, encoding='utf-8')
        self.df_pos.to_csv('cards_pos.csv', sep='|', index=False, encoding='utf-8')
        self.df_online.to_csv('cards_online.csv', sep='|', index=False, encoding='utf-8')
        self.df_offline.to_csv('cards_offline.csv', sep='|', index=False, encoding='utf-8')


trx_codes = TransactionCodes()

if __name__ == "__main__":
    TransactionCodes().save_to_csv()
