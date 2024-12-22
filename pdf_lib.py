from datetime import datetime

from fpdf import FPDF


def create_report(client_name: str, logo_path: str):
    """
    Creates the basic template for the report
    Args:
        client_name (str): Name of the client for the report.
        logo_path (str): Logo of the client for the report
    """
    # Date of creation
    creation_date = datetime.today().strftime("%d-%m-%Y")
    # Initialization
    pdf = FPDF()
    pdf.add_page()
    # Basic data
    pdf.image(logo_path, x=10, y=8, w=30)
    pdf.set_font("Arial", size=16, style="B")
    pdf.cell(200, 10, txt=f"Reporte de red: {client_name}", ln=True, align="C")
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 10, txt=f"{creation_date}", ln=True, align="L")
    pdf.ln(10)

    # Datos generales
    pdf.set_font("Arial", size=14, style="B")
    pdf.cell(0, 10, txt="Datos generales", ln=True, align="L")
    pdf.ln(10)

    # Mini images (four images horizontally)
    image_paths = [
        "assets/general_stats/1.png",
        "assets/general_stats/2.png",
        "assets/general_stats/3.png",
        "assets/general_stats/4.png",
    ]
    x_offset = 10
    y_offset = pdf.get_y()
    image_width = 45  # Adjust image width for horizontal alignment
    image_height = 30  # Fixed height for mini images
    for image in image_paths:
        pdf.image(image, x=x_offset, y=y_offset, w=image_width, h=image_height)
        x_offset += image_width + 10

    # Move below the mini images
    pdf.ln(image_height + 10)

    # Add map and table
    map_path = "assets/general_stats/map.png"
    map_width = 100
    map_height = 50  # Reduced height for the map to avoid overlap
    table_x_offset = 120  # Set X offset for the table

    # Add map image on the left
    map_y_position = pdf.get_y()
    pdf.image(map_path, x=10, y=map_y_position, w=map_width, h=map_height)

    # Adjust table position to align next to the map and below mini images
    table_y_position = map_y_position  # Keep the table aligned with the map
    pdf.set_xy(table_x_offset, table_y_position)

    # Add table on the right
    pdf.set_font("Arial", size=10)
    table_data = [
        ["Column 1", "Column 2", "Column 3"],  # Header row
        ["Row 1", "Value 1", "Value 2"],
        ["Row 2", "Value 1", "Value 2"],
        ["Row 3", "Value 1", "Value 2"],
        ["Row 4", "Value 1", "Value 2"],
        ["Row 5", "Value 1", "Value 2"],
        ["Row 6", "Value 1", "Value 2"],
        ["Row 7", "Value 1", "Value 2"],
        ["Row 8", "Value 1", "Value 2"],
        ["Row 9", "Value 1", "Value 2"],
        ["Row 10", "Value 1", "Value 2"],
    ]
    cell_widths = [30, 40, 40]  # Column widths
    cell_height = 8  # Row height

    # Draw table
    for row in table_data:
        for i, cell in enumerate(row):
            pdf.cell(cell_widths[i], cell_height, cell, border=1, align="C")
        pdf.ln(cell_height)  # Move to the next row

    # Save the PDF
    file_name = f"reporte_red_{creation_date}.pdf"
    pdf.output(file_name)
    print(f"PDF report '{file_name}' generated successfully.")


# Usage
create_report("ACME Corporation", "./assets/ACME_logo.png")
