from abc import ABC, abstractmethod
import pandas as pd


def find_value(df: pd.DataFrame, column_name: str, value: str) -> pd.DataFrame | None:
    value = str(value)
    discovered = df.loc[df[column_name].str.contains(value, regex=True)]
    return discovered


class DataframeOps(ABC):

    @abstractmethod
    def __init__(self, file: str, rate: float):
        pass

    @abstractmethod
    def set_columns(self, columns: list):
        pass

    @abstractmethod
    def sort_data(self, columns: list, order_asc: bool):
        pass

    @abstractmethod
    def add_currency(self, currency: str, rate: float):
        pass

    @abstractmethod
    def set_card_brands(self, brands: list):
        pass


class JCOps(DataframeOps, ABC):
    version = 0.1

    def __init__(self, file: str, rate: float):
        jc = pd.read_csv(file, sep='|', dtype='str')

        # after seeing that last two rows are all NaN, we can get rid of them
        jc.drop(jc.tail(2).index, inplace=True)
        jc.fillna('', inplace=True)

        needed_columns = ['TRX_CODE', 'BUSINESS_TIME', 'GUEST_FULL_NAME', 'REFERENCE',
                          'CREDIT_CARD_SUPPLEMENT', 'ROOM', 'CURRENCY1',
                          'CASHIER_CREDIT', 'CASH_ID_USER_NAME']
        jc = jc[needed_columns]
        jc.columns = [column.lower() for column in jc.columns]

        convenient_col_names_dict = {'business_time': 'trx_time',
                                     'guest_full_name': 'guest_name',
                                     'reference': 'note1',
                                     'credit_card_supplement': 'note2',
                                     'currency1': 'currency',
                                     'cashier_credit': 'usd',
                                     'cash_id_user_name': 'username'
                                     }
        jc.rename(columns=convenient_col_names_dict, inplace=True)

        # working with text of columns
        columns = ['note1', 'note2', 'guest_name', 'currency']
        for column in columns:
            if column in columns[:2]:
                # make all text lowercase
                jc[column] = jc[column].apply(lambda x: x.lower() if isinstance(x, str) else x)
                # replace all POS(payment on spot) notes
                jc[column] = jc[column].replace(r'^check# 0([0-9]{6}) \[[0-9]{5}\]', r'pos \1', regex=True)
                # replace all text containing bank card numbers
                jc[column] = jc[column].replace(r'x+([0-9]{4})|(x{3,20}[a-z]*\.)', r'xx\1', regex=True)
                jc[column] = jc[column].replace(r'[\.]+([0-9]{4})', r'xx\1', regex=True)
                jc[column] = jc[column].replace(r'(xx[0-9]{4})( xx[0-9]{4}| xx$)', r'\1', regex=True)
                jc[column] = jc[column].replace(r'[ ]{2,9}([0-9]{1,2}\/[0-9]{1,2})', r' \1', regex=True)

            if column == columns[0]:
                jc[column] = jc[column].replace(r'([0-9]{1,3}),([0-9]+\.[0-9]{2,}) usd split into ', r'[\1\2=',
                                                regex=True)
                jc[column] = jc[column].replace(
                    r'([0-9]{1,3}),([0-9]+\.[0-9]{2,}) usd and ([0-9]{1,3}),([0-9]+\.[0-9]{2,}) ', r'\1\2+\3\4',
                    regex=True)
                jc[column] = jc[column].replace(r'([0-9]+)usd. ', r'\1]', regex=True)
                jc[column] = jc[column].replace(r'(\[[0-9.=+]+\])[a-z ]+([0-9.=>#]+)[a-z ]+([0-9#]+)', r'\1 \2\3',
                                                regex=True)
                jc[column] = jc[column].replace(r'[ ]+', ' ', regex=True)

            elif column == columns[1]:
                jc[column] = jc[column].replace(r'[ ]+', ' ', regex=True)

            elif column == columns[2]:
                jc[column] = jc[column].replace(r'[ ,]*(And|and)[ ,]*', r' + ', regex=True)
                jc[column] = jc[column].replace(
                    r'^(Mrs|mrs|Mr|mr)|(Mrs|mrs|Mr|mr)$|[ ,]*(Mrs|mrs|Mr|mr)|(Mrs|mrs|Mr|mr)[ ,]*$',
                    '', regex=True)
                jc[column] = jc[column].replace(r'[ +]+$', '', regex=True)

            elif column == columns[3]:
                jc[column] = jc[column].replace(r'ILS\(([0-9.]+)\)', r'\1', regex=True)

        jc['guest_name'] = jc['guest_name'].str.title()

        # now we can remove all whitespaces from our columns
        for column in columns:
            jc[column] = jc[column].apply(lambda x: x.strip())

        # add new all in one notes column
        notes = []
        for index, row in jc.iterrows():
            if row['note1'] == "" and row['note2'] == "":
                notes.append("empty")
            elif row['note1'] == "":
                notes.append(row['note2'])
            elif row['note2'] == "":
                notes.append(row['note1'])
            elif row['note1'] != row['note2']:
                notes.append(f"{row['note2']} :: {row['note1']}")
            else:
                notes.append(row['note1'])

        jc['note'] = notes

        # convert column datatype to float for future calculations
        jc['usd'] = jc['usd'].astype(float)
        jc['ils'] = jc['usd'].apply(lambda x: round(x * rate, 2))

        # convert back to str to use find function better
        jc['usd'] = jc['usd'].astype(str)

        final_columns = ['username', 'trx_code', 'trx_time', 'guest_name',
                         'note', 'room', 'currency', 'ils', 'usd']
        jc = jc[final_columns]

        self.jc = jc
        self.rate = rate

        self.jc_custom_cards = pd.DataFrame
        self.jc_custom_columns = pd.DataFrame
        self.jc_sorted = self.jc.copy()
        self.jc_w_currency = self.jc.copy()

    def set_columns(self, columns: list) -> pd.DataFrame:
        self.jc_custom_columns = self.jc.copy()
        self.jc_custom_columns = self.jc_custom_columns[columns]
        return self.jc_custom_columns

    def sort_data(self, columns: list, order_asc=False) -> pd.DataFrame:
        self.jc_sorted = self.jc_sorted.sort_values(columns, ascending=order_asc)
        return self.jc_sorted

    def add_currency(self, currency: str, rate: float) -> pd.DataFrame:
        self.jc_w_currency[currency] = self.jc_w_currency.apply(
            lambda x: round(x['usd'] * rate, 2))
        return self.jc_w_currency

    def set_card_brands(self, trx_codes: list) -> pd.DataFrame:
        self.jc_custom_cards = self.jc.copy()
        self.jc_custom_cards = self.jc_custom_cards.loc[
            self.jc_custom_cards['trx_code'].isin(trx_codes)]
        return self.jc_custom_cards

    def show_initial(self) -> pd.DataFrame:
        return self.jc

    def save(self, df: pd.DataFrame) -> str:
        self.jc = df
        return "Success!"


