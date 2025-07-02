from __future__ import annotations
import json
from pathlib import Path
from typing import TypedDict, List, Any
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A5
from .layout import draw_recipe_area
from .definition import RecipeData

from cocktail_pdf_generator.image_utils import auto_same_name
from cocktail_pdf_generator.definition import RecipeData

REQ = {"title", "ingredients", "steps"}

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
    draw_recipe_area(c, 0, 0, recipe_data, Path(glasses_dir) if glasses_dir else Path(__file__).resolve().parent.parent / "glasses")
    c.save()
    return output_path


def generate_pdfs_from_folder(recipes_folder: str | Path, output_dir: str | Path | None = None, glasses_dir: str | Path | None = None):
    recipes_folder = Path(recipes_folder).expanduser().resolve()
    out_dir = Path(output_dir).expanduser().resolve() if output_dir else recipes_folder
    out_dir.mkdir(parents=True, exist_ok=True)
    pdfs: List[Path] = []
    for js in recipes_folder.glob("*.json"):
        rec = load_recipe_json(js)
        auto_img = auto_same_name(js)
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