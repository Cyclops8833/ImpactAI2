from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Optional
import os
from datetime import datetime
import uuid
import logging
import mysql.connector
from dotenv import load_dotenv
import time
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors

# Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
app = FastAPI(title="Print Quote Assistant API", version="1.0.0")

ALLOWED_ORIGINS = os.environ.get('ALLOWED_ORIGINS', '*').split(',')
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DB setup
load_dotenv()
db = mysql.connector.connect(
    host=os.getenv("MYSQL_HOST"),
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
    database=os.getenv("MYSQL_DATABASE")
)
cursor = db.cursor(dictionary=True)

# Models
class QuoteRequest(BaseModel):
    client_name: str = Field(..., min_length=1)
    product_type: str
    finished_size: str
    page_count: int
    sidedness: str
    cover_stock: Optional[str]
    text_stock: Optional[str]
    finishing_options: List[str] = []
    quantity: int
    delivery_location: str
    special_requirements: Optional[str]
    ink_type: str
    pms_colors: bool = False
    pms_color_count: int = 1

class QuoteResponse(BaseModel):
    quote_id: str
    client_name: str
    product_type: str
    estimated_cost: float
    created_at: datetime
    status: str

class QuoteDetail(QuoteResponse):
    finished_size: str
    page_count: int
    sidedness: str
    cover_stock: Optional[str]
    text_stock: Optional[str]
    finishing_options: List[str]
    quantity: int
    delivery_location: str
    special_requirements: Optional[str]
    ink_type: str
    pms_colors: bool
    pms_color_count: int

# Quote cost logic
def calculate_quote_cost(quote_data: QuoteRequest) -> float:
    base_cost = {
        'Booklet': 2.5, 'Brochure': 1.8, 'Flyer': 0.5, 'Signage': 15,
        'Business Cards': 0.25, 'Posters': 8, 'Banners': 25,
        'Stickers': 1.2, 'Catalogues': 3.5, 'Newsletters': 1.6
    }.get(quote_data.product_type, 2.0)
    size_mult = {
        'A6': 0.8, 'A5': 1.0, 'A4': 1.2, 'A3': 1.8, 'DL': 0.9, 'Custom': 1.5
    }.get(quote_data.finished_size.split(' ')[0], 1.0)
    page_mult = max(1.0, quote_data.page_count * 0.3)
    sided_mult = 1.6 if quote_data.sidedness == 'double' else 1.0
    stock_cost = 0.0
    if quote_data.cover_stock:
        if '300gsm' in quote_data.cover_stock or '350gsm' in quote_data.cover_stock:
            stock_cost += 0.3
        elif '400gsm' in quote_data.cover_stock:
            stock_cost += 0.5
    if quote_data.text_stock:
        if '150gsm' in quote_data.text_stock or '170gsm' in quote_data.text_stock:
            stock_cost += 0.2
        elif '200gsm' in quote_data.text_stock or '250gsm' in quote_data.text_stock:
            stock_cost += 0.35
    finish_cost = sum({
        'Matt Laminate': 0.4, 'Gloss Laminate': 0.4, 'Spot UV': 0.8,
        'Foiling (Gold)': 1.2, 'Foiling (Silver)': 1.0, 'Foiling (Other)': 1.3,
        'Embossing': 1.5, 'Debossing': 1.5, 'Die Cutting': 2.0,
        'Perfect Binding': 1.8, 'Saddle Stitching': 0.6
    }.get(f, 0.0) for f in quote_data.finishing_options)
    ink_cost = {'CMYK': 0.15, 'Black Only': 0.05, 'Custom': 0.25}.get(quote_data.ink_type, 0.1)
    pms_cost = quote_data.pms_color_count * 0.35 if quote_data.pms_colors else 0
    delivery_cost = {
        'Metro Melbourne': 15, 'Regional Victoria': 25, 'Interstate (NSW)': 35,
        'Interstate (QLD)': 40, 'Interstate (SA)': 35, 'Interstate (WA)': 50,
        'Interstate (TAS)': 45, 'Interstate (NT)': 55, 'Interstate (ACT)': 30
    }.get(quote_data.delivery_location, 30)
    discount = 0.15 if quote_data.quantity >= 1000 else 0.1 if quote_data.quantity >= 500 else 0.05 if quote_data.quantity >= 100 else 0.0
    unit_cost = base_cost * size_mult * page_mult * sided_mult + stock_cost + finish_cost + ink_cost + pms_cost
    total_cost = unit_cost * quote_data.quantity * (1 - discount) + delivery_cost
    return round(total_cost, 2)

