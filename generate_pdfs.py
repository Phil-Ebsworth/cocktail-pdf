from pathlib import Path
from PyPDF2 import PdfMerger

from cocktail_pdf_generator import generate_pdfs_from_folder


def merge_pdfs(pdf_paths: list[Path], output_path: Path) -> None:
    merger = PdfMerger()
    for pdf in pdf_paths:
        merger.append(str(pdf))
    merger.write(str(output_path))
    merger.close()


def main() -> None:
    root = Path(__file__).parent
    rezepte = root / "rezepte"
    out = root / "pdfs"
    out.mkdir(parents=True, exist_ok=True)

    # Einzelne PDFs generieren
    pdfs = generate_pdfs_from_folder(rezepte, output_dir=out)

    print("\nErzeugte PDFs:")
    for path in pdfs:
        print(" •", path.relative_to(root))

    # Sammel-PDF erzeugen
    merged_pdf_path = out / "alle_rezepte_gesamt.pdf"
    merge_pdfs(pdfs, merged_pdf_path)
    print("\nSammel-PDF erstellt:")
    print(" •", merged_pdf_path.relative_to(root))


if __name__ == "__main__":
    main()
