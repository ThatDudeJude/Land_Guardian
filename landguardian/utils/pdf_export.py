from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from datetime import datetime
import os

def generate_parcels_pdf(parcels, filename):
    """
    Generate a PDF report for land parcels.

    Args:
        parcels: List of LandParcel objects to include in the report
        filename: Output filename for the PDF

    Returns:
        None (saves PDF to specified filename)
    """
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter

    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, height - 100, "LandGuardian Parcel Report")

    # Subtitle
    c.setFont("Helvetica", 12)
    c.drawString(100, height - 130, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    c.drawString(100, height - 150, f"Total Parcels: {len(parcels)}")

    y = height - 180
    for i, parcel in enumerate(parcels):
        if y < 100:  # New page if running out of space
            c.showPage()
            y = height - 100

        c.setFont("Helvetica-Bold", 12)
        c.drawString(100, y, f"{i+1}. {parcel.name}")
        y -= 20

        c.setFont("Helvetica", 10)
        c.drawString(120, y, f"Location: {parcel.location}")
        y -= 15
        c.drawString(120, y, f"Soil Quality: {parcel.soil_quality}/10")
        y -= 15
        c.drawString(120, y, f"Vegetation Cover: {parcel.vegetation_cover}/10")
        y -= 15
        c.drawString(120, y, f"Health Score: {parcel.health_score}%")
        y -= 15
        c.drawString(120, y, f"Risk Level: {parcel.risk_label}")
        y -= 25

    c.save()