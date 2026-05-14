# ⚡ DataStream Engine — High Engineering System

> Pipeline ETL autónomo con dashboard en tiempo real, generación de reportes PDF y distribución automatizada.

![Version](https://img.shields.io/badge/version-3.2.1-00f0ff?style=flat&labelColor=0d0d1a)
![Python](https://img.shields.io/badge/Python-3.11-00ff41?style=flat&logo=python&logoColor=white&labelColor=0d0d1a)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-7c3aed?style=flat&logo=fastapi&logoColor=white&labelColor=0d0d1a)
![License](https://img.shields.io/badge/license-MIT-555577?style=flat&labelColor=0d0d1a)

---

## Propósito

DataStream Engine es un sistema de **alta ingeniería** diseñado para automatizar el ciclo completo de procesamiento de datos:

```
Ingesta → Extracción → Transformación → Validación → Render → Distribución
```

Está construido para ingenieros que necesitan un pipeline confiable, visible y auditable, sin intervención manual. Cada ejecución produce un reporte PDF profesional con gráficos y estadísticas, y se distribuye automáticamente según programación Cron.

---

## Stack Tecnológico

### Frontend

| Tecnología | Uso |
|------------|-----|
| HTML5 + Tailwind CSS | Maquetación responsiva mobile-first |
| CSS3 Custom Properties | Sistema de diseño oscuro con acentos neón |
| Vanilla JS (ES6+) | Terminal animada, count-up, pipeline secuencial, fetch API |
| IntersectionObserver | Animaciones al hacer scroll |
| Google Fonts (Inter, JetBrains Mono) | Tipografía técnica profesional |

### Backend

| Tecnología | Uso |
|------------|-----|
| **Python 3.11** | Runtime principal |
| **FastAPI** | Framework REST con documentación OpenAPI automática |
| **Pandas 2.2 + NumPy** | Procesamiento de datos y estadísticas |
| **Matplotlib + Seaborn** | Generación de gráficos profesionales con tema oscuro |
| **ReportLab 4.3** | Composición programática de PDFs |
| **APScheduler 3.10** | Ejecución automatizada por expresión Cron |
| **Uvicorn** | Servidor ASGI de alto rendimiento |

---

## Guía de Instalación Rápida

### Requisitos

- Python 3.10+
- Un navegador moderno (Chrome 90+, Firefox 90+, Safari 15+, Edge 90+)

### Pasos

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/datastream-engine.git
cd datastream-engine

# 2. Crear entorno virtual
python -m venv venv

# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Iniciar el backend
cd backend
python main.py
# → Servidor en http://localhost:8000
# → Docs interactivas en http://localhost:8000/docs

# 5. Abrir el frontend
# Simplemente abre index.html en el navegador
```

---

## Arquitectura del Pipeline

```
                    ┌────────────────────────────┐
                    │     Dashboard (HTML/JS)     │
                    │  localhost:5500/index.html   │
                    └───────────┬────────────────┘
                                │ Fetch API
                                ▼
┌──────────────────────────────────────────────────────────┐
│                   FastAPI (main.py:8000)                  │
│                                                          │
│  POST /api/generate    GET /api/stats                    │
│  GET  /api/reports     DELETE /api/reports/{filename}    │
│                                                          │
│  ┌────────────────────────────────────────────────────┐  │
│  │  APScheduler · Cron: 0 6 * * 1-5                  │  │
│  │  (Lun–Vie 06:00 UTC, sin supervisión)             │  │
│  └──────────────────────┬─────────────────────────────┘  │
└──────────────────────────┼──────────────────────────────┘
                           │
         ┌─────────────────┼────────────────────┐
         ▼                 ▼                     ▼
┌────────────────┐ ┌──────────────┐ ┌────────────────────┐
│ data_processor │ │chart_generator│ │   pdf_generator    │
│ Pandas + NumPy │ │ Matplotlib   │ │   ReportLab         │
│                │ │ Seaborn      │ │                     │
│ 2000 registros │ │ Bar + Line   │ │ Portada + Tabla    │
│ 12 métricas     │ │ Tema oscuro  │ │ + Gráficos + Footer│
└───────┬────────┘ └──────┬───────┘ └──────────┬─────────┘
        │                 │                    │
        ▼                 ▼                    ▼
   DataFrame           PNG temp/           PDF en outputs/
```

### Flujo de Datos (simulado)

1. **Ingesta** — Se genera un DataFrame sintético de 2000 registros con 6 fuentes de datos, valores, tiempos de procesamiento y estados aleatorios con distribución realista.
2. **Extracción** — Los datos se agrupan por fuente y se calculan estadísticas descriptivas.
3. **Transformación** — Pandas normaliza tipos, calcula percentiles, promedios y tasas de error.
4. **Validación** — Se aplican checksums lógicos y control de calidad sobre los datos procesados.
5. **Render** — Matplotlib genera 2 gráficos (barras por fuente + líneas de rendimiento) y ReportLab los ensambla en un PDF profesional.
6. **Distribución** — El PDF se almacena en `backend/outputs/` y queda accesible vía API para descarga.

---

## API REST — Referencia

| Método | Ruta | Descripción | Códigos |
|--------|------|-------------|---------|
| `POST` | `/api/generate` | Ejecuta el pipeline completo | `201` / `500` |
| `GET` | `/api/reports` | Lista todos los PDFs generados | `200` |
| `GET` | `/api/reports/{filename}` | Descarga un PDF específico | `200` / `404` |
| `DELETE` | `/api/reports/{filename}` | Elimina un PDF | `200` / `404` |
| `GET` | `/api/stats` | Métricas en vivo para el dashboard | `200` / `500` |

Documentación interactiva disponible en `http://localhost:8000/docs` una vez iniciado el servidor.

---

## Despliegue en Producción

### GitHub

```bash
# Inicializar repositorio
git init
git add .
git commit -m "feat: DataStream Engine v3.2.1 — pipeline ETL autonomo con dashboard"

# Conectar con repositorio remoto
git remote add origin https://github.com/tu-usuario/datastream-engine.git
git branch -M main
git push -u origin main
```

### Vercel (Frontend + Backend Serverless)

El proyecto está optimizado para Vercel con Python Serverless Functions.

#### Configuración

1. **Crear `vercel.json`** en la raíz del proyecto (ya incluido):

```json
{
  "buildCommand": "pip install -r requirements.txt",
  "outputDirectory": ".",
  "functions": {
    "api/**/*.py": {
      "runtime": "python3.11",
      "maxDuration": 30
    }
  },
  "rewrites": [
    { "source": "/(.*)", "destination": "/api/main" }
  ]
}
```

2. **Crear carpeta `api/`** y dentro un archivo `main.py` que importe la aplicación FastAPI desde el backend:

```python
# api/main.py
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent / "backend"))
from main import app
```

3. **En Vercel Dashboard**:
   - Importar el repositorio desde GitHub
   - Framework: **Other**
   - Build command: `pip install -r requirements.txt`
   - Output directory: `.`
   - Root directory: (vacío — usar la raíz del repo)

4. **Variables de entorno** (si se requiere configuración adicional):
   - Ninguna requerida para el funcionamiento base.

5. **Desplegar**: Vercel detecta automáticamente las Python Serverless Functions en la carpeta `api/`.

> ⚠️ **Nota**: El dashboard (`index.html`) debe actualizar la constante `API` en el bloque de integración para apuntar a la URL de producción de Vercel en lugar de `localhost:8000`.

---

## Estructura del Proyecto

```
datastream-engine/
│
├── index.html              # Dashboard mobile-first (único archivo)
├── README.md               # Esta documentación
├── requirements.txt        # Dependencias Python
├── vercel.json             # Configuración de despliegue Vercel
│
├── backend/
│   ├── main.py             # FastAPI + endpoints + APScheduler
│   ├── config.py           # Constantes de configuración
│   ├── data_processor.py   # Ingesta y estadísticas (Pandas)
│   ├── chart_generator.py  # Gráficos (Matplotlib/Seaborn)
│   ├── pdf_generator.py    # PDFs (ReportLab)
│   ├── outputs/            # PDFs generados
│   └── temp/               # PNGs temporales
│
├── frontend/
│   └── api.js              # Módulo JS para consumir la API
│
└── api/
    └── main.py             # Vercel Serverless Function wrapper
```

---

## Responsive Design

| Componente | Móvil (< 640px) | Tablet (640–1024px) | Desktop (> 1024px) |
|------------|------------------|---------------------|---------------------|
| Stats grid | 2 columnas       | 4 columnas          | 4 columnas          |
| Features   | 1 columna        | 2 columnas          | 3 columnas          |
| Pipeline   | Lista vertical   | Horizontal compacto | Horizontal completo |
| Tech Stack | Grid 3×2         | Flex horizontal     | Flex horizontal     |
| Cron fields| 5 col compacto   | 5 col normal        | 5 col expandido     |
| Outputs    | 1 columna        | 3 columnas          | 3 columnas          |
| Terminal   | font-size: 11px  | font-size: 13px     | font-size: 14px     |

Touch targets mínimos de **44px** (estándar Apple HIG / Google Material).

---

## Créditos

| Rol | Nombre |
|-----|--------|
| **Desarrollo Integral** | Dylan Ramirez Lopez |
| Arquitectura del sistema | Dylan Ramirez Lopez |
| Diseño UI/UX | Dylan Ramirez Lopez |
| Backend y pipeline de datos | Dylan Ramirez Lopez |
| Documentación | Dylan Ramirez Lopez |

---

> *Diseñado y desarrollado por **Dylan Ramirez Lopez** — 2026*
>
> [Reportar un problema](https://github.com/tu-usuario/datastream-engine/issues)
