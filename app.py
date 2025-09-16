
import os
import time
import requests
import pandas as pd
import streamlit as st

NOTION_TOKEN = st.secrets.get("NOTION_TOKEN", os.getenv("NOTION_TOKEN", ""))
NOTION_DB_ID = st.secrets.get("NOTION_DB_ID", os.getenv("NOTION_DB_ID", ""))

NOTION_VERSION = "2022-06-28"
NOTION_HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": NOTION_VERSION,
    "Content-Type": "application/json"
}

LOCAL_CSV = "reading_log.csv"

st.set_page_config(page_title="Lectura • Tracker", page_icon="📚", layout="centered")

st.markdown("# 📚 Tracker de Lectura")
st.caption("Registra tu progreso en cualquier dispositivo. Si configuras Notion, los datos se guardan en tu base de datos.")

with st.expander("🔧 Estado de conexión"):
    if NOTION_TOKEN and NOTION_DB_ID:
        st.success("Conectado a Notion (usa los secretos `NOTION_TOKEN` y `NOTION_DB_ID`).")
    else:
        st.warning("Sin conexión a Notion. Guardaré localmente en `reading_log.csv`. Agrega secretos para sincronizar.")

def create_notion_page(data):
    if not (NOTION_TOKEN and NOTION_DB_ID):
        return {"ok": False, "msg": "Notion no configurado; usando CSV local."}

    # Notion properties mapping — deben existir en tu DB
    payload = {
        "parent": {"database_id": NOTION_DB_ID},
        "properties": {
            "Fecha": {"date": {"start": data["date"]}},
            "Libro": {"title": [{"text": {"content": data["book"]}}]},
            "Páginas": {"number": data["pages"]},
            "Minutos": {"number": data["minutes"]},
            "Estado": {"select": {"name": data["status"]}},
            "Ánimo": {"select": {"name": data["mood"]}},
        },
        "children": [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {"rich_text": [{"type": "text", "text": {"content": data["notes"] or ""}}]}
            }
        ]
    }
    try:
        r = requests.post("https://api.notion.com/v1/pages", headers=NOTION_HEADERS, json=payload, timeout=20)
        if r.status_code in (200, 201):
            return {"ok": True, "msg": "Guardado en Notion ✅"}
        else:
            return {"ok": False, "msg": f"Error Notion {r.status_code}: {r.text[:200]}"}
    except Exception as e:
        return {"ok": False, "msg": f"Excepción Notion: {e}"}

def notion_query(limit=50):
    if not (NOTION_TOKEN and NOTION_DB_ID):
        return []
    try:
        r = requests.post(f"https://api.notion.com/v1/databases/{NOTION_DB_ID}/query",
                          headers=NOTION_HEADERS, json={"page_size": limit}, timeout=20)
        r.raise_for_status()
        return r.json().get("results", [])
    except Exception:
        return []

with st.form("entry"):
    col1, col2 = st.columns(2)
    with col1:
        book = st.text_input("Libro", placeholder="Título del libro", help="Ej: 'Thinking, Fast and Slow'")
        date = st.date_input("Fecha")
        pages = st.number_input("Páginas leídas", min_value=0, step=1)
    with col2:
        minutes = st.number_input("Minutos", min_value=0, step=5)
        status = st.selectbox("Estado", ["Leyendo", "Terminado", "Releyendo", "Abandonado"])
        mood = st.selectbox("Ánimo", ["Enfocada", "Relajada", "Cansada", "Apurada", "Neutral"])
    notes = st.text_area("Notas (opcional)", placeholder="Qué aprendiste / highlights / citas...")

    submitted = st.form_submit_button("➕ Registrar")

if submitted:
    if not book:
        st.error("Pon al menos el nombre del libro.")
    else:
        row = {
            "date": str(date),
            "book": book.strip(),
            "pages": int(pages),
            "minutes": int(minutes),
            "status": status,
            "mood": mood,
            "notes": notes.strip()
        }
        # Try Notion
        res = create_notion_page(row)
        if not res["ok"]:
            # Fallback local CSV
            exists = os.path.exists(LOCAL_CSV)
            df = pd.DataFrame([row])
            if exists:
                df.to_csv(LOCAL_CSV, mode="a", header=False, index=False, encoding="utf-8")
            else:
                df.to_csv(LOCAL_CSV, index=False, encoding="utf-8")
            st.info(res["msg"] + " También guardado en CSV local.")
        else:
            st.success(res["msg"])

st.markdown("## 📈 Dashboard rápido")
# Build dataframe from Notion or CSV
def load_df():
    # Try Notion first
    results = notion_query(limit=200)
    rows = []
    if results:
        for r in results:
            props = r.get("properties", {})
            def g(p, t, default=None):
                try:
                    if t == "title":
                        return props[p]["title"][0]["plain_text"]
                    if t == "date":
                        return props[p]["date"]["start"]
                    if t == "number":
                        return props[p]["number"]
                    if t == "select":
                        return props[p]["select"]["name"]
                except Exception:
                    return default
            rows.append({
                "Fecha": g("Fecha", "date", ""),
                "Libro": g("Libro", "title", ""),
                "Páginas": g("Páginas", "number", 0),
                "Minutos": g("Minutos", "number", 0),
                "Estado": g("Estado", "select", ""),
                "Ánimo": g("Ánimo", "select", ""),
            })
        if rows:
            return pd.DataFrame(rows)
    # Fallback CSV
    if os.path.exists(LOCAL_CSV):
        df = pd.read_csv(LOCAL_CSV)
        df.rename(columns={"date":"Fecha","book":"Libro","pages":"Páginas","minutes":"Minutos",
                           "status":"Estado","mood":"Ánimo"}, inplace=True)
        return df
    return pd.DataFrame(columns=["Fecha","Libro","Páginas","Minutos","Estado","Ánimo"])

df = load_df()
if df.empty:
    st.info("Aún no hay registros.")
else:
    # Show table
    st.dataframe(df.sort_values("Fecha", ascending=False), use_container_width=True)

    # KPIs
    colA, colB, colC = st.columns(3)
    with colA:
        st.metric("Total páginas", int(df["Páginas"].fillna(0).sum()))
    with colB:
        st.metric("Total minutos", int(df["Minutos"].fillna(0).sum()))
    with colC:
        dias = df["Fecha"].nunique()
        st.metric("Días con lectura", int(dias))

    # Simple chart: pages by date
    try:
        import matplotlib.pyplot as plt
        df_plot = df.copy()
        df_plot["Fecha"] = pd.to_datetime(df_plot["Fecha"], errors="coerce")
        df_plot = df_plot.dropna(subset=["Fecha"])
        daily = df_plot.groupby("Fecha")[["Páginas","Minutos"]].sum().sort_index()
        st.markdown("### Progreso por día")
        fig = plt.figure()
        daily["Páginas"].plot(marker="o")
        st.pyplot(fig)
    except Exception as e:
        st.caption(f"No se pudo graficar: {e}")
