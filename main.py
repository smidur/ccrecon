import streamlit as st
from backend import JCOps, PCOps
from opera_trx_codes.trx_codes_extractor import trx_codes

# page properties for streamlit
st.set_page_config(layout='wide', page_title="Credit Card Reconciliation")

st.header("Credit card reconciliation")

tabs = ["Input Data", "Tables", "Search Data"]
input_tab, tables_tab, search_tab = st.tabs(tabs=tabs)
with input_tab:
    jc_file_col, pc_file_col = st.columns(2)
    with jc_file_col:
        st.subheader('**Opera table properties**')
        jc_file_formats = ['txt', ]
        jc_file_uploader_label = 'Opera\'s Journal by Credit Card file:'

        jc_file = st.file_uploader(label=jc_file_uploader_label,
                                   type=jc_file_formats)

    with pc_file_col:
        st.subheader('**Pelecard table properties**')
        pc_file_formats = ['xlsx', ]
        pc_file_uploader_label = 'PeleCard report MS Excel file:'

        pc_file = st.file_uploader(label=pc_file_uploader_label,
                                   type=pc_file_formats)

    rate_col, empty1_col, empty2_col = st.columns(3)
    with rate_col:
        rate = st.number_input('Rate:', value=3.64, format='%.4f', step=0.01)

    file_upload_status = False
    file_upload_warning_txt = '**⚠️ Upload files and set the rate first**'

    if jc_file and pc_file and rate:
        file_upload_status = True
    else:
        st.warning(file_upload_warning_txt)

    if file_upload_status:
        jc_obj = JCOps(jc_file, rate)
        pc_obj = PCOps(pc_file, rate)

        jc_settings, pc_settings = st.columns(2)
        with jc_settings:

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

            jc_all_columns = jc_obj.jc.columns
            jc_default_columns = ['trx_time', 'guest_name', 'note',
                                  'room', 'currency', 'ils', 'usd']
            jc_columns_choice = st.multiselect('Set desired columns', options=jc_all_columns,
                                               default=jc_default_columns)

        with pc_settings:
            pc_brand_col, pc_currency_col, pc_pos_col = st.columns(3)
            with pc_brand_col:
                pc_brand = st.selectbox('Brand name', options=BRANDS, key='pc_brand')
            with pc_currency_col:
                pc_currency = st.selectbox('Currency', options=CURRENCIES, key='pc_currency')
            with pc_pos_col:
                pc_pos_setup = st.selectbox('POS / No POS', options=POS_SETUPS, key='pc_pos_setup')

            pc_all_columns = pc_obj.pc.columns
            pc_default_columns = ['usd', 'ils', 'card_num', 'trx_time',
                                  'note', 'currency', 'appr_num']
            pc_columns_choice = st.multiselect('Set desired columns', options=pc_all_columns,
                                               default=pc_default_columns)

with tables_tab:
    if file_upload_status:
        jc_table_col, pc_table_col = st.columns(2)
        with jc_table_col:
            jc_table = st.data_editor(jc_obj.set_columns(jc_columns_choice), height=2000, num_rows='dynamic',
                                      hide_index=True, disabled=False, use_container_width=True)

        with pc_table_col:
            pc_table = st.data_editor(pc_obj.set_columns(pc_columns_choice), height=2000, num_rows='dynamic',
                                      hide_index=True, disabled=False, use_container_width=True)

with search_tab:
    if file_upload_status:
        st.subheader('Search')
        st.write('Specify column and value(s) to look for them in tables')
        jc_find_col, pc_find_col = st.columns(2)
        with jc_find_col:
            jc_find_options_col, jc_find_value_col = st.columns(2)
            with jc_find_options_col:
                jc_find_multiselect_options = jc_columns_choice.copy()
                jc_find_multiselect_options = list(reversed(jc_find_multiselect_options))
                jc_find_options_default_index = jc_find_multiselect_options.index('note')
                jc_find_options = st.selectbox('Find in column:', options=jc_find_multiselect_options,
                                               index=jc_find_options_default_index,
                                               help='Select a column name',
                                               label_visibility='visible')

            with jc_find_value_col:
                jc_find_value_input = st.text_input('Value:', max_chars=200,
                                                    label_visibility='visible', key='jc_find_value')

        with pc_find_col:
            pc_find_options_col, pc_find_value_col = st.columns(2)
            with pc_find_options_col:
                pc_find_multiselect_options = pc_columns_choice.copy()
                pc_find_options_default_index = pc_find_multiselect_options.index('card_num')
                pc_find_options = st.selectbox('Find in column:', options=pc_find_multiselect_options,
                                               index=pc_find_options_default_index,
                                               help='Select a column name',
                                               label_visibility='visible')

            with pc_find_value_col:
                pc_find_value_input = st.text_input('Value:', max_chars=200, label_visibility='visible',
                                                    key='pc_find_value')

        jc_found_col, pc_found_col = st.columns(2)
        with jc_found_col:
            jc_found_table = st.data_editor(find_value(jc_obj.jc, jc_find_options, jc_find_value_input),
                                            height=2000, num_rows='dynamic',
                                            hide_index=True, disabled=False, use_container_width=True)
        with pc_found_col:
            pc_found_table = st.data_editor(find_value(pc_obj.pc, pc_find_options, pc_find_value_input),
                                            height=2000, num_rows='dynamic',
                                            hide_index=True, disabled=False, use_container_width=True)

