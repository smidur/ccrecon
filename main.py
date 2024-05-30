import pandas as pd
import streamlit as st
from backend import JCOps, PCOps, find_value
from opera_trx_codes.trx_codes_extractor import trx_codes

# create dataframe with transaction code for bank cards
# that we will use to operate with journal by credit card
df_cards = trx_codes.cards

BRANDS = ['Visa', 'MasterCard', 'AmEx', 'Diners']
CURRENCIES = ['USD', 'ILS']
POS_SETUPS = ['With POS', 'Without POS']

# page properties for streamlit
st.set_page_config(layout='wide', page_title="Credit Card Reconciliation")

st.header("Credit card reconciliation")

tabs = ["Input Data", "Tables", "Search Data"]
input_tab, tables_tab, search_tab = st.tabs(tabs=tabs)
with input_tab:
    jc_file_col, pc_file_col = st.columns(2)
    with jc_file_col:
        jc_file_formats = ['txt', ]
        jc_file_uploader_label = 'Opera\'s Journal by Credit Card file:'

        jc_file = st.file_uploader(label=jc_file_uploader_label,
                                   type=jc_file_formats)

    with pc_file_col:
        pc_file_formats = ['xlsx', ]
        pc_file_uploader_label = 'PeleCard report MS Excel file:'

        pc_file = st.file_uploader(label=pc_file_uploader_label,
                                   type=pc_file_formats)

    rate_col, empty1_col, empty2_col = st.columns(3)
    with rate_col:
        rate = st.number_input('Rate:', value=3.64, format='%.4f', step=0.01)

    file_upload_status = True
    file_upload_warning_txt = '**⚠️ Upload files and set the rate first**'
    # if all([jc_file, pc_file, rate]):
    #     file_upload_status = True
    # else:
    #     st.warning(file_upload_warning_txt)

with tables_tab:
    if not file_upload_status:
        st.warning(file_upload_warning_txt)
    else:
        jc = JCOps('20240427_jc.txt', rate)
        pc = PCOps('20240427_pc.xlsx', rate)

        with st.expander('**Tables\' Properties**', expanded=True):
            with st.form(key='properties_form'):
                jc_settings, pc_settings = st.columns(2)
                with jc_settings:
                    st.subheader('**Journal by CC table properties**')

                    jc_brand_col, jc_trx_type_col, jc_currency_col, jc_pos_col = st.columns(4)
                    with jc_brand_col:
                        jc_brand = st.selectbox('Brand name', options=BRANDS, key='jc_brand')
                    with jc_trx_type_col:
                        jc_trx_types = ['Online + Offline', 'Online', 'Offline']
                        jc_trx_type = st.selectbox('Trx type', options=jc_trx_types)
                    with jc_currency_col:
                        jc_currency = st.selectbox('Currency', options=CURRENCIES, key='jc_currency')
                    with jc_pos_col:
                        jc_pos_setup = st.selectbox('POS / No POS', options=POS_SETUPS, key='jc_pos_setup')

                    jc_all_columns = jc.jc.columns
                    jc_default_columns = ['trx_time', 'guest_name', 'note',
                                          'room', 'currency', 'ils', 'usd']
                    jc_columns_choice = st.multiselect('Set desired columns', options=jc_all_columns,
                                                       default=jc_default_columns)

                with pc_settings:
                    st.subheader('**Pele card table properties**')

                    pc_brand_col, pc_currency_col, pc_pos_col = st.columns(3)
                    with pc_brand_col:
                        pc_brand = st.selectbox('Brand name', options=BRANDS, key='pc_brand')
                    with pc_currency_col:
                        pc_currency = st.selectbox('Currency', options=CURRENCIES, key='pc_currency')
                    with pc_pos_col:
                        pc_pos_setup = st.selectbox('POS / No POS', options=POS_SETUPS, key='pc_pos_setup')

                    pc_all_columns = pc.pc.columns
                    pc_default_columns = ['usd', 'ils', 'card_num', 'trx_time',
                                          'note', 'currency', 'appr_num']
                    pc_columns_choice = st.multiselect('Set desired columns', options=pc_all_columns,
                                                       default=pc_default_columns)

                apply_button = st.form_submit_button('APPLY', use_container_width=True)

        with st.form(key='find_form'):
            jc_find_col, pc_find_col = st.columns(2)

            find_options_col, find_value_col, find_reset_button_col = st.columns([7, 10, 1])
            with find_options_col:
                find_multiselect_options = jc_columns_choice.copy()
                find_multiselect_options.insert(0, 'all')
                find_options = st.selectbox('Find in column:', options=jc_columns_choice, label_visibility='visible')

            with find_value_col:
                find_value_input = st.text_input('Value:', max_chars=200, label_visibility='visible', key='find_value')

            with find_reset_button_col:
                st.write('')
                st.write('')
                find_reset_button = st.form_submit_button('RESET')

            find_submit_button = st.form_submit_button('FIND', use_container_width=True)

        if find_reset_button:
            find_submit_button = False
            reset_find_button = False

        jc_table_col, pc_table_col = st.columns(2)
        with jc_table_col:
            if find_submit_button and find_options not in [None, '']:
                jc_table: object = find_value(df=jc.jc, column_name=find_options, value=find_value_input)
                discovered = st.data_editor(jc_table, height=2000, num_rows='dynamic',
                                            hide_index=True, disabled=False, use_container_width=True)
            else:
                jc_table = st.data_editor(jc.set_columns(jc_columns_choice), height=2000, num_rows='dynamic',
                                          hide_index=True, disabled=False, use_container_width=True)

        with pc_table_col:
            pc_table = st.data_editor(pc.set_columns(pc_columns_choice), height=2000, num_rows='dynamic',
                                      hide_index=True, disabled=False, use_container_width=True)
