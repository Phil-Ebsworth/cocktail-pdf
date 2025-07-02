"""PDF‑Generator für Cocktail‑Rezepte – kompakte DIN A5‑Ausgabe **und** A4‑Doppelseite.

v2.1 (2025‑07‑02)
~~~~~~~~~~~~~~~~~
* Standardfunktion **create_cocktail_pdf** erzeugt weiterhin eine DIN A5‑Seite pro Rezept.
* **NEU:** `generate_double_a4_sheet(recipes_folder, output_path, glasses_dir=None)` –
  legt alle Rezepte paarweise (oben / unten) auf DIN A4‑Seiten ab. Praktisch zum
  Sammeldruck: zwei A5‑Rezepte auf einem A4‑Blatt.
* Intern wiederverwendet ein Helfer `_draw_recipe_area`, damit keine Code‑Duplikate
  entsteht. PNG‑Transparenz‑Fix usw. bleiben uneingeschränkt erhalten.

Dependencies
~~~~~~~~~~~~
```bash
pip install reportlab pillow
```
"""

from __future__ import annotations

import io
import json
from pathlib import Path
from typing import List, TypedDict, Any, Optional, Tuple

from reportlab.lib.pagesizes import A5, A4  # DIN A5 & A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from reportlab.pdfgen import canvas

try:
    from PIL import Image  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    Image = None  # Pillow optional (für PNG‑Fix empfohlen)

__all__ = [
    "create_cocktail_pdf",
    "generate_pdfs_from_folder",
    "generate_double_a4_sheet",
    "load_recipe_json",
]

# ---------------------------------------------------------------------------
# Datentypen
# ---------------------------------------------------------------------------

class RecipeData(TypedDict, total=False):
    title: str
    ingredients: List[str]
    steps: List[str]
    image_path: str | None
    tip: str | None
    glass: str | None  # martini | tumbler | longdrink | wine …

# ---------------------------------------------------------------------------
# Platzhalter‑Zeichnung
# ---------------------------------------------------------------------------

def _draw_placeholder(c: canvas.Canvas, x: float, y: float, w: float, h: float) -> None:
    c.saveState()
    c.setStrokeColor(colors.black)
    c.setLineWidth(1.5)
    c.rect(x, y, w, h)
    c.line(x, y, x + w, y + h)
    c.line(x, y + h, x + w, y)
    c.setFont("Helvetica-Bold", 8)
    c.drawCentredString(x + w / 2, y + h / 2 - 3, "(Bild fehlt)")
    c.restoreState()

# ---------------------------------------------------------------------------
# Bild‑Loader (PNG‑Fix etc.)
# ---------------------------------------------------------------------------

def _auto_same_name(base: Path) -> Optional[Path]:
    for ext in (".jpg", ".jpeg", ".png", ".gif"):
        cand = base.with_suffix(ext)
        if cand.is_file():
            return cand
    return None


def _find_glass_image(glass: str, gdir: Path) -> Optional[Path]:
    for ext in (".png", ".jpg", ".jpeg", ".gif"):
        img = gdir / f"{glass}{ext}"
        if img.is_file():
            return img
    return None


def _draw_bitmap(c: canvas.Canvas, path: Path, x: float, y: float, w: float, h: float) -> bool:
    suffix = path.suffix.lower()
    if suffix == ".png" and Image is not None:
        try:
            img = Image.open(path)
            if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
                bg = Image.new("RGB", img.size, (255, 255, 255))
                bg.paste(img, mask=img.split()[-1])
                bio = io.BytesIO()
                bg.save(bio, format="PNG")
                bio.seek(0)
                c.drawImage(ImageReader(bio), x, y, w, h, preserveAspectRatio=True, anchor="c")
                return True
        except Exception:
            pass
    try:
        c.drawImage(str(path), x, y, w, h, preserveAspectRatio=True, anchor="c", mask="auto")
        return True
    except Exception:
        pass
    if Image is not None:
        try:
            img = Image.open(path).convert("RGB")
            bio = io.BytesIO()
            img.save(bio, format="PNG")
            bio.seek(0)
            c.drawImage(ImageReader(bio), x, y, w, h, preserveAspectRatio=True, anchor="c")
            return True
        except Exception:
            pass
    return False

