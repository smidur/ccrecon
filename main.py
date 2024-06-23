import streamlit as st
from backend import JCOps, PCOps
from frontend import inputs, jc_elems, pc_elems
from variables import file_upload_warning_txt

# page properties for streamlit
st.set_page_config(layout='wide', page_title="Credit Card Reconciliation")

st.header("Credit card reconciliation")

tabs = ["Input Data", "Tables", "Search Data"]
input_tab, tables_tab, search_tab = st.tabs(tabs=tabs)
with input_tab:
    jc_file_col, pc_file_col = st.columns(2)
    with jc_file_col:
        inputs.jc_file_upload()

    with pc_file_col:
        inputs.pc_file_upload()

    rate_col, empty1_col, empty2_col = st.columns(3)
    with rate_col:
        inputs.rate_input()

    if inputs.check_status():
        jc_obj = JCOps()
        jc_obj.set_inputs(inputs.jc_file, inputs.rate)
        pc_obj = PCOps()
        pc_obj.set_inputs(inputs.pc_file, inputs.rate)

        jc_settings, pc_settings = st.columns(2)
        with jc_settings:
            jc_elems.settings(jc_obj.jc)

        with pc_settings:
            pc_elems.settings(pc_obj.pc)

inputs_status = inputs.check_status()

with tables_tab:
    if inputs_status:
        jc_table_col, pc_table_col = st.columns(2)
        with jc_table_col:
            jc_table = st.data_editor(jc_obj.set_columns(jc_elems.columns_choice),
                                      height=2000, num_rows='dynamic',
                                      hide_index=True, disabled=False, use_container_width=True)

        with pc_table_col:
            pc_table = st.data_editor(pc_obj.set_columns(pc_elems.columns_choice),
                                      height=2000, num_rows='dynamic',
                                      hide_index=True, disabled=False, use_container_width=True)
    else:
        st.warning(file_upload_warning_txt)

with search_tab:
    if inputs_status:
        st.subheader('Search')
        st.write('Specify column and value(s) to look for them in tables')
        jc_find_col, pc_find_col = st.columns(2)
        with jc_find_col:
            jc_elems.find_input()

        with pc_find_col:
            pc_elems.find_input()
    else:
        st.warning(file_upload_warning_txt)


