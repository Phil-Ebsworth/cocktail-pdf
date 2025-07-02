from cocktail_pdf_generator import generate_double_a4_sheet
from cocktail_pdf_generator import generate_quadruple_a4_sheet

generate_double_a4_sheet(
    recipes_folder="rezepte",
    output_path=".\pdfs\cocktails_zwei_auf_a4.pdf",
    glasses_dir="glasses"      # falls du den Glasordner umbenannt hast
)