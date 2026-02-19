# Beneficios Automáticos (Entel, Movistar, Bci, Caja 18)
- Raspa catálogos **públicos** de beneficios y los sube a **Google Sheets**.
- Envío por correo (Apps Script) el día **1** de cada mes.

## Requisitos
- Secret `GOOGLE_SERVICE_ACCOUNT_JSON` (contenido **completo** del JSON de Service Account).
- Secret `SHEET_ID` (ID de Google Sheet).
- La Sheet compartida con el Service Account (rol Editor).

## Probar manualmente
- Actions → selecciona el workflow → **Run workflow**.
