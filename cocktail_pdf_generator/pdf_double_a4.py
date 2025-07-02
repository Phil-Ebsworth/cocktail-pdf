from __future__ import annotations
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, A5
from reportlab.lib.units import mm
from .layout import draw_recipe_area
from .recipe_loader import load_recipe_json, RecipeData

MARGIN_H = 10 * mm
MARGIN_V = 10 * mm
GAP      = 8 * mm


def _compute_scale(page_w: float) -> float:
    """Skalierung, damit gedrehte A5‑Breite (210 mm) in A4‑Breite passt."""
    return (page_w - 2 * MARGIN_H) / A5[1]


# ---------------------------------------------------------------------------
# Neue Funktion: alle Rezepte paarweise auf DIN A4
# ---------------------------------------------------------------------------

def generate_double_a4_sheet(
    recipes_folder: str | Path,
    output_path: str | Path,
    glasses_dir: str | Path | None = None,
) -> Path:
    """DIN-A4-PDF mit **zwei quer liegenden A5-Rezepten**, jetzt wirklich volle Breite.

    • Dreht den A5-Block um **+90 °** (Uhrzeigersinn) – Breite = 210 mm.
    • Skalierung wird nur von der **Breite** bestimmt (10 mm Seitenrand). 
    • Blöcke werden linksbündig gesetzt; nichts ragt mehr aus der Seite.
    """

    recipes_folder = Path(recipes_folder).expanduser().resolve()
    output_path = Path(output_path).expanduser().resolve()
    glasses_dir_path = Path(glasses_dir) if glasses_dir else Path(__file__).resolve().parent.parent / "glasses"

    recipes = [load_recipe_json(j) for j in sorted(recipes_folder.glob("*.json"))]

    c = canvas.Canvas(str(output_path), pagesize=A4)
    page_w, page_h = A4  # ~595 × 842 pt

    margin_h = 10 * mm
    margin_v = 10 * mm
    gap      = 8 * mm

    # Skaliere so, dass gedrehte Breite (A5-Höhe) genau page_w - 2*margin_h füllt
    scale = (page_w - 2 * margin_h) / A5[1]

    block_h = A5[0] * scale  # Höhe jedes Blocks nach Rotation (148 mm → ~104 mm)

    # Prüfen, ob zwei Blöcke + Gap in die Höhe passen, sonst proportionale Reduktion
    needed_h = 2 * block_h + gap
    max_h    = page_h - 2 * margin_v
    if needed_h > max_h:
        scale *= max_h / needed_h
        block_h = A5[0] * scale

    x_left = margin_h                # Block beginnt am linken Rand (nach Rotation)
    y_top  = page_h - margin_v - block_h
    y_bottom = margin_v

    for idx, rec in enumerate(recipes):
        slot = idx % 2  # 0 oben, 1 unten
        if slot == 0 and idx > 0:
            c.showPage()

        y_off = y_top if slot == 0 else y_bottom

        c.saveState()
        # Positioniere an linke UNTERE Ecke des Blocks und rotiere +90°
        c.translate(x_left, y_off)
        c.rotate(90)
        c.scale(scale, scale)
        # Nach Drehung liegt Ursprungs-(0,0) links-unten; wir brauchen links-oben
        c.translate(0, -A5[1])
        draw_recipe_area(c, 0, 0, rec, glasses_dir_path)
        c.restoreState()

    c.save()
    return output_path