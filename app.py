import os
import io
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import date

CSV_PATH = "reading_log.csv"

st.set_page_config(page_title="Tracker de Lectura", page_icon="📚", layout="centered")
st.markdown("# 📚 Tracker de Lectura")
st.caption("Registra tu lectura en 1 minuto. Guarda en CSV y edita")

# --- utils ---
def load_csv():
    cols = ["Fecha","Libro","Páginas","Minutos","Ánimo","Momento","Notas"]
    if not os.path.exists(CSV_PATH):
        return pd.DataFrame(columns=cols)
    try:
        df = pd.read_csv(CSV_PATH)
    except Exception:
        return pd.DataFrame(columns=cols)

    for c in cols:
        if c not in df.columns:
            df[c] = "" if c in ["Libro","Ánimo","Momento","Notas","Fecha"] else 0
    return df[cols]

def save_csv(df):
    df.to_csv(CSV_PATH, index=False, encoding="utf-8")

def save_current_book(book):
    if not book:
        return
    with open(".last_book.txt","w",encoding="utf-8") as f:
        f.write(book)

def load_current_book():
    try:
        with open(".last_book.txt","r",encoding="utf-8") as f:
            return f.read().strip()
    except Exception:
        return ""

# --- formulario exprés (nuevo registro) ---
st.markdown("## ➕ Nuevo registro")
colA, colB = st.columns(2)
with colA:
    fecha = st.date_input("Fecha", value=date.today())
with colB:
    default_book = load_current_book()
    libro = st.text_input("Libro", value=default_book, placeholder="Título del libro")

col1, col2 = st.columns(2)
with col1:
    paginas = st.number_input("Páginas leídas", min_value=0, step=1, value=0)
with col2:
    minutos = st.number_input("Minutos", min_value=0, step=5, value=0)

col3, col4 = st.columns(2)
with col3:
    animo = st.selectbox("Ánimo", ["Enfocada","Relajada","Cansada","Apurada","Neutral","Ansiosa","Enojada","Triste"], index=0)

momento = st.radio("¿Fue en la mañana o tarde?", ["AM","PM"], horizontal=True)
notas = st.text_area("Notas (opcional)", placeholder="Highlights, ideas, citas...")

