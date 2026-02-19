
mport os, json
import gspread
from google.oauth2.service_account import Credentials

SCOPE = ["https://www.googleapis.com/auth/spreadsheets"]

def get_client():
    key_json = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])
    creds = Credentials.from_service_account_info(key_json, scopes=SCOPE)
    return gspread.authorize(creds)

def write_rows(rows):
    sheet_id = os.environ["SHEET_ID"]
    gc = get_client()
    sh = gc.open_by_key(sheet_id)

    try:
        ws = sh.worksheet("Beneficios")
    except Exception:
        ws = sh.add_worksheet(title="Beneficios", rows=100, cols=8)

    header = ["Proveedor","Categoría","Comercio","Beneficio","Vigencia","Link","Fuente","Extraido_En"]

    # Si la hoja está vacía, crea encabezado
    if ws.row_count == 0 or ws.cell(1,1).value != header[0]:
        ws.clear()
        ws.append_row(header)

    # Limpia todo menos la cabecera
    ws.resize(rows=1)

    values = [[r.get(k,"") for k in header] for r in rows]
    if values:
        ws.append_rows(values, value_input_option="RAW")

