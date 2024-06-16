BRANDS = ['Visa', 'MasterCard', 'AmEx', 'Diners']
CURRENCIES = ['USD', 'ILS']
POS_SETUPS = ['With POS', 'Without POS']
JC_DEFAULT_COLUMNS = ['trx_time', 'guest_name', 'note',
                      'room', 'currency', 'ils', 'usd']
PC_DEFAULT_COLUMNS = ['usd', 'ils', 'card_num', 'trx_time',
                      'note', 'currency', 'appr_num']

JC_TRX_TYPES = ['Online + Offline', 'Online', 'Offline']

file_upload_warning_txt = '**⚠️ Upload files and set the rate first**'

jc_upload_subheader = '**Opera table properties**'
jc_file_formats = ['txt', ]
jc_file_uploader_label = 'Opera\'s Journal by Credit Card file:'

pc_upload_subheader = '**Pelecard table properties**'
pc_file_formats = ['xlsx', ]
pc_file_uploader_label = 'PeleCard report MS Excel file:'
