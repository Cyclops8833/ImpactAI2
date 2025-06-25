from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Optional
import os
from datetime import datetime
import uuid
from pymongo import MongoClient
import logging
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Print Quote Assistant API", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = MongoClient(MONGO_URL)
db = client.print_quotes
quotes_collection = db.quotes

# Pydantic models
class QuoteRequest(BaseModel):
    client_name: str = Field(..., min_length=1, description="Client name")
    product_type: str = Field(..., description="Type of product to print")
    finished_size: str = Field(..., description="Finished size of the product")
    page_count: int = Field(..., gt=0, description="Number of pages")
    sidedness: str = Field(..., description="Single or double sided")
    cover_stock: Optional[str] = Field(None, description="Cover stock type")
    text_stock: Optional[str] = Field(None, description="Text stock type")
    finishing_options: List[str] = Field(default=[], description="List of finishing options")
    quantity: int = Field(..., gt=0, description="Quantity to print")
    delivery_location: str = Field(..., description="Delivery location")
    special_requirements: Optional[str] = Field(None, description="Special requirements")
    ink_type: str = Field(..., description="Ink type (CMYK, Black Only, Custom)")
    pms_colors: bool = Field(default=False, description="PMS colors required")
    pms_color_count: int = Field(default=1, description="Number of PMS colors")

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

# Quote calculation logic
def calculate_quote_cost(quote_data: QuoteRequest) -> float:
    """
    Calculate estimated cost based on quote parameters
    This is a simplified calculation - in production this would be more complex
    """
    base_cost = 0.0
    
    # Base cost by product type
    product_costs = {
        'Booklet': 2.50,
        'Brochure': 1.80,
        'Flyer': 0.50,
        'Signage': 15.00,
        'Business Cards': 0.25,
        'Posters': 8.00,
        'Banners': 25.00,
        'Stickers': 1.20,
        'Catalogues': 3.50,
        'Newsletters': 1.60
    }
    
    base_cost = product_costs.get(quote_data.product_type, 2.00)
    
    # Size multiplier
    size_multipliers = {
        'A6': 0.8,
        'A5': 1.0,
        'A4': 1.2,
        'A3': 1.8,
        'DL': 0.9,
        'Custom': 1.5
    }
    
    size_key = quote_data.finished_size.split(' ')[0]  # Extract size prefix
    size_multiplier = size_multipliers.get(size_key, 1.0)
    
    # Page count multiplier
    page_multiplier = max(1.0, quote_data.page_count * 0.3)
    
    # Sidedness multiplier
    sidedness_multiplier = 1.6 if quote_data.sidedness == 'double' else 1.0
    
    # Stock costs
    stock_cost = 0.0
    if quote_data.cover_stock:
        if '300gsm' in quote_data.cover_stock or '350gsm' in quote_data.cover_stock:
            stock_cost += 0.30
        elif '400gsm' in quote_data.cover_stock:
            stock_cost += 0.50
    
    if quote_data.text_stock:
        if '150gsm' in quote_data.text_stock or '170gsm' in quote_data.text_stock:
            stock_cost += 0.20
        elif '200gsm' in quote_data.text_stock or '250gsm' in quote_data.text_stock:
            stock_cost += 0.35
    
    # Finishing costs
    finishing_costs = {
        'Matt Laminate': 0.40,
        'Gloss Laminate': 0.40,
        'Spot UV': 0.80,
        'Foiling (Gold)': 1.20,
        'Foiling (Silver)': 1.00,
        'Foiling (Other)': 1.30,
        'Embossing': 1.50,
        'Debossing': 1.50,
        'Die Cutting': 2.00,
        'Perfect Binding': 1.80,
        'Saddle Stitching': 0.60
    }
    
    finishing_cost = sum(finishing_costs.get(option, 0.0) for option in quote_data.finishing_options)
    
    # Ink costs
    ink_costs = {
        'CMYK': 0.15,
        'Black Only': 0.05,
        'Custom': 0.25
    }
    
    ink_cost = ink_costs.get(quote_data.ink_type, 0.10)
    
    # PMS color costs
    pms_cost = 0.0
    if quote_data.pms_colors:
        pms_cost = quote_data.pms_color_count * 0.35
    
    # Delivery costs
    delivery_costs = {
        'Metro Melbourne': 15.00,
        'Regional Victoria': 25.00,
        'Interstate (NSW)': 35.00,
        'Interstate (QLD)': 40.00,
        'Interstate (SA)': 35.00,
        'Interstate (WA)': 50.00,
        'Interstate (TAS)': 45.00,
        'Interstate (NT)': 55.00,
        'Interstate (ACT)': 30.00
    }
    
    delivery_cost = delivery_costs.get(quote_data.delivery_location, 30.00)
    
    # Quantity discount
    if quote_data.quantity >= 1000:
        quantity_discount = 0.15
    elif quote_data.quantity >= 500:
        quantity_discount = 0.10
    elif quote_data.quantity >= 100:
        quantity_discount = 0.05
    else:
        quantity_discount = 0.0
    
    # Calculate total
    unit_cost = base_cost * size_multiplier * page_multiplier * sidedness_multiplier + stock_cost + finishing_cost + ink_cost + pms_cost
    total_print_cost = unit_cost * quote_data.quantity
    discounted_cost = total_print_cost * (1 - quantity_discount)
    total_cost = discounted_cost + delivery_cost
    
    return round(total_cost, 2)