if st.button("✅ Guardar registro", use_container_width=True):
    if not libro:
        st.error("Escribe el nombre del libro.")
    elif paginas <= 0 and minutos <= 0:
        st.error("Ingresa al menos páginas o minutos.")
    else:
        df = load_csv()
        new_row = {
            "Fecha": str(fecha),
            "Libro": libro.strip(),
            "Páginas": int(paginas),
            "Minutos": int(minutos),
            "Ánimo": animo,
            "Momento": momento,
            "Notas": notas.strip(),
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        save_csv(df)
        save_current_book(libro.strip())
        st.success("Registro guardado en reading_log.csv")
        st.rerun()

# --- dashboard ---
st.markdown("## 📊 Dashboard")
df = load_csv()

if df.empty:
    st.info("Aún no hay registros.")
else:
    try:
        # KPIs
        dias_habito = df["Fecha"].nunique()
        meses_habito = round(dias_habito/30, 1)
        prom_paginas = round(pd.to_numeric(df["Páginas"], errors="coerce").fillna(0).sum()/dias_habito, 1) if dias_habito>0 else 0
        libros_leidos = df["Libro"].nunique()

        colK1, colK2, colK3, colK4, colK5 = st.columns(5)
        with colK1: st.metric("Total páginas", int(pd.to_numeric(df["Páginas"], errors="coerce").fillna(0).sum()))
        with colK2: st.metric("Días con hábito", dias_habito)
        with colK3: st.metric("≈ Meses", meses_habito)
        with colK4: st.metric("Prom. páginas/día", prom_paginas)
        with colK5: st.metric("Libros distintos", libros_leidos)

        # --- Gráficas AM vs PM ---
        dfx = df.copy()
        dfx["Fecha"] = pd.to_datetime(dfx["Fecha"], errors="coerce")
        dfx["Páginas"] = pd.to_numeric(dfx["Páginas"], errors="coerce").fillna(0).astype(int)
        daily = dfx.dropna(subset=["Fecha"]).groupby(["Fecha","Momento"])["Páginas"].sum().unstack().fillna(0)

        if not daily.empty:
            st.markdown("### Progreso por día (AM vs PM)")
            colG1, colG2 = st.columns(2)

            with colG1:
                if "AM" in daily:
                    fig1, ax1 = plt.subplots()
                    daily["AM"].plot(marker="o", ax=ax1, title="Lecturas AM")
                    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%d-%m"))
                    plt.xticks(rotation=45)
                    st.pyplot(fig1)

            with colG2:
                if "PM" in daily:
                    fig2, ax2 = plt.subplots()
                    daily["PM"].plot(marker="o", ax=ax2, title="Lecturas PM", color="orange")
                    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%d-%m"))
                    plt.xticks(rotation=45)
                    st.pyplot(fig2)

    except Exception as e:
        st.error(f"No se pudo generar dashboard: {e}")

# --- Heatmap Emoción vs Momento ---
st.markdown("### 🔥 Heatmap: Emoción vs Momento (suma de páginas)")
try:
    if not df.empty:
        dfx = df.copy()
        dfx["Páginas"] = pd.to_numeric(dfx["Páginas"], errors="coerce").fillna(0).astype(int)

        tabla_cross = dfx.pivot_table(
            values="Páginas",
            index="Ánimo",
            columns="Momento",
            aggfunc="sum",
            fill_value=0
        )

        if not tabla_cross.empty:
            fig, ax = plt.subplots(figsize=(5,4))
            cax = ax.imshow(tabla_cross.values, cmap="YlOrRd", aspect="auto")

            ax.set_xticks(range(len(tabla_cross.columns)))
            ax.set_xticklabels(tabla_cross.columns)
            ax.set_yticks(range(len(tabla_cross.index)))
            ax.set_yticklabels(tabla_cross.index)

            for i in range(len(tabla_cross.index)):
                for j in range(len(tabla_cross.columns)):
                    ax.text(j, i, int(tabla_cross.values[i, j]),
                            ha="center", va="center", color="black", fontsize=9)

            fig.colorbar(cax, ax=ax, label="Páginas")
            ax.set_title("Páginas leídas por emoción y momento (AM/PM)")
            st.pyplot(fig)
except Exception as e:
    st.error(f"No se pudo generar el heatmap: {e}")

# --- editar registros ---
st.markdown("## ✏️ Editar registro existente")
if not df.empty:
    df_edit = df.copy().reset_index(drop=True)
    df_edit["ID"] = df_edit.index.astype(str) + " | " + df_edit["Fecha"].astype(str) + " | " + df_edit["Libro"].astype(str)

    selected = st.selectbox("Selecciona un registro para editar", options=df_edit["ID"])

    if selected:
        idx = int(selected.split(" | ")[0])
        registro = df_edit.loc[idx]

        # validación de fecha segura
        try:
            fecha_val = pd.to_datetime(registro["Fecha"]).date()
        except Exception:
            fecha_val = date.today()

        fecha_edit = st.date_input("Fecha", value=fecha_val, key=f"edit_fecha_{idx}")
        libro_edit = st.text_input("Libro", value=str(registro["Libro"]), key=f"edit_libro_{idx}")
        paginas_edit = st.number_input("Páginas", min_value=0, value=int(registro["Páginas"]) if pd.notnull(registro["Páginas"]) else 0, key=f"edit_paginas_{idx}")
        minutos_edit = st.number_input("Minutos", min_value=0, value=int(registro["Minutos"]) if pd.notnull(registro["Minutos"]) else 0, key=f"edit_minutos_{idx}")

        emociones = ["Enfocada","Relajada","Cansada","Apurada","Neutral","Ansiosa","Enojada","Triste"]
        if registro["Ánimo"] not in emociones:
            emociones.append(registro["Ánimo"])
        animo_edit = st.selectbox("Ánimo", emociones,
                                  index=emociones.index(registro["Ánimo"]) if registro["Ánimo"] in emociones else 0,
                                  key=f"edit_animo_{idx}")

        momento_edit = st.radio("Momento", ["AM","PM"],
                                index=0 if registro["Momento"]=="AM" else 1,
                                horizontal=True, key=f"edit_momento_{idx}")
        notas_edit = st.text_area("Notas", value=str(registro["Notas"]), key=f"edit_notas_{idx}")

        if st.button("💾 Guardar cambios", use_container_width=True, key=f"save_{idx}"):
            df.loc[idx, ["Fecha","Libro","Páginas","Minutos","Ánimo","Momento","Notas"]] = [
                str(fecha_edit), libro_edit.strip(), paginas_edit, minutos_edit,
                animo_edit, momento_edit, notas_edit.strip()
            ]
            save_csv(df)
            st.success("Registro actualizado")
            st.rerun()

# --- tabla al final ---
st.markdown("## 📋 Registros")
if not df.empty:
    st.dataframe(df.sort_values("Fecha", ascending=False), use_container_width=True)

# --- descarga CSV ---
st.markdown("## ⬇️ Descargar tu CSV")
if not df.empty:
    buf = io.StringIO()
    df.to_csv(buf, index=False, encoding="utf-8")
    st.download_button(
        "Descargar reading_log.csv",
        data=buf.getvalue(),
        file_name="reading_log.csv",
        mime="text/csv",
        use_container_width=True
    )
else:
    st.caption("Cuando registres tu primera lectura, podrás descargar el CSV aquí.")
##streamlit run app.py
