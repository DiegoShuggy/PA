from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm

print("✅ ReportLab instalado correctamente")

# Crear PDF simple
c = canvas.Canvas("test_reportlab.pdf", pagesize=A4)
c.drawString(100, 750, "Reporte InA - Duoc UC")
c.drawString(100, 730, "✅ PDF generado con ReportLab")
c.drawString(100, 710, "Funciona perfectamente en Windows")
c.save()

print("✅ PDF generado: test_reportlab.pdf")