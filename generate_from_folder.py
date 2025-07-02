"""CLI‑Skript: baue auf einen Rutsch alle PDFs aus dem Rezepte‑Ordner."""

from pathlib import Path

from cocktail_pdf_generator import generate_pdfs_from_folder


def main() -> None:
    root = Path(__file__).parent
    rezepte = root / "rezepte"
    out = root / "pdfs"
    out.mkdir(parents=True, exist_ok=True)

    pdfs = generate_pdfs_from_folder(rezepte, output_dir=out)
    print("\nErzeugte PDFs:")
    for path in pdfs:
        print(" •", path.relative_to(root))


if __name__ == "__main__":
    main()
