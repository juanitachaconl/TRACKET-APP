
# 📚 Tracker de Lectura (Python + Streamlit + Notion)

Una app web sencilla y bonita para registrar tu progreso de lectura desde **celular, tablet o computador**. 
- ✅ Interface web (URL compartible)
- ✅ Sincroniza con **Notion** (opcional)
- ✅ Dashboard rápido con métricas y gráfico
- ✅ Fallback local a CSV si Notion no está configurado

## 1) Requisitos
- Python 3.10+
- Cuenta de Notion (opcional pero recomendado)

## 2) Clonar y correr local
```bash
pip install -r requirements.txt
streamlit run app.py
```
Se abrirá en tu navegador en `http://localhost:8501`.

## 3) Conectar con Notion (opcional)
1. Ve a [https://www.notion.so/my-integrations](https://www.notion.so/my-integrations) y crea una **Integration**. Copia el **Internal Integration Token**.
2. Crea una base de datos en Notion con estas **propiedades** (respeta nombres y tipos):
   - `Libro` (Title)
   - `Fecha` (Date)
   - `Páginas` (Number)
   - `Minutos` (Number)
   - `Estado` (Select) — opciones sugeridas: *Leyendo*, *Terminado*, *Releyendo*, *Abandonado*
   - `Ánimo` (Select) — opciones sugeridas: *Enfocada*, *Relajada*, *Cansada*, *Apurada*, *Neutral*
3. Abre el menú de la base de datos → **Add connections** → agrega tu Integration.
4. Copia el `database_id` de la URL de tu base de datos (la parte larga tipo `abc123...`).

### Añadir secretos
En local puedes exportar variables o crear un archivo `.streamlit/secrets.toml`:
```toml
NOTION_TOKEN="tu_token_notion"
NOTION_DB_ID="tu_database_id"
```

## 4) Desplegar gratis con Streamlit Community Cloud
1. Sube este repo a GitHub.
2. Entra a [share.streamlit.io](https://share.streamlit.io/) e inicia sesión.
3. Elige tu repo y `app.py` como entrypoint.
4. En *Advanced settings → Secrets* pega:
```
NOTION_TOKEN="tu_token_notion"
NOTION_DB_ID="tu_database_id"
```
¡Listo! Tendrás una **URL pública** para usar desde el celular/tablet/PC.

## 5) Alternativas de despliegue
- **Render** o **Railway** con `Flask`/`FastAPI` si quieres una API real.
- **Cloud Run** (GCP) o **Fly.io** para más control.
- **Hugging Face Spaces** con la misma app de Streamlit.

## 6) Personalización rápida
- Cambia los campos del formulario en `app.py` según lo que quieras trackear (e.g., capítulos, formato, idioma).
- Agrega más gráficos en la sección *Dashboard* (usa `matplotlib`).

## 7) Seguridad
- Nunca subas tu `NOTION_TOKEN` al repo. Usa **secrets**.
- Si la URL es pública, cualquiera que acceda podrá escribir. Streamlit Community Cloud permite proteger con **password** en `st.secrets` si lo deseas (ej: `APP_PASSWORD`).

---

Hecho con ❤️ para que vuelvas a disfrutar tus hábitos de lectura.
