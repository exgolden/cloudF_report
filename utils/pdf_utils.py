"""
V3 functions neccesary to run the pdf creation
"""

__version__ = "3.0.0"

from datetime import datetime

from fpdf import FPDF


def create_pdf_report(client_name: str, client_image_path: str):
    """
    Creates a PDF report with sections and manually placed images.

    Args:
        client_name (str): Name of the client.
        client_image_path (str): Path to the client's logo.

    The PDF will be saved with the format "<CLIENT_NAME>_report_<TODAY_DATE>.pdf".
    """
    # Create the PDF instance
    pdf = FPDF()
    pdf.add_page()

    # Set title and date
    today_date = datetime.today().strftime("%Y-%m-%d")
    pdf.set_font("Arial", size=16, style="B")
    # pdf.cell(0, 10, txt=f"Reporte de red: {client_name}", ln=True, align="C")
    pdf.cell(0, 10, txt="Reporte de red: CLIENTE", ln=True, align="C")
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, txt=f"Fecha: {today_date}", ln=True, align="C")
    pdf.ln(10)  # Add space after the title

    # Add header images
    pdf.image("assets/atdac_logo.png", x=10, y=10, w=30)  # Smaller ATDAC logo
    pdf.image(client_image_path, x=160, y=10, w=30)  # Upper right corner
    pdf.ln(10)  # Add space after the logos

    # Section: Estadísticas generales
    pdf.set_font("Arial", size=14, style="B")
    pdf.cell(0, 10, txt="Estadísticas generales", ln=True, align="L")
    pdf.ln(5)  # Add some space after the title

    # Row 1: 4 images horizontally
    y_position_row1 = pdf.get_y()  # Get current y position after the title
    pdf.image("assets/general_stats/bandwidth.png", x=10, y=y_position_row1, w=45, h=20)
    pdf.image("assets/general_stats/requests.png", x=60, y=y_position_row1, w=45, h=20)
    pdf.image("assets/general_stats/views.png", x=110, y=y_position_row1, w=45, h=20)
    pdf.image("assets/general_stats/visitas.png", x=160, y=y_position_row1, w=45, h=20)

    # Row 2: 2 larger images horizontally below row 1
    y_position_row2 = y_position_row1 + 25  # Add space below row 1
    pdf.image("assets/general_stats/table.png", x=5, y=y_position_row2, w=100, h=60)
    pdf.image(
        "assets/general_stats/requests_map.png", x=110, y=y_position_row2, w=100, h=60
    )
    pdf.ln(90)  # Add space after this section

    # Section: Network
    pdf.set_font("Arial", size=14, style="B")
    pdf.cell(0, 10, txt="Network", ln=True, align="L")
    pdf.ln(5)  # Add space after the title
    y_position_network = pdf.get_y()  # Get the current y position for Network images
    pdf.image("assets/network/content_type.png", x=5, y=y_position_network, w=60, h=30)
    pdf.image(
        "assets/network/html_versions.png", x=75, y=y_position_network, w=60, h=30
    )
    pdf.image("assets/network/ssl_content.png", x=145, y=y_position_network, w=60, h=30)
    pdf.ln(30)

    # Seguridad
    pdf.set_font("Arial", size=14, style="B")
    pdf.cell(0, 10, txt="Seguridad", ln=True, align="L")
    pdf.image("assets/security/encrypted_bandwidth.png", x=10, y=210, w=90)
    pdf.image("assets/security/encrypted_requests.png", x=110, y=210, w=90)
    pdf.ln(20)  # Add space after the title

    # Section: Cache
    pdf.set_font("Arial", size=14, style="B")
    pdf.cell(0, 10, txt="Cache", ln=True, align="L")
    pdf.image("assets/cache/cached_bandwidth.png", x=10, y=240, w=90)
    pdf.image("assets/cache/cached_requests.png", x=110, y=240, w=90)
    pdf.ln(15)

    # Section: Errores
    pdf.set_font("Arial", size=14, style="B")
    pdf.cell(0, 10, txt="Errores", ln=True, align="L")
    pdf.image("assets/errors/four_errors.png", x=10, y=270, w=90)
    pdf.image("assets/errors/five_errors.png", x=110, y=270, w=90)

    # Save the PDF
    # file_name = f"{client_name}_report_{today_date}.pdf".replace(" ", "_")
    file_name = "assets/report.pdf"
    pdf.output(file_name)
    print(f"PDF report saved as {file_name}")


# Example Usage
create_pdf_report("ACME Corporation", "assets/ACME_logo.png")
