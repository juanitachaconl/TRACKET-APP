# 📚 Tracker de Lectura

Aplicación sencilla en **Streamlit** para registrar y visualizar hábitos de lectura.  
Permite guardar registros en CSV, editarlos, generar métricas rápidas, gráficas por momento del día (AM/PM) y un mapa de calor que relaciona páginas leídas con emociones.

---

## ✨ Funcionalidades

- **Registro exprés (1 min)**:  
  - Fecha (por defecto hoy, editable).  
  - Libro (se recuerda automáticamente el último).  
  - Páginas y minutos leídos.  
  - Estado de ánimo y momento (AM/PM).  
  - Notas opcionales.  

- **Dashboard interactivo**:  
  - KPIs: total de páginas, días con hábito, meses aproximados, promedio páginas/día, libros distintos.  
  - Gráficas de progreso **AM vs PM** (línea por día).  
  - Heatmap **Emoción vs Momento** con suma de páginas.  

- **Edición de registros**:  
  - Seleccionar un registro pasado y modificar cualquiera de sus campos.  
  - Cambios se guardan y refrescan automáticamente.  

- **Descarga de datos**:  
  - Exportar el historial completo como `reading_log.csv`.  

---

## 🛠️ Instalación

Clona el repositorio y entra a la carpeta:

```bash
git clone <https://github.com/juanitachaconl/TRACKET-APP/edit/main>
cd TRACKET-APP
