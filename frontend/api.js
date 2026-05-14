/**
 * api.js — Consumo de la API REST de AutoData Pipeline.
 *
 * Todas las funciones retornan Promesas (async/await).
 * Ajusta API_BASE a la URL donde corra el backend.
 *
 * Arquitectura, diseno y desarrollo integral liderado por Dylan Ramirez Lopez.
 */

const API_BASE = "http://localhost:8000/api";

/**
 * POST /api/generate — Dispara el pipeline completo.
 * @returns {Promise<object>} { status, filename, path, stats, generated_at }
 */
export async function generateReport() {
  const res = await fetch(`${API_BASE}/generate`, { method: "POST" });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Error ${res.status} al generar reporte`);
  }
  return res.json();
}

/**
 * GET /api/reports — Lista todos los PDFs generados.
 * @returns {Promise<Array<{filename, size_bytes, size_kb, created_at}>>}
 */
export async function fetchReports() {
  const res = await fetch(`${API_BASE}/reports`);
  if (!res.ok) throw new Error(`Error ${res.status} al obtener reportes`);
  return res.json();
}

/**
 * GET /api/reports/{filename} — Devuelve la URL de descarga directa.
 * @param {string} filename
 * @returns {string} URL para descargar el PDF
 */
export function getDownloadUrl(filename) {
  return `${API_BASE}/reports/${encodeURIComponent(filename)}`;
}

/**
 * DELETE /api/reports/{filename} — Elimina un PDF del servidor.
 * @param {string} filename
 * @returns {Promise<object>} { status, filename }
 */
export async function deleteReport(filename) {
  const res = await fetch(`${API_BASE}/reports/${encodeURIComponent(filename)}`, {
    method: "DELETE",
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Error ${res.status} al eliminar reporte`);
  }
  return res.json();
}

/**
 * GET /api/stats — Métricas en vivo para el dashboard.
 * @returns {Promise<object>} { total_records, active_sources, uptime, total_executions, ... }
 */
export async function fetchStats() {
  const res = await fetch(`${API_BASE}/stats`);
  if (!res.ok) throw new Error(`Error ${res.status} al obtener estadisticas`);
  return res.json();
}

/**
 * Helper: descarga un PDF directamente en el navegador.
 * @param {string} filename
 */
export function downloadPdf(filename) {
  const a = document.createElement("a");
  a.href = getDownloadUrl(filename);
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}

/**
 * Helper: formatea bytes a KB/MB legibles.
 * @param {number} bytes
 * @returns {string}
 */
export function formatFileSize(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}
