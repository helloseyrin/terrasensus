"""
TerraSensus — Lab Report PDF Generator

Generates realistic synthetic soil lab report PDFs using reportlab.
These act as test fixtures for the lab-parser service.

Each report mimics a real UK/EU accredited soil lab format with:
  - Lab header, sample metadata, result table, interpretation notes
  - Values drawn from agronomically realistic distributions
  - Intentional format variation across reports (tests parser robustness)

Phase 2: real lab reports will be uploaded by farmers via the mobile app.
"""

import random
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path

# reportlab import guarded — install separately: pip install reportlab
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import cm
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


# Realistic value ranges per field (mean, std_dev)
SOIL_DISTRIBUTIONS = {
    "pH":                  (6.8,  0.6),
    "Nitrogen (N)":        (85,   30),    # mg/kg
    "Phosphorus (P)":      (45,   20),    # mg/kg
    "Potassium (K)":       (130,  50),    # mg/kg
    "EC":                  (1.1,  0.5),   # dS/m
    "Organic Matter":      (3.5,  1.2),   # %
    "CEC":                 (18,   6),     # meq/100g
    "Calcium (Ca)":        (1800, 400),   # mg/kg
    "Magnesium (Mg)":      (180,  60),    # mg/kg
    "Zinc (Zn)":           (4.5,  2.0),   # mg/kg
    "Iron (Fe)":           (55,   20),    # mg/kg
    "Sand":                (40,   15),    # %
    "Silt":                (35,   12),    # %
    "Clay":                (25,   10),    # %
}

UNITS = {
    "pH": "", "Nitrogen (N)": "mg/kg", "Phosphorus (P)": "mg/kg",
    "Potassium (K)": "mg/kg", "EC": "dS/m", "Organic Matter": "%",
    "CEC": "meq/100g", "Calcium (Ca)": "mg/kg", "Magnesium (Mg)": "mg/kg",
    "Zinc (Zn)": "mg/kg", "Iron (Fe)": "mg/kg",
    "Sand": "%", "Silt": "%", "Clay": "%",
}

LAB_NAMES = [
    "AgriAnalytics Ltd", "SoilSense Laboratories", "GreenField Testing Services",
    "EarthCheck UK", "CropLab Europe",
]


@dataclass
class LabReport:
    plot_id: str
    sample_depth_cm: int
    sample_date: date
    lab_name: str
    report_ref: str
    results: dict = field(default_factory=dict)

    @classmethod
    def generate(cls, plot_id: str) -> "LabReport":
        results = {}
        for field_name, (mean, std) in SOIL_DISTRIBUTIONS.items():
            value = random.gauss(mean, std)
            # Ensure texture sums to ~100% and values stay positive
            value = max(0.1, value)
            if field_name in ("Sand", "Silt", "Clay"):
                results[field_name] = round(value, 1)
            elif field_name == "pH":
                results[field_name] = round(min(9.5, max(3.5, value)), 2)
            else:
                results[field_name] = round(value, 2)

        sample_date = date.today() - timedelta(days=random.randint(3, 30))
        return cls(
            plot_id=plot_id,
            sample_depth_cm=random.choice([15, 20, 30]),
            sample_date=sample_date,
            lab_name=random.choice(LAB_NAMES),
            report_ref=f"TS-{random.randint(10000, 99999)}",
            results=results,
        )


def generate_pdf(report: LabReport, output_dir: Path) -> Path:
    if not REPORTLAB_AVAILABLE:
        raise ImportError("reportlab is required: pip install reportlab")

    output_dir.mkdir(parents=True, exist_ok=True)
    filename = output_dir / f"{report.plot_id}_{report.report_ref}.pdf"

    doc = SimpleDocTemplate(str(filename), pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    story = []

    # Header
    story.append(Paragraph(f"<b>{report.lab_name}</b>", styles["Title"]))
    story.append(Paragraph("Soil Analysis Report", styles["Heading2"]))
    story.append(Spacer(1, 0.5*cm))

    # Metadata table
    meta = [
        ["Report Ref:", report.report_ref, "Plot ID:", report.plot_id],
        ["Sample Date:", report.sample_date.isoformat(), "Sample Depth:", f"{report.sample_depth_cm} cm"],
        ["Analysis Date:", date.today().isoformat(), "", ""],
    ]
    meta_table = Table(meta, colWidths=[4*cm, 6*cm, 4*cm, 4*cm])
    meta_table.setStyle(TableStyle([("FONTSIZE", (0,0), (-1,-1), 9)]))
    story.append(meta_table)
    story.append(Spacer(1, 0.8*cm))

    # Results table
    story.append(Paragraph("<b>Analysis Results</b>", styles["Heading3"]))
    data = [["Parameter", "Result", "Unit"]]
    for param, value in report.results.items():
        data.append([param, str(value), UNITS.get(param, "")])

    result_table = Table(data, colWidths=[8*cm, 4*cm, 4*cm])
    result_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2d6a4f")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f4f0")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    story.append(result_table)
    story.append(Spacer(1, 1*cm))

    story.append(Paragraph(
        "This report is for agronomic guidance only. Values represent the submitted sample "
        "and may not reflect the entire plot. Consult a qualified agronomist before applying treatments.",
        styles["Italic"],
    ))

    doc.build(story)
    return filename


if __name__ == "__main__":
    import yaml
    config = yaml.safe_load(open(Path(__file__).parent / "config.yaml"))
    output_dir = Path(config["lab_report"]["output_dir"])

    for plot in config["plots"]:
        report = LabReport.generate(plot_id=plot["id"])
        path = generate_pdf(report, output_dir)
        print(f"Generated: {path}")
