from cocktail_pdf_generator import create_cocktail_pdf

create_cocktail_pdf(
    title="Debug-Test",
    ingredients=["Test-Zutat"],
    steps=["Step 1"],
    glass="martini",        # oder tumbler, longdrink …
    svg_dir="svg",          # falls Ordner anders heißt
    output_path="debug.pdf"
)