# API endpoints
@app.get("/")
async def root():
    return {"message": "Print Quote Assistant API", "status": "running"}

@app.post("/api/quotes", response_model=QuoteResponse)
async def create_quote(quote_request: QuoteRequest):
    """Create a new quote"""
    try:
        # Generate unique quote ID
        quote_id = str(uuid.uuid4())[:8].upper()
        
        # Calculate estimated cost
        estimated_cost = calculate_quote_cost(quote_request)
        
        # Create quote document
        quote_doc = {
            "quote_id": quote_id,
            "client_name": quote_request.client_name,
            "product_type": quote_request.product_type,
            "finished_size": quote_request.finished_size,
            "page_count": quote_request.page_count,
            "sidedness": quote_request.sidedness,
            "cover_stock": quote_request.cover_stock,
            "text_stock": quote_request.text_stock,
            "finishing_options": quote_request.finishing_options,
            "quantity": quote_request.quantity,
            "delivery_location": quote_request.delivery_location,
            "special_requirements": quote_request.special_requirements,
            "estimated_cost": estimated_cost,
            "created_at": datetime.utcnow(),
            "status": "pending"
        }
        
        # Insert into database
        result = quotes_collection.insert_one(quote_doc)
        
        if result.inserted_id:
            logger.info(f"Quote created successfully: {quote_id}")
            return QuoteResponse(
                quote_id=quote_id,
                client_name=quote_request.client_name,
                product_type=quote_request.product_type,
                estimated_cost=estimated_cost,
                created_at=quote_doc["created_at"],
                status="pending"
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to create quote")
            
    except Exception as e:
        logger.error(f"Error creating quote: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/quotes", response_model=List[QuoteResponse])
async def get_quotes(limit: int = 50, offset: int = 0):
    """Get all quotes with pagination"""
    try:
        quotes = list(quotes_collection.find(
            {},
            {
                "quote_id": 1,
                "client_name": 1,
                "product_type": 1,
                "estimated_cost": 1,
                "created_at": 1,
                "status": 1,
                "_id": 0
            }
        ).sort("created_at", -1).skip(offset).limit(limit))
        
        return [QuoteResponse(**quote) for quote in quotes]
        
    except Exception as e:
        logger.error(f"Error fetching quotes: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/quotes/{quote_id}", response_model=QuoteDetail)
async def get_quote_detail(quote_id: str):
    """Get detailed quote information"""
    try:
        quote = quotes_collection.find_one({"quote_id": quote_id}, {"_id": 0})
        
        if not quote:
            raise HTTPException(status_code=404, detail="Quote not found")
        
        return QuoteDetail(**quote)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching quote detail: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.put("/api/quotes/{quote_id}/status")
async def update_quote_status(quote_id: str, status: str):
    """Update quote status"""
    try:
        valid_statuses = ["pending", "approved", "rejected", "completed"]
        if status not in valid_statuses:
            raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
        
        result = quotes_collection.update_one(
            {"quote_id": quote_id},
            {"$set": {"status": status, "updated_at": datetime.utcnow()}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Quote not found")
        
        return {"message": f"Quote status updated to {status}"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating quote status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.delete("/api/quotes/{quote_id}")
async def delete_quote(quote_id: str):
    """Delete a quote"""
    try:
        result = quotes_collection.delete_one({"quote_id": quote_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Quote not found")
        
        return {"message": "Quote deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting quote: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        quotes_collection.find_one()
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow(),
            "database": "connected"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Service unavailable")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)