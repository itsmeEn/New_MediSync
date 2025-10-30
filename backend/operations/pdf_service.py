import io
from typing import Dict, Any
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from datetime import datetime
from django.core.mail import EmailMessage
from django.conf import settings

try:
    from PyPDF2 import PdfReader, PdfWriter
except Exception:  # pragma: no cover
    PdfReader = None
    PdfWriter = None


def generate_records_pdf(patient_name: str, patient_email: str, details: Dict[str, Any]) -> bytes:
    """
    Generate a simple PDF containing requested medical records summary using reportlab.
    Returns raw PDF bytes (unencrypted).
    """
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    y = height - 1 * inch
    c.setFont("Helvetica-Bold", 16)
    c.drawString(1 * inch, y, "MediSync Medical Records")
    y -= 0.4 * inch

    c.setFont("Helvetica", 11)
    c.drawString(1 * inch, y, f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    y -= 0.3 * inch
    c.drawString(1 * inch, y, f"Patient: {patient_name}")
    y -= 0.25 * inch
    c.drawString(1 * inch, y, f"Email: {patient_email}")
    y -= 0.4 * inch

    c.setFont("Helvetica-Bold", 12)
    c.drawString(1 * inch, y, "Request Details")
    y -= 0.3 * inch
    c.setFont("Helvetica", 11)

    def draw_wrapped(text: str, x: float, y: float, max_width: float) -> float:
        from reportlab.pdfbase.pdfmetrics import stringWidth
        words = text.split()
        line = ""
        for w in words:
            if stringWidth(line + (" " if line else "") + w, "Helvetica", 11) > max_width:
                c.drawString(x, y, line)
                y -= 14
                line = w
            else:
                line = (line + " " + w) if line else w
        if line:
            c.drawString(x, y, line)
            y -= 14
        return y

    for key, value in details.items():
        val = value
        if isinstance(value, (dict, list)):
            import json
            val = json.dumps(value, indent=2)[:4000]
        c.setFont("Helvetica-Bold", 11)
        c.drawString(1 * inch, y, f"- {key}:")
        y -= 14
        c.setFont("Helvetica", 11)
        y = draw_wrapped(str(val), 1.2 * inch, y, width - 2.2 * inch)
        y -= 4
        if y < 1 * inch:
            c.showPage()
            y = height - 1 * inch

    c.showPage()
    c.save()
    return buffer.getvalue()


def encrypt_pdf_aes256(pdf_bytes: bytes, password: str) -> bytes:
    """
    Encrypt PDF bytes using AES-256 (requires PyPDF2 >= 3.0.0).
    """
    if PdfReader is None or PdfWriter is None:
        raise RuntimeError("PyPDF2 is required for AES-256 PDF encryption. Please install it.")

    reader = PdfReader(io.BytesIO(pdf_bytes))
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)

    # AES-256 encryption
    writer.encrypt(user_password=password, owner_password=password, use_128bit=False, permissions={})

    out_buf = io.BytesIO()
    writer.write(out_buf)
    return out_buf.getvalue()


def send_encrypted_pdf_to_patient(patient_email: str, encrypted_pdf: bytes, filename: str, message: str = None):
    subject = "Your Requested Medical Records (Encrypted PDF)"
    body = message or (
        "Attached is your encrypted medical records PDF. "
        "Use the provided password format to open it."
    )
    email = EmailMessage(subject, body, getattr(settings, 'DEFAULT_FROM_EMAIL', None), [patient_email])
    email.attach(filename, encrypted_pdf, 'application/pdf')
    email.send(fail_silently=False)