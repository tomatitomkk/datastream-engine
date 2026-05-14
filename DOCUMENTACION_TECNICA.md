# Documentación Técnica — AutoData Pipeline

> Sistema automatizado de extracción, transformación, generación de reportes y distribución de datos.
>
> *Arquitectura, diseño y desarrollo integral liderado por **Dylan Ramirez Lopez***

---

## Índice

1. [Arquitectura del Sistema](#1-arquitectura-del-sistema)
2. [Estructura del Proyecto](#2-estructura-del-proyecto)
3. [Módulos del Backend](#3-módulos-del-backend)
4. [API REST — Endpoints](#4-api-rest--endpoints)
5. [Automatización (APScheduler)](#5-automatización-apscheduler)
6. [Integración con el Frontend](#6-integración-con-el-frontend)
7. [Instrucciones de Instalación](#7-instrucciones-de-instalación)
8. [Uso del Sistema](#8-uso-del-sistema)
9. [Créditos y Autoría](#9-créditos-y-autoría)

---

## 1. Arquitectura del Sistema

```
                        ┌─────────────────────────────┐
                        │        NAVEGADOR            │
                        │   (Dashboard HTML/CSS/JS)   │
                        └──────────┬──────────────────┘
                                   │ HTTP (Fetch API)
                                   ▼
┌──────────────────────────────────────────────────────────┐
│                    FASTAPI (main.py)                      │
│                                                          │
│  POST /api/generate   GET /api/stats                     │
│  GET /api/reports     DELETE /api/reports/{f}            │
│                                                          │
│  ┌────────────────────────────────────────────────────┐  │
│  │  APScheduler (Cron: 0 6 * * 1-5)                  │  │
│  └──────────────────────┬─────────────────────────────┘  │
└──────────────────────────┼──────────────────────────────┘
                           │
         ┌─────────────────┼────────────────────┐
         ▼                 ▼                     ▼
┌────────────────┐ ┌──────────────┐ ┌────────────────────┐
│ data_processor │ │chart_generator│ │   pdf_generator    │
│  (Pandas/NumPy)│ │ (Matplotlib) │ │   (ReportLab)      │
└───────┬────────┘ └──────┬───────┘ └──────────┬─────────┘
        │                 │                    │
        ▼                 ▼                    ▼
   Datos sintéticos    PNG temp/           PDF en outputs/
```

### Flujo de una generación de reporte

```
POST /api/generate
  │
  ├─ 1. DataProcessor.compute_stats()
  │     └─ DataFrame sintético de 2000 registros × 7 columnas
  │     └─ Métricas: total_records, active_sources, avg_processing_ms, etc.
  │
  ├─ 2. DataProcessor.get_source_summary()
  │     └─ Agrupación por fuente: records, error_rate, avg_processing_ms
  │
  ├─ 3. DataProcessor.get_time_series()
  │     └─ Serie temporal de 30 días: records_processed, avg_processing_ms
  │
  ├─ 4. chart_generator.generate_bar_chart()
  │     └─ Gráfico de barras horizontal: registros por fuente + tasa de error
  │     └─ Se guarda en backend/temp/chart_bar_*.png
  │
  ├─ 5. chart_generator.generate_line_chart()
  │     └─ Gráfico de líneas + área: rendimiento 30 días
  │     └─ Segundo eje Y para tiempo de procesamiento
  │     └─ Se guarda en backend/temp/chart_line_*.png
  │
  ├─ 6. PDFReport.generate(stats, bar_path, line_path)
  │     └─ Página de portada con metadatos
  │     └─ Tabla de estadísticas (10 métricas)
  │     └─ Gráficos embebidos
  │     └─ Footer con atribución
  │     └─ Se guarda en backend/outputs/reporte_YYYYMMDD.pdf
  │
  ├─ 7. Limpieza de archivos temporales
  │
  └─ 8. Respuesta JSON con filename, stats, generated_at
```

### Stack tecnológico

| Componente      | Tecnología          | Propósito                         |
|-----------------|---------------------|-----------------------------------|
| Web framework   | FastAPI + Uvicorn   | API REST con docs automáticos     |
| Procesamiento   | Pandas 2.2 / NumPy  | Manipulación y estadísticas       |
| Gráficos        | Matplotlib + Seaborn| Visualizaciones profesional       |
| PDF Engine      | ReportLab 4.3       | Composición programática de PDFs  |
| Scheduler       | APScheduler 3.10    | Ejecución cron automatizada       |
| Almacenamiento  | SQLite (vía Pandas) | Portabilidad inmediata            |

---

## 2. Estructura del Proyecto

```
automatizacion_reportes/
│
├── index.html                     # Dashboard frontend (autocontenido)
├── DOCUMENTACION_TECNICA.md       # Este documento
├── requirements.txt               # Dependencias Python
│
├── backend/
│   ├── main.py                    # ★ FastAPI app, endpoints, scheduler
│   ├── config.py                  # Constantes, rutas de directorios
│   ├── data_processor.py          # Ingesta sintética, estadísticas con Pandas
│   ├── chart_generator.py         # Gráficos Matplotlib/Seaborn
│   ├── pdf_generator.py           # PDF con ReportLab
│   ├── outputs/                   # → PDFs generados aquí
│   └── temp/                      # → PNGs temporales (se limpian)
│
└── frontend/
    └── api.js                     # Funciones JS para consumir la API
```

---

## 3. Módulos del Backend

### 3.1 `config.py`

Define rutas absolutas a los directorios `outputs/` y `temp/`, la expresión Cron por defecto y el texto de atribución del footer.

### 3.2 `data_processor.py` — Ingesta y Estadísticas

**Clase `DataProcessor`:**

- `__init__()`: Genera un DataFrame sintético de 2000 registros con 7 columnas:
  - `source`: 6 fuentes simuladas (PostgreSQL CRM, MySQL ERP, REST API Clientes, etc.)
  - `record_id`: identificador único
  - `value`: valor numérico distribuido exponencialmente
  - `processing_time_ms`: tiempo de procesamiento (distribución gamma)
  - `status`: OK/WARN/ERROR con pesos realistas (70/15/10/3/2 %)
  - `source_id`: entero aleatorio
  - `timestamp`: datetime secuencial

- `compute_stats() -> dict`: Calcula 12 métricas clave incluyendo total_records, active_sources, avg_processing_ms, p95_processing_ms, uptime (99.97%), total_executions (2472).

- `get_source_summary() -> pd.DataFrame`: Agrupación por fuente con records, avg_processing_ms, error_rate.

- `get_time_series(n_points=30) -> pd.DataFrame`: Serie temporal de 30 días con records_processed y avg_processing_ms, generada con semilla fija para reproducibilidad.

### 3.3 `chart_generator.py` — Gráficos

Dos funciones independientes con tema oscuro profesional:

- `generate_bar_chart()`: Gráfico de barras horizontal. Muestra registros por fuente con etiqueta de tasa de error. Colores cyan sobre fondo charcoal (#0d0d1a).

- `generate_line_chart()`: Gráfico de líneas con relleno de área. Muestra rendimiento en 30 días. Segundo eje Y (verde) para tiempo de procesamiento promedio. Marcadores circulares en cada punto.

Ambas funciones reciben datos serializados (listas de dicts) y una ruta de salida PNG. Retornan la ruta del archivo generado.

### 3.4 `pdf_generator.py` — PDF con ReportLab

**Clase `PDFReport`:**

- Estilos tipográficos registrados programáticamente (cover, títulos, cuerpo, tabla, footer).
- `build_cover(stats)`: Portada con nombre del sistema, fecha de generación, métricas resumen y línea decorativa cyan.
- `build_stats_table(stats)`: Tabla de 10 filas con métrica/valor. Encabezado con fondo oscuro, filas alternadas, bordes sutiles.
- `build_charts(bar_path, line_path)`: Inserta las dos imágenes PNG generadas, cada una a 160mm × 80mm.
- `build_footer()`: Línea separadora y texto de atribución.
- `generate()`: Ensambla y escribe el PDF en la ruta especificada.

### 3.5 `main.py` — API y Scheduler

Ver sección [4. API REST](#4-api-rest--endpoints) y [5. Automatización](#5-automatización-apscheduler).

---

## 4. API REST — Endpoints

| Método   | Ruta                         | Descripción                          | Códigos HTTP           |
|----------|------------------------------|--------------------------------------|------------------------|
| `POST`   | `/api/generate`              | Ejecuta pipeline completo → PDF     | `201` / `500`          |
| `GET`    | `/api/reports`               | Lista todos los PDFs generados       | `200`                  |
| `GET`    | `/api/reports/{filename}`    | Descarga un PDF específico           | `200` / `404`          |
| `DELETE` | `/api/reports/{filename}`    | Elimina un PDF del servidor          | `200` / `404` / `500`  |
| `GET`    | `/api/stats`                 | Métricas en vivo para el dashboard   | `200` / `500`          |

### 4.1 `POST /api/generate`

**Response `201`:**

```json
{
  "status": "ok",
  "filename": "reporte_20260514.pdf",
  "path": "backend\\outputs\\reporte_20260514.pdf",
  "stats": {
    "total_records": 2000,
    "ok_records": 1400,
    "error_records": 40,
    "active_sources": 5,
    "total_sources": 6,
    "avg_processing_ms": 98.23,
    "p95_processing_ms": 218.45,
    "total_value": 1987234.56,
    "uptime": 99.97,
    "total_executions": 2472,
    "last_generated": "2026-05-14T17:00:00Z",
    "by_source": [ ... ]
  },
  "generated_at": "2026-05-14T17:00:00Z"
}
```

### 4.2 `GET /api/reports`

**Response `200`:**

```json
[
  {
    "filename": "reporte_20260514.pdf",
    "size_bytes": 234567,
    "size_kb": 229.1,
    "created_at": "2026-05-14T17:00:00"
  }
]
```

### 4.3 `GET /api/reports/{filename}`

Streaming del archivo PDF con `Content-Type: application/pdf`.

### 4.4 `DELETE /api/reports/{filename}`

**Response `200`:**

```json
{ "status": "deleted", "filename": "reporte_20260514.pdf" }
```

### 4.5 `GET /api/stats`

Retorna el mismo objeto `stats` del endpoint `/api/generate` (ver sección 4.1), ejecutado contra los datos actuales en memoria.

---

## 5. Automatización (APScheduler)

El scheduler se inicializa en el `lifespan` de la aplicación FastAPI:

```python
scheduler = BackgroundScheduler()
scheduler.add_job(
    scheduled_pipeline,
    CronTrigger.from_crontab("0 6 * * 1-5"),  # Lunes a viernes 06:00 UTC
    id="auto_pipeline",
)
scheduler.start()
```

- **Expresión Cron**: `0 6 * * 1-5` — Coincide con la expresión mostrada en el dashboard.
- **Trigger**: `CronTrigger.from_crontab()` interpreta la expresión estándar de 5 campos.
- **Manejo de errores**: La función `scheduled_pipeline()` captura excepciones y las imprime sin colapsar el scheduler.
- **Shutdown**: Se detiene gracefulmente al cerrar la aplicación.
- **Fallback**: Si APScheduler no está instalado, el scheduler se omite sin errores.

---

## 6. Integración con el Frontend

### 6.1 Archivo `frontend/api.js`

Módulo ES6 exportable con 6 funciones asíncronas:

| Función                     | Método | Endpoint                    |
|-----------------------------|--------|-----------------------------|
| `generateReport()`          | POST   | `/api/generate`             |
| `fetchReports()`            | GET    | `/api/reports`              |
| `getDownloadUrl(filename)`  | GET    | `/api/reports/{filename}`   |
| `deleteReport(filename)`    | DELETE | `/api/reports/{filename}`   |
| `fetchStats()`              | GET    | `/api/stats`                |
| `downloadPdf(filename)`     | —      | Helper de descarga directa  |

### 6.2 Integración directa en `index.html`

El dashboard incluye un bloque `<script>` que:

1. **Carga métricas reales** al iniciar: `GET /api/stats` → actualiza `data-target` de las stat cards.
   - Si el backend no está disponible, los valores demo se mantienen.

2. **Carga la lista de reportes** al iniciar: `GET /api/reports` → renderiza tabla con botones DESCARGAR / ELIMINAR.
   - Muestra mensaje de error si el backend no responde.

3. **Botón "GENERAR REPORTE"**: `POST /api/generate` con estado de carga (loading, éxito, error).

4. **Acciones por reporte**:
   - DESCARGAR: crea un `<a>` temporal con `href` al endpoint de descarga.
   - ELIMINAR: confirmación con `confirm()` + `DELETE /api/reports/{filename}` + recarga de lista.

---

## 7. Instrucciones de Instalación

### Requisitos

- Python 3.10+
- pip (gestor de paquetes)
- Navegador web moderno (para el frontend)

### Instalación

```bash
# 1. Clonar o copiar el proyecto
cd automatizacion_reportes

# 2. Crear entorno virtual (recomendado)
python -m venv venv

# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt
```

### Ejecución

```bash
# 1. Iniciar el backend
cd backend
python main.py
# → Servidor en http://localhost:8000
# → Docs automáticas en http://localhost:8000/docs
# → OpenAPI en http://localhost:8000/openapi.json

# 2. Abrir el frontend
# Simplemente abre index.html en el navegador.
# El dashboard se conectará automáticamente a localhost:8000.
```

### Verificación

```bash
# Probar que la API responde
curl http://localhost:8000/api/stats

# Probar generación de reporte
curl -X POST http://localhost:8000/api/generate

# Listar reportes generados
curl http://localhost:8000/api/reports
```

---

## 8. Uso del Sistema

### Desde el Dashboard

1. Abre `index.html` en el navegador.
2. La terminal animada muestra el flujo simulado del pipeline.
3. Las tarjetas de métricas se actualizan con datos reales del backend.
4. Navega a la sección **"Gestión de Reportes"**.
5. Haz clic en **"GENERAR REPORTE"** para ejecutar el pipeline completo.
6. Una vez generado, aparecerá en la lista con opciones para descargar o eliminar.

### Desde la API

```bash
# Generar reporte
curl -X POST http://localhost:8000/api/generate

# Obtener estadísticas
curl http://localhost:8000/api/stats

# Listar reportes
curl http://localhost:8000/api/reports

# Descargar un reporte
curl -o reporte.pdf http://localhost:8000/api/reports/reporte_20260514.pdf

# Eliminar un reporte
curl -X DELETE http://localhost:8000/api/reports/reporte_20260514.pdf
```

### Documentación interactiva

FastAPI genera automáticamente documentación Swagger en:
- `http://localhost:8000/docs` (UI interactiva)
- `http://localhost:8000/redoc` (vista alternativa)

---

## 9. Créditos y Autoría

| Rol | Nombre |
|------|--------|
| **Arquitectura del sistema** | Dylan Ramirez Lopez |
| **Diseño y desarrollo backend** | Dylan Ramirez Lopez |
| **Diseño UI/UX y frontend** | Dylan Ramirez Lopez |
| **Pipeline de datos** | Dylan Ramirez Lopez |
| **Generación de gráficos y PDFs** | Dylan Ramirez Lopez |
| **Automatización y scheduler** | Dylan Ramirez Lopez |
| **Documentación técnica** | Dylan Ramirez Lopez |

---

> *Arquitectura, diseño y desarrollo integral liderado por **Dylan Ramirez Lopez** — 2026*
>
> AutoData Pipeline v3.2.1 — Sistema automatizado de procesamiento de datos y generación de reportes.