def generate_quote_pdf(quote_data):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5 * inch)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=20, alignment=1, textColor=colors.HexColor('#4F46E5'))
    heading = ParagraphStyle('Heading', parent=styles['Heading2'], fontSize=14, textColor=colors.HexColor('#1F2937'))
    story = [Paragraph("PRINT QUOTE", title_style), Spacer(1, 20)]
    story.append(Paragraph("Quote Information", heading))
    info = [['Quote ID:', quote_data['quote_id']], ['Date:', quote_data['created_at'].strftime('%d/%m/%Y')],
            ['Client:', quote_data['client_name']], ['Status:', quote_data['status'].title()],
            ['Estimated Cost:', f"${quote_data['estimated_cost']:.2f}"]]
    story.append(Table(info, colWidths=[2*inch, 4*inch]))
    story.append(Spacer(1, 20))
    story.append(Paragraph("Product Specifications", heading))
    specs = [['Product Type:', quote_data['product_type']],
             ['Finished Size:', quote_data['finished_size']],
             ['Page Count:', str(quote_data['page_count'])],
             ['Printing:', quote_data['sidedness'].title() + ' Sided'],
             ['Quantity:', str(quote_data['quantity'])],
             ['Ink Type:', quote_data['ink_type']]]
    if quote_data['pms_colors']:
        specs.append(['PMS Colors:', str(quote_data['pms_color_count'])])
    if quote_data['cover_stock']:
        specs.append(['Cover Stock:', quote_data['cover_stock']])
    if quote_data['text_stock']:
        specs.append(['Text Stock:', quote_data['text_stock']])
    story.append(Table(specs, colWidths=[2*inch, 4*inch]))
    if quote_data['finishing_options']:
        story.append(Paragraph("Finishing Options", heading))
        story.append(Paragraph(", ".join(quote_data['finishing_options']), styles['Normal']))
    story.append(Paragraph("Delivery Location: " + quote_data['delivery_location'], styles['Normal']))
    if quote_data['special_requirements']:
        story.append(Paragraph("Special Requirements: " + quote_data['special_requirements'], styles['Normal']))
    story.append(Spacer(1, 30))
    story.append(Paragraph("Total Estimated Cost", heading))
    story.append(Paragraph(f"<b>${quote_data['estimated_cost']:.2f}</b>", styles['Normal']))
    doc.build(story)
    buffer.seek(0)
    return buffer

@app.post("/api/quotes", response_model=QuoteResponse)
async def create_quote(quote_request: QuoteRequest):
    try:
        quote_id = str(uuid.uuid4())[:8].upper()
        estimated_cost = calculate_quote_cost(quote_request)
        cursor.execute("""
            INSERT INTO quotes (
                quote_id, client_name, product_type, finished_size, page_count, sidedness,
                cover_stock, text_stock, finishing_options, quantity, delivery_location,
                special_requirements, ink_type, pms_colors, pms_color_count, estimated_cost,
                created_at, status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            quote_id, quote_request.client_name, quote_request.product_type,
            quote_request.finished_size, quote_request.page_count, quote_request.sidedness,
            quote_request.cover_stock, quote_request.text_stock,
            ",".join(quote_request.finishing_options), quote_request.quantity,
            quote_request.delivery_location, quote_request.special_requirements,
            quote_request.ink_type, quote_request.pms_colors, quote_request.pms_color_count,
            estimated_cost, datetime.utcnow(), "pending"
        ))
        db.commit()
        return QuoteResponse(quote_id=quote_id, client_name=quote_request.client_name,
            product_type=quote_request.product_type, estimated_cost=estimated_cost,
            created_at=datetime.utcnow(), status="pending")
    except Exception as e:
        logger.error(f"Insert error: {str(e)}")
        raise HTTPException(status_code=500, detail="DB insert error")

@app.get("/api/quotes/{quote_id}", response_model=QuoteDetail)
async def get_quote(quote_id: str):
    cursor.execute("SELECT * FROM quotes WHERE quote_id = %s", (quote_id,))
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Quote not found")
    row["finishing_options"] = row["finishing_options"].split(",") if row["finishing_options"] else []
    return row

@app.get("/api/quotes", response_model=List[QuoteResponse])
async def list_quotes():
    cursor.execute("SELECT quote_id, client_name, product_type, estimated_cost, created_at, status FROM quotes")
    rows = cursor.fetchall()
    return rows

@app.put("/api/quotes/{quote_id}/status")
async def update_status(quote_id: str, status: str):
    cursor.execute("UPDATE quotes SET status = %s WHERE quote_id = %s", (status, quote_id))
    db.commit()
    return {"message": "Status updated"}

@app.delete("/api/quotes/{quote_id}")
async def delete_quote(quote_id: str):
    cursor.execute("DELETE FROM quotes WHERE quote_id = %s", (quote_id,))
    db.commit()
    return {"message": "Quote deleted"}

@app.get("/api/quotes/{quote_id}/export")
async def export_quote_pdf(quote_id: str):
    cursor.execute("SELECT * FROM quotes WHERE quote_id = %s", (quote_id,))
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Quote not found")
    row["finishing_options"] = row["finishing_options"].split(",") if row["finishing_options"] else []
    pdf_stream = generate_quote_pdf(row)
    return StreamingResponse(pdf_stream, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=quote_{quote_id}.pdf"})

@app.get("/api/health")
def health_check():
    try:
        cursor.execute("SELECT 1")
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "fail", "error": str(e)}

@app.get("/")
async def root():
    return {"message": "Print Quote Assistant API", "status": "running"}
