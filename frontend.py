import pandas as pd
import streamlit as st
from variables import *
from backend import df_cards


class Inputs:
    def __init__(self):
        self.jc_file = None
        self.pc_file = None
        self.rate = None

    def jc_file_upload(self):
        st.subheader(jc_upload_subheader)
        self.jc_file = st.file_uploader(label=jc_file_uploader_label,
                                        type=jc_file_formats)

    def pc_file_upload(self):
        st.subheader(pc_upload_subheader)
        self.pc_file = st.file_uploader(label=pc_file_uploader_label,
                                        type=pc_file_formats)

    def rate_input(self):
        self.rate = st.number_input('Rate:', value=3.64, format='%.4f', step=0.01)

    def check_status(self):
        if self.pc_file and self.jc_file and self.rate:
            return True


class JCElements:
    def __init__(self):
        self.found = pd.DataFrame
        self.found_table = st.data_editor
        self.find_value_input = st.text_input
        self.find_options = st.selectbox
        self.columns_choice = st.multiselect
        self.pos_setup = st.selectbox
        self.currency = st.selectbox
        self.trx_type = st.selectbox
        self.brand = st.selectbox

    def settings(self, df: pd.DataFrame):
        brand_col, trx_type_col, currency_col, pos_col = st.columns(4)
        with brand_col:
            self.brand = st.selectbox('Brand name', options=BRANDS, key='jc_brand')
        with trx_type_col:
            self.trx_type = st.selectbox('Trx type', options=JC_TRX_TYPES)
        with currency_col:
            self.currency = st.selectbox('Currency', options=CURRENCIES, key='jc_currency')
        with pos_col:
            self.pos_setup = st.selectbox('POS / No POS', options=POS_SETUPS, key='jc_pos_setup')

        all_columns = df.columns
        self.columns_choice = st.multiselect('Set desired columns', options=all_columns,
                                             default=JC_DEFAULT_COLUMNS)

    def find_input(self):
        find_options_col, find_value_col = st.columns(2)
        with find_options_col:
            find_multiselect_options = self.columns_choice.copy()
            find_multiselect_options = list(reversed(find_multiselect_options))
            find_options_default_index = find_multiselect_options.index('note')
            self.find_options = st.selectbox('Find in column:', options=find_multiselect_options,
                                             index=find_options_default_index,
                                             help='Select a column name',
                                             label_visibility='visible')

        with find_value_col:
            self.find_value_input = st.text_input('Value:', max_chars=200,
                                                  label_visibility='visible', key='jc_find_value')

    def show_found(self, df: pd.DataFrame):
        self.found = df
        self.found_table = st.data_editor(self.found, height=2000, num_rows='dynamic',
                                          hide_index=True, disabled=False, use_container_width=True)


class PCElements:
    def __init__(self):
        self.found = pd.DataFrame
        self.found_table = st.data_editor
        self.find_value_input = st.text_input
        self.find_options = st.selectbox
        self.columns_choice = st.multiselect
        self.pos_setup = st.selectbox
        self.currency = st.selectbox
        self.brand = st.selectbox

    def settings(self, df: pd.DataFrame):
        brand_col, currency_col, pos_col = st.columns(3)
        with brand_col:
            self.brand = st.selectbox('Brand name', options=BRANDS, key='pc_brand')
        with currency_col:
            self.currency = st.selectbox('Currency', options=CURRENCIES, key='pc_currency')
        with pos_col:
            self.pos_setup = st.selectbox('POS / No POS', options=POS_SETUPS, key='pc_pos_setup')

        all_columns = df.columns
        self.columns_choice = st.multiselect('Set desired columns', options=all_columns,
                                             default=PC_DEFAULT_COLUMNS)

    def find_input(self):
        find_options_col, find_value_col = st.columns(2)
        with find_options_col:
            find_multiselect_options = self.columns_choice.copy()
            find_options_default_index = find_multiselect_options.index('card_num')
            self.find_options = st.selectbox('Find in column:', options=find_multiselect_options,
                                             index=find_options_default_index,
                                             help='Select a column name',
                                             label_visibility='visible')

        with find_value_col:
            self.find_value_input = st.text_input('Value:', max_chars=200, label_visibility='visible',
                                                  key='pc_find_value')

    def show_found(self, df: pd.DataFrame):
        self.found = df
        self.found_table = st.data_editor(self.found, height=2000, num_rows='dynamic',
                                          hide_index=True, disabled=False, use_container_width=True)


inputs = Inputs()
jc_elems = JCElements()
pc_elems = PCElements()