class PCOps(DataframeOps, ABC):
    version = 0.1

    def __init__(self, file: str, rate: float):
        pc = pd.read_excel(file, dtype='str')

        col_names_to_english = {
            'מספר מסוף': 'aaa',
            'שם עסק': 'bbb',
            'תאריך ושעה': 'trx_time',
            'מספר ריכוז': 'conc_num',
            'מספר שובר': 'voucher_num',
            'מספר כרטיס אשראי': 'card_num',
            'תוקף': 'card_exp',
            'חברה סולקת': 'ccc',
            'מותג': 'brand',
            'סוג עסקה': 'pay_way',
            'מספר אישור': 'appr_num',
            'סוג אשראי': 'trx_type',
            'סכום': 'trx_amount',
            'מטבע': 'currency',
            'מספר תשלומים': 'split_pay',
            'תשלום ראשון': 'ddd',
            'תשלום קבוע': 'eee',
            'פרטים נוספים': 'note',
            'חברה מנפיקה': 'fff',
            'ת.ז': 'guest_id',
            'מזהה עסקה': 'uid',
            'טוקן': 'token',
            'מקור כרטיס האשראי': 'iin',
            'סטאטוס': 'status',
            'קוד סטאטוס': 'status_code'
        }
        pc.rename(columns=col_names_to_english, inplace=True)

        cols_to_drop = ['aaa', 'bbb', 'voucher_num', 'card_exp', 'ccc', 'pay_way', 'trx_type',
                        'ddd', 'eee', 'fff', 'guest_id', 'uid', 'iin', 'status', 'status_code',
                        'token', 'conc_num']

        pc.drop(cols_to_drop, axis='columns', inplace=True)

        needed_columns = ['trx_amount', 'card_num', 'trx_time', 'note',
                          'currency', 'appr_num', 'split_pay', 'brand']
        pc = pc[needed_columns]

        pc.fillna('0', inplace=True)

        # replace hebrew credit card company names with english ones in column 'brand'
        pc['brand'] = pc['brand'].replace(r'מסטרכרד|מאסטרו', 'mastercard', regex=True)
        pc['brand'] = pc['brand'].replace('ויזה', 'visa')
        pc['brand'] = pc['brand'].replace('אמקס', 'visa')
        pc['brand'] = pc['brand'].replace('דיינרס', 'diners')

        # make notes lowercase for convenience
        pc['note'] = pc['note'].apply(lambda x: x.lower() if isinstance(x, str) else x)

        # some improvements in column values
        pc['trx_time'] = pc['trx_time'].replace(r'^[0-9/ ]+([0-9]{2}:[0-9]{2}):[0-9]{2}', r'\1', regex=True)
        pc['card_num'] = pc['card_num'].replace(r'^[0-9]+[*]+([0-9]{4})', r'xx\1', regex=True)
        pc['currency'] = pc['currency'].replace('$', 'USD')
        pc['currency'] = pc['currency'].replace('₪', 'ILS')
        pc['note'] = pc['note'].replace(r'([0-9]{7,}) [0-9]+', r'\1', regex=True)
        pc['note'] = pc['note'].replace(r'^b[0-9]{5,}([0-9]{3}$)', r'pos xx\1', regex=True)
        pc['note'] = pc['note'].replace(r'^�$', 'pos кракозябра', regex=True)

        for column in pc.columns:
            pc[column] = pc[column].apply(lambda x: x.strip())

        pc['split_pay'] = pc['split_pay'].astype('int8')
        pc['trx_amount'] = pc['trx_amount'].astype('float')

        pc['ils'] = pc.apply(lambda x:
                             round(x['trx_amount'], 2)
                             if x['currency'] == 'ILS'
                             else round(x['trx_amount'] * rate, 2), axis='columns')

        pc['usd'] = pc.apply(lambda x:
                             round(x['trx_amount'], 2)
                             if x['currency'] == 'USD'
                             else round(x['trx_amount'] / rate, 2), axis='columns')

        pc.drop('trx_amount', axis='columns', inplace=True)

        chosen_columns = ['usd', 'ils', 'card_num', 'trx_time', 'note',
                          'currency', 'appr_num', 'split_pay', 'brand']
        pc = pc[chosen_columns]

        self.pc = pc
        self.rate = rate

        self.pc_custom_cards = pd.DataFrame
        self.pc_custom_columns = pd.DataFrame
        self.pc_sorted = self.pc.copy()
        self.pc_w_currency = self.pc.copy()

    def set_columns(self, columns: list) -> pd.DataFrame:
        self.pc_custom_columns = self.pc.copy()
        self.pc_custom_columns = self.pc_custom_columns[columns]
        return self.pc_custom_columns

    def sort_data(self, columns: list, order_asc=False) -> pd.DataFrame:
        self.pc_sorted = self.pc_sorted.sort_values(columns, ascending=order_asc)
        return self.pc_sorted

    def add_currency(self, currency: str, rate: float) -> pd.DataFrame:
        self.pc_w_currency[currency] = (self.pc_w_currency.apply(lambda x: round(x['ils'] * rate, 2)))
        return self.pc_w_currency

    def set_card_brands(self, brands: list) -> pd.DataFrame:
        self.pc_custom_cards = self.pc.copy()
        self.pc_custom_cards = self.pc_custom_cards.loc[self.pc_custom_cards['brand'].isin(brands)]
        return self.pc_custom_cards

    def show_initial(self) -> pd.DataFrame:
        return self.pc

    def save(self, df: pd.DataFrame) -> str:
        self.pc = df
        return "Success!"