# ---------------------------------------------------------------------------
# Gemeinsamer Drawer für DIN A5‑Fläche (wird von beiden Generatoren genutzt)
# ---------------------------------------------------------------------------

def _draw_recipe_area(
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
        drawn = _draw_bitmap(c, Path(recipe["image_path"]), box_x, box_y, box_size, box_size)
    if not drawn and recipe.get("glass"):
        gimg = _find_glass_image(recipe["glass"], glasses_dir)
        if gimg:
            drawn = _draw_bitmap(c, gimg, box_x, box_y, box_size, box_size)
    if not drawn:
        _draw_placeholder(c, box_x, box_y, box_size, box_size)

    # Glasname
    if recipe.get("glass"):
        c.setFont("Helvetica", 8)
        c.drawCentredString(box_x + box_size / 2, box_y - 3 * mm, recipe["glass"].capitalize())

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

# ---------------------------------------------------------------------------
# Öffentliche API: einzelne A5‑PDF
# ---------------------------------------------------------------------------

def create_cocktail_pdf(
    *,
    title: str,
    ingredients: List[str],
    steps: List[str],
    output_path: str | Path,
    image_path: str | Path | None = None,
    glass: str | None = None,
    glasses_dir: str | Path | None = None,
) -> Path:
    output_path = Path(output_path).expanduser().resolve()
    c = canvas.Canvas(str(output_path), pagesize=A5)
    recipe_data: RecipeData = {
        "title": title,
        "ingredients": ingredients,
        "steps": steps,
        "image_path": str(image_path) if image_path else None,
        "glass": glass,
    }
    _draw_recipe_area(c, 0, 0, recipe_data, Path(glasses_dir) if glasses_dir else Path(__file__).resolve().parent.parent / "glasses")
    c.save()
    return output_path

# ---------------------------------------------------------------------------
# Batch‑Generator (unverändert)
# ---------------------------------------------------------------------------

def load_recipe_json(json_file: str | Path) -> RecipeData:
    data: Any = json.loads(Path(json_file).read_text("utf-8"))
    if not {"title", "ingredients", "steps"}.issubset(data):
        raise ValueError(f"JSON {json_file} fehlt Pflichtfelder (title, ingredients, steps)")
    return RecipeData(
        title=data["title"],
        ingredients=data["ingredients"],
        steps=data["steps"],
        image_path=data.get("image_path"),
        glass=data.get("glass"),
    )


def generate_pdfs_from_folder(recipes_folder: str | Path, output_dir: str | Path | None = None, glasses_dir: str | Path | None = None):
    recipes_folder = Path(recipes_folder).expanduser().resolve()
    out_dir = Path(output_dir).expanduser().resolve() if output_dir else recipes_folder
    out_dir.mkdir(parents=True, exist_ok=True)
    pdfs: List[Path] = []
    for js in recipes_folder.glob("*.json"):
        rec = load_recipe_json(js)
        auto_img = _auto_same_name(js)
        if not rec.get("image_path") and auto_img:
            rec["image_path"] = str(auto_img)
        pdfs.append(
            create_cocktail_pdf(
                title=rec["title"],
                ingredients=rec["ingredients"],
                steps=rec["steps"],
                image_path=rec.get("image_path"),
                glass=rec.get("glass"),
                glasses_dir=glasses_dir,
                output_path=out_dir / f"{js.stem}.pdf",
            )
        )
    return pdfs

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
        _draw_recipe_area(c, 0, 0, rec, glasses_dir_path)
        c.restoreState()

    c.save()
    return output_path
