from __future__ import annotations
from pathlib import Path
from reportlab.lib.pagesizes import A5
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from .image_utils import draw_bitmap, draw_placeholder, find_glass_image
from .definition import RecipeData

MARGIN   = 12 * mm
BOX_SIZE = 40 * mm
PAGE_W, PAGE_H = A5


# ---------------------------------------------------------------------------
# Gemeinsamer Drawer für DIN A5‑Fläche (wird von beiden Generatoren genutzt)
# ---------------------------------------------------------------------------

def draw_recipe_area(
    c: canvas.Canvas,
    area_x: float,
    area_y: float,
    recipe: RecipeData,
    glasses_dir: Path,
) -> None:
    """Zeichnet ein Rezept in einen A5‑großen Rechteckbereich (oben‑links = area_x/area_y)."""

    # Layout für den Bereich (identisch zu create_cocktail_pdf, aber relativ)
    margin = 12 * mm
    box_size = 40 * mm
    page_w, page_h = A5

    # Koordinaten relativ zum Bereich
    def rx(val: float) -> float:  # X-Wert innerhalb der A5‑Fläche
        return area_x + val

    def ry(val: float) -> float:  # Y-Wert innerhalb der A5‑Fläche
        return area_y + val

    # Titel
    c.setFont("Helvetica-Bold", 16)
    c.drawString(rx(margin), ry(page_h - margin), recipe["title"])

    # Bildbox
    box_x = rx(page_w - margin - box_size)
    box_y = ry(page_h - margin - box_size + 3)
    drawn = False
    if recipe.get("image_path") and Path(recipe["image_path"]).is_file():
        drawn = draw_bitmap(c, Path(recipe["image_path"]), box_x, box_y, box_size, box_size)
    if not drawn and recipe.get("glass"):
        gimg = find_glass_image(recipe["glass"], glasses_dir)
        if gimg:
            drawn = draw_bitmap(c, gimg, box_x, box_y, box_size, box_size)
    if not drawn:
        draw_placeholder(c, box_x, box_y, box_size, box_size)


    # Zutaten
    top_ing = ry(page_h - margin - 12 * mm)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(rx(margin), top_ing, "Zutaten")
    c.setFont("Helvetica", 9)
    lh = 7 * mm
    for i, ing in enumerate(recipe["ingredients"], 1):
        c.drawString(rx(margin + 4 * mm), top_ing - i * lh, f"• {ing}")

    # Zubereitung
    top_steps = top_ing - (len(recipe["ingredients"])+1) * lh
    c.setFont("Helvetica-Bold", 12)
    c.drawString(rx(margin), top_steps, "Zubereitung")
    c.setFont("Helvetica", 9)
    sh = 6 * mm
    for idx, step in enumerate(recipe["steps"], 1):
        c.drawString(rx(margin + 4 * mm), top_steps - idx * sh, f"{idx}. {step}")