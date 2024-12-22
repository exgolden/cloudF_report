"""
Library to create the report
"""

from datetime import datetime

from fpdf import FPDF


def create_pdf_report(client_name: str, client_image_path: str):
    """
    Creates a PDF report with a title and two images in the upper corners.

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
    pdf.cell(0, 10, txt=f"Reporte de red: {client_name}", ln=True, align="C")
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, txt=f"Fecha: {today_date}", ln=True, align="C")
    pdf.ln(20)  # Add space after the title

    # Add images
    pdf.image("assets/atdac_logo.png", x=10, y=10, w=40)  # Upper left corner
    pdf.image(client_image_path, x=160, y=10, w=40)  # Upper right corner

    # Save the PDF
    file_name = f"{client_name}_report_{today_date}.pdf".replace(" ", "_")
    pdf.output(file_name)
    print(f"PDF report saved as {file_name}")


# Example Usage
create_pdf_report("ACME Corporation", "assets/ACME_logo.png")
