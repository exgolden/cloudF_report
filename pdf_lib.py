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
    # Add a title
    pdf.set_font("Arial", size=16, style="B")
    pdf.cell(200, 10, txt=f"Reporte de red: {client_name}", ln=True, align="C")

    # Add dummy data
    pdf.set_font("Arial", size=12)
    pdf.ln(20)  # Add some space
    dummy_data = [
        "Network Status: Stable",
        "Total Data Transferred: 1.2TB",
        "Average Latency: 45ms",
        "Downtime: 0.01%",
    ]
    for line in dummy_data:
        pdf.cell(200, 10, txt=line, ln=True, align="L")

    # Save the PDF
    pdf.output(f"reporte_red_{creation_date}.pdf")
    print("PDF report generated successfully.")


# Usage
create_report(client_name="ACME Corporation")
