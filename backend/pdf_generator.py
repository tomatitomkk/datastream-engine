"""
pdf_generator.py — Professional PDF assembly with ReportLab.

Produces a multi-page PDF containing:
  - Cover page with title, timestamp, and pipeline metadata
  - Statistics summary table
  - Embedded chart images (bar + line)
  - Footer attribution
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, PageBreak, HRFlowable
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pathlib import Path
from datetime import datetime

DARK_BG = "#07070d"
ACCENT_CYAN = "#00f0ff"
HEADER_FILE = Path(__file__).resolve().parent / "temp" / ".header_generated"


class PDFReport:
    def __init__(self, output_path: Path):
        self.output_path = output_path
        self.styles = getSampleStyleSheet()
        self._register_styles()

        self.elements = []

    def _register_styles(self):
        self.styles.add(ParagraphStyle(
            "CoverTitle", fontName="Helvetica-Bold", fontSize=26,
            textColor=colors.HexColor("#e8e8f0"), alignment=TA_CENTER,
            leading=34, spaceAfter=12,
        ))
        self.styles.add(ParagraphStyle(
            "CoverSub", fontName="Helvetica", fontSize=12,
            textColor=colors.HexColor("#8888aa"), alignment=TA_CENTER,
            leading=18, spaceAfter=6,
        ))
        self.styles.add(ParagraphStyle(
            "SectionTitle", fontName="Helvetica-Bold", fontSize=15,
            textColor=colors.HexColor(ACCENT_CYAN), alignment=TA_LEFT,
            leading=20, spaceBefore=16, spaceAfter=8,
        ))
        self.styles.add(ParagraphStyle(
            "BodyText2", fontName="Helvetica", fontSize=9,
            textColor=colors.HexColor("#c8c8e0"), leading=13,
            spaceAfter=4,
        ))
        self.styles.add(ParagraphStyle(
            "Footer", fontName="Helvetica-Oblique", fontSize=8,
            textColor=colors.HexColor("#555577"), alignment=TA_CENTER,
            leading=10,
        ))
        self.styles.add(ParagraphStyle(
            "TableHeader", fontName="Helvetica-Bold", fontSize=8,
            textColor=colors.white, alignment=TA_CENTER,
        ))
        self.styles.add(ParagraphStyle(
            "TableCell", fontName="Helvetica", fontSize=8,
            textColor=colors.HexColor("#c8c8e0"), alignment=TA_CENTER,
        ))

    def build_cover(self, stats: dict):
        self.elements.append(Spacer(1, 60 * mm))
        self.elements.append(Paragraph("AutoData Pipeline", self.styles["CoverTitle"]))
        self.elements.append(Paragraph("Reporte Automatizado de Datos", self.styles["CoverSub"]))
        self.elements.append(Spacer(1, 10 * mm))
        self.elements.append(HRFlowable(
            width="60%", thickness=1, color=colors.HexColor(ACCENT_CYAN),
            spaceAfter=10 * mm, spaceBefore=4 * mm,
        ))
        generated = stats.get("last_generated", datetime.utcnow().isoformat())
        try:
            dt = datetime.fromisoformat(generated.replace("Z", "+00:00"))
            date_str = dt.strftime("%d de %B de %Y a las %H:%M UTC")
        except Exception:
            date_str = generated

        self.elements.append(Paragraph(f"Generado: {date_str}", self.styles["CoverSub"]))
        self.elements.append(Spacer(1, 4 * mm))
        self.elements.append(Paragraph(
            f"Registros procesados: {stats.get('total_records', 0):,}  |  "
            f"Fuentes activas: {stats.get('active_sources', 0)}  |  "
            f"Uptime: {stats.get('uptime', 0)}%",
            self.styles["CoverSub"]
        ))
        self.elements.append(PageBreak())

    def build_stats_table(self, stats: dict):
        self.elements.append(Paragraph("Resumen de Métricas", self.styles["SectionTitle"]))
        self.elements.append(Spacer(1, 3 * mm))

        rows = [
            ["Métrica", "Valor"],
            ["Total registros procesados", f"{stats.get('total_records', 0):,}"],
            ["Registros OK", f"{stats.get('ok_records', 0):,}"],
            ["Registros con error", f"{stats.get('error_records', 0):,}"],
            ["Fuentes de datos activas", f"{stats.get('active_sources', 0)} / {stats.get('total_sources', 0)}"],
            ["Tiempo promedio de procesamiento", f"{stats.get('avg_processing_ms', 0):.2f} ms"],
            ["P95 de procesamiento", f"{stats.get('p95_processing_ms', 0):.2f} ms"],
            ["Valor total acumulado", f"${stats.get('total_value', 0):,.2f}"],
            ["Uptime del sistema", f"{stats.get('uptime', 0)}%"],
            ["Ejecuciones completadas", f"{stats.get('total_executions', 0):,}"],
        ]

        col_widths = [120 * mm, 60 * mm]
        table = Table(rows, colWidths=col_widths, repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a3a")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("ALIGN", (1, 0), (-1, -1), "CENTER"),
            ("ALIGN", (0, 0), (0, -1), "LEFT"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#0d0d1a"), colors.HexColor("#111122")]),
            ("TEXTCOLOR", (0, 1), (-1, -1), colors.HexColor("#c8c8e0")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#1a1a3a")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        self.elements.append(table)
        self.elements.append(Spacer(1, 6 * mm))

    def build_charts(self, bar_path: Path, line_path: Path):
        self.elements.append(Paragraph("Visualizaciones", self.styles["SectionTitle"]))
        self.elements.append(Spacer(1, 3 * mm))

        if bar_path.exists():
            img = Image(str(bar_path), width=160 * mm, height=80 * mm)
            self.elements.append(img)
            self.elements.append(Spacer(1, 4 * mm))

        if line_path.exists():
            img = Image(str(line_path), width=160 * mm, height=80 * mm)
            self.elements.append(img)
            self.elements.append(Spacer(1, 4 * mm))

        self.elements.append(PageBreak())

    def build_footer(self):
        self.elements.append(Spacer(1, 15 * mm))
        self.elements.append(HRFlowable(
            width="40%", thickness=0.5, color=colors.HexColor("#1a1a3a"),
            spaceAfter=4 * mm, spaceBefore=4 * mm,
        ))
        self.elements.append(Paragraph(
            "Arquitectura, diseno y desarrollo integral liderado por Dylan Ramirez Lopez",
            self.styles["Footer"]
        ))

    def generate(self, stats: dict, bar_chart_path: Path, line_chart_path: Path) -> Path:
        try:
            self.build_cover(stats)
            self.build_stats_table(stats)
            self.build_charts(bar_chart_path, line_chart_path)
            self.build_footer()

            doc = SimpleDocTemplate(
                str(self.output_path),
                pagesize=A4,
                topMargin=20 * mm,
                bottomMargin=20 * mm,
                leftMargin=18 * mm,
                rightMargin=18 * mm,
            )
            doc.build(self.elements)
            return self.output_path
        except Exception as e:
            raise RuntimeError(f"Error generating PDF: {e}") from e
