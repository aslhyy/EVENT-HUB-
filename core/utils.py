"""
Utilidades generales para EventHub.
"""
import qrcode
from io import BytesIO
from django.core.files import File
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
import random
import string


def generate_qr_code(data: str) -> File:
    """
    Genera un código QR a partir de un string.
    
    Args:
        data: Información a codificar en el QR
        
    Returns:
        File: Archivo de imagen del QR
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Guardar en BytesIO
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    return File(buffer, name=f'qr_{data[:10]}.png')


def generate_ticket_code(length: int = 12) -> str:
    """
    Genera un código único para tickets.
    
    Args:
        length: Longitud del código
        
    Returns:
        str: Código generado
    """
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


def generate_ticket_pdf(ticket):
    """
    Genera un PDF para un ticket.
    
    Args:
        ticket: Instancia del modelo Ticket
        
    Returns:
        File: Archivo PDF del ticket
    """
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Título
    p.setFont("Helvetica-Bold", 24)
    p.drawString(100, height - 100, "EventHub Ticket")
    
    # Información del evento
    p.setFont("Helvetica", 12)
    y_position = height - 150
    
    p.drawString(100, y_position, f"Evento: {ticket.ticket_type.event.title}")
    y_position -= 20
    
    p.drawString(100, y_position, f"Tipo: {ticket.ticket_type.name}")
    y_position -= 20
    
    p.drawString(100, y_position, f"Código: {ticket.code}")
    y_position -= 20
    
    p.drawString(100, y_position, f"Comprador: {ticket.buyer.get_full_name() or ticket.buyer.username}")
    y_position -= 20
    
    if ticket.ticket_type.event.start_date:
        p.drawString(100, y_position, f"Fecha: {ticket.ticket_type.event.start_date.strftime('%Y-%m-%d %H:%M')}")
        y_position -= 20
    
    if ticket.ticket_type.event.venue:
        p.drawString(100, y_position, f"Lugar: {ticket.ticket_type.event.venue.name}")
        y_position -= 40
    
    # QR Code
    if ticket.qr_code:
        try:
            qr_image = ImageReader(ticket.qr_code.path)
            p.drawImage(qr_image, 100, y_position - 200, width=200, height=200)
        except:
            pass
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    return File(buffer, name=f'ticket_{ticket.code}.pdf')