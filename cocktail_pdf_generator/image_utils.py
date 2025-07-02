from __future__ import annotations
import io
from pathlib import Path
from typing import Optional
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.lib import colors

try:
    from PIL import Image
except ModuleNotFoundError:
    Image = None

__all__ = ["draw_bitmap", "draw_placeholder", "find_glass_image", "auto_same_name"]

GLASS_EXT = (".png", ".jpg", ".jpeg", ".gif")


# ---------------------------------------------------------------------------
# Platzhalter‑Zeichnung
# ---------------------------------------------------------------------------

def draw_placeholder(c: canvas.Canvas, x: float, y: float, w: float, h: float) -> None:
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

def auto_same_name(base: Path) -> Optional[Path]:
    for ext in (".jpg", ".jpeg", ".png", ".gif"):
        cand = base.with_suffix(ext)
        if cand.is_file():
            return cand
    return None


def find_glass_image(glass: str, gdir: Path) -> Optional[Path]:
    for ext in (".png", ".jpg", ".jpeg", ".gif"):
        img = gdir / f"{glass}{ext}"
        if img.is_file():
            return img
    return None


def draw_bitmap(c: canvas.Canvas, path: Path, x: float, y: float, w: float, h: float) -> bool:
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