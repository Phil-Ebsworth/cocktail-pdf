from __future__ import annotations
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, A5
from reportlab.lib.units import mm
from .layout import draw_recipe_area
from .recipe_loader import load_recipe_json, RecipeData

def generate_quadruple_a4_sheet(
    recipes_folder: str | Path,
    output_path: str | Path,
    glasses_dir: str | Path | None = None,
) -> Path:
    """Erzeugt ein A4‑PDF mit **vier hochkant platzierten A5‑Rezepten** (2×2‑Raster)."""

    recipes_folder = Path(recipes_folder).expanduser().resolve()
    output_path = Path(output_path).expanduser().resolve()
    glasses_dir_path = Path(glasses_dir) if glasses_dir else Path(__file__).resolve().parent.parent / "glasses"

    recipes = [load_recipe_json(j) for j in sorted(recipes_folder.glob("*.json"))]

    c = canvas.Canvas(str(output_path), pagesize=A4)
    page_w, page_h = A4

    margin_h = 10 * mm
    margin_v = 10 * mm
    gap_x    = 8 * mm
    gap_y    = 8 * mm

    block_w = (page_w - 2 * margin_h - gap_x) / 2
    block_h = (page_h - 2 * margin_v - gap_y) / 2
    scale_x = block_w / A5[0]
    scale_y = block_h / A5[1]
    scale = min(scale_x, scale_y)

    # Offset-Koordinaten (linke untere Ecke je Block)
    positions = [
        (margin_h, page_h - margin_v - block_h),              # oben links
        (margin_h + block_w + gap_x, page_h - margin_v - block_h),  # oben rechts
        (margin_h, margin_v),                                 # unten links
        (margin_h + block_w + gap_x, margin_v),               # unten rechts
    ]

    for idx, rec in enumerate(recipes):
        slot = idx % 4
        if slot == 0 and idx > 0:
            c.showPage()

        x_off, y_off = positions[slot]
        c.saveState()
        c.translate(x_off, y_off)
        c.scale(scale, scale)
        draw_recipe_area(c, 0, 0, rec, glasses_dir_path)
        c.restoreState()

    c.save()
    return output_path



