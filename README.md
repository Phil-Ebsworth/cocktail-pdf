# 🍸 Cocktail PDF Generator

Ein Python-Projekt zur Erstellung von ansprechenden PDF-Rezeptkarten für Cocktails – wahlweise als einzelne DIN-A5-Seite oder gesammelt im DIN-A4-Format mit 2 oder 4 Rezepten pro Blatt.

---

## 📦 Features

- ✅ **Einzel-PDFs (DIN A5)** – perfekt für einzelne Ausdrucke oder digitale Sammlung.
- ✅ **Doppelseiten (2×A5 quer auf A4)** – ideal für praktischen Druck und Zuschnitt.
- ✅ **Vierer-Layout (4×A5 quer auf A4)** – platzsparend und effizient.
- ✅ **Automatische Glas-Bilder** – über `glass`-Feld im JSON wählbar (`longdrink`, `tumbler`, `wine`, `martini` usw.)
- ✅ **Fallback bei fehlenden Bildern** – Platzhalter wird angezeigt.
- ✅ **PNG-Transparenz-Support** – Bilder mit Alpha-Kanal werden korrekt dargestellt.

---

## 📂 Projektstruktur

```text
cocktail_pdf_generator/
├── __init__.py              # Öffentliche API
├── recipe_loader.py         # JSON ↔️ TypedDict + Batch-Funktionen
├── image_utils.py           # Bildhandling & PNG-Fix
├── layout.py                # Layout der Rezeptblöcke
├── pdf_single.py            # Einzelnes A5-Rezept
├── pdf_double_a4.py         # Zwei Rezepte (gedreht) auf A4
└── pdf_quadruple_a4.py      # Vier Rezepte (gedreht) auf A4
```

---

## 🧪 Abhängigkeiten

Installiere die benötigten Pakete mit pip:

```bash
pip install reportlab pillow
```

---

## 📄 Rezept-JSON-Format

Jede Rezeptdatei (`*.json`) sollte wie folgt aufgebaut sein:

```json
{
  "title": "Espresso Martini",
  "ingredients": [
    "4 cl Wodka",
    "2 cl Kaffeelikör",
    "2 cl Espresso",
    "Eiswürfel"
  ],
  "steps": [
    "Alle Zutaten in einen Shaker mit Eis geben.",
    "Kräftig schütteln und in ein gekühltes Glas abseihen."
  ],
  "glass": "martini"
}
```

### 🖼 Automatische Bildauswahl

Das Rezeptfeld `"image_path"` ist optional. Falls es fehlt, greift der Generator automatisch auf folgende Logik zurück:

1. **Bild mit gleichem Namen**:
   - Wenn zur JSON-Datei eine Bilddatei mit gleichem Namen im selben Verzeichnis existiert (`.png`, `.jpg`, `.jpeg`, `.gif`), wird diese verwendet.
   - Beispiel: `mojito.json` → `mojito.png`

2. **Glasbild anhand des `"glass"`-Feldes**:
   - Wenn kein eigenes Bild vorhanden ist, wird ein Glasbild aus dem angegebenen `glasses/`-Ordner genutzt.
   - Beispiel: `"glass": "martini"` → `glasses/martini.png`

3. **Platzhalteranzeige**:
   - Wenn weder ein Bild noch ein Glas definiert ist, wird automatisch ein Platzhalter ("Bild fehlt") angezeigt.

💡 Die Glasbilder können frei gewählt und angepasst werden – du kannst z. B. eigene Illustrationen oder SVG‑Renders vorbereiten.


## 🛠 Verwendung

### Einzelne A5-PDFs generieren:

```bash
from cocktail_pdf_generator import generate_pdfs_from_folder

generate_pdfs_from_folder(
    src="rezepte",
    out="pdfs",
    glasses_dir="glasses"
)
```
### Zwei Rezepte quer auf A4 (2×A5):

```bash
from cocktail_pdf_generator import generate_double_a4_sheet

generate_double_a4_sheet(
    recipes_folder="rezepte",
    output_path="cocktails_2xA5.pdf",
    glasses_dir="glasses"
)
```

## 📁 Beispielordnerstruktur

```bash
cocktails/
├── glasses/
│   ├── longdrink.png
│   ├── martini.png
│   └── ...
├── rezepte/
│   ├── mojito.json
│   ├── mojito.jpg
│   ├── caipirinha.json
│   └── ...
├── generate_from_folder.py
└── README.md
```

## 📝 Lizenz

MIT License – feel free to use, share, and modify.