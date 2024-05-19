import streamlit as st
from backend import JCOps, PCOps
from opera_trx_codes.trx_codes_extractor import trx_codes

# create dataframe with transaction code for bank cards
# that we will use to operate with journal by credit card
df_cards = trx_codes.cards

# page properties for streamlit
st.set_page_config(layout='wide', page_title="Credit Card Reconciliation")

st.subheader("Credit card reconciliation")

tabs = ["Input Data", "Tables", "Search Data"]

input_tab, tables_tab, search_tab = st.tabs(tabs=tabs)

with input_tab:
    jc_file_col, pc_file_col = st.columns(2)
    with jc_file_col:
        jc_file_formats = ['txt', 'csv']
        jc_file_uploader_label = 'Opera\'s Journal by Credit Card file:'

        jc_file = st.file_uploader(label=jc_file_uploader_label,
                                   type=jc_file_formats)

    with pc_file_col:
        pc_file_formats = ['xlsx', 'xls', 'xlsm']
        pc_file_uploader_label = 'Pele card report\' MS Excel file:'

        pc_file = st.file_uploader(label=pc_file_uploader_label,
                                   type=pc_file_formats)

    rate_col, empty1_col, empty2_col = st.columns(3)
    with rate_col:
        rate = st.number_input('Rate:', value=3.6, format='%.4f', step=0.01)

    file_upload_status = False
    file_upload_warning_txt = st.warning('Upload files and set the rate first')
    if not all([pc_file, jc_file, rate]):
        st.warning(file_upload_warning_txt)
    else:
        file_upload_status = True

with tables_tab:
    if file_upload_status:
        jc = JCOps(jc_file, rate)
        pc = PCOps(pc_file, rate)
    else:
        st.warning(file_upload_warning_txt)

    brand_col, currency_col, pos_col = st.columns(3)



















