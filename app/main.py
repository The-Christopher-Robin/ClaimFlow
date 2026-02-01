"""
ClaimFlow Micro-Skills API
Designed for IBM watsonx Orchestrate Integration.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
import os
import uuid
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="ClaimFlow Tools",
    description="Micro-skills for IBM watsonx Agent",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- CONFIGURATION (YOUR PUBLIC URL) ---
# I grabbed this from your screenshot. It MUST be exact for the link to work.
BASE_URL = "https://claimflow-backend.25rar0221uf4.us-south.codeengine.appdomain.cloud"

# --- DATA MODELS ---

class DamageAnalysis(BaseModel):
    damage_type: str
    severity: str
    estimated_cost: float
    confidence: float

class PayoutRequest(BaseModel):
    repair_cost: float
    deductible: float
    policy_id: str

class PayoutResponse(BaseModel):
    final_payout: float
    status: str
    offer_letter_url: str

class PDFRequest(BaseModel):
    claim_id: str
    policy_id: str
    final_amount: float
    damage_type: str

# --- THE SKILLS (Endpoints for Watsonx) ---

@app.get("/")
def health_check():
    """Keep-alive endpoint for IBM Code Engine."""
    return {"status": "ClaimFlow Skills Active", "timestamp": datetime.now().isoformat()}

# SKILL 1: Vision (The Eyes)
@app.post("/tools/analyze-image", response_model=DamageAnalysis, summary="Analyze Car Damage")
async def analyze_image_tool(image_name: str = "crash.jpg"):
    """
    Simulates analyzing a car photo.
    Input: Image filename or URL.
    Output: Damage details and cost estimate.
    """
    logger.info(f"Analyzing image: {image_name}")
    
    # Logic: Return different results based on keywords in the filename
    if "total" in image_name.lower() or "heavy" in image_name.lower():
        return {
            "damage_type": "Major Frontal Collision",
            "severity": "High",
            "estimated_cost": 4500.0,
            "confidence": 0.98
        }
    elif "scratch" in image_name.lower():
        return {
            "damage_type": "Paint Scratch",
            "severity": "Low",
            "estimated_cost": 350.0,
            "confidence": 0.85
        }
    else:
        # Default case
        return {
            "damage_type": "Front Bumper Dent",
            "severity": "Medium",
            "estimated_cost": 850.0,
            "confidence": 0.95
        }

# SKILL 2: Finance (The Calculator)
@app.post("/tools/calculate-payout", response_model=PayoutResponse, summary="Calculate Final Payout")
def calculate_payout_tool(data: PayoutRequest):
    """
    Calculates the final check amount.
    """
    amount = data.repair_cost - data.deductible
    if amount < 0: 
        amount = 0.0
    
    # Generate a Mock Offer ID
    offer_id = f"OFFER-{uuid.uuid4().hex[:6].upper()}"
    
    return {
        "final_payout": amount,
        "status": "Approved" if amount > 0 else "Denied",
        # We point this URL to our new PDF generator endpoint below
        "offer_letter_url": f"{BASE_URL}/api/claims/{offer_id}/pdf"
    }

# SKILL 3: PDF Generator (The Paperwork)
@app.post("/tools/generate-pdf", summary="Generate Offer Letter")
def generate_pdf_tool(data: PDFRequest):
    """
    Generates the official PDF offer letter link.
    """
    # Create a unique ID
    offer_id = uuid.uuid4().hex
    
    # CRITICAL FIX: Return the Full Public URL
    download_link = f"{BASE_URL}/api/claims/{offer_id}/pdf"
    
    return {
        "message": "PDF Generated Successfully",
        "filename": f"claim_{offer_id}.pdf",
        "download_url": download_link
    }

# --- NEW: THE ENDPOINT THAT MAKES THE LINK WORK ---
@app.get("/api/claims/{offer_id}/pdf")
def get_offer_pdf(offer_id: str):
    """
    Serves a text receipt that looks like a PDF for the demo.
    """
    content = f"""
    =========================================
          OFFICIAL CLAIMFLOW DOCUMENT
    =========================================
    
    CLAIM ID: {offer_id}
    DATE:     {datetime.now().strftime("%Y-%m-%d")}
    STATUS:   PROCESSED
    
    -----------------------------------------
    Thank you for using ClaimFlow. 
    Your payout assessment is complete.
    
    Please retain this document for your records.
    
    [Authorized Signature]
    IBM watsonx Orchestrate Agent
    =========================================
    """
    return PlainTextResponse(content)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# ============================================================================
# ORIGINAL MONOLITHIC ENDPOINT - Keep for backward compatibility
# ============================================================================

@app.post("/api/claims/process", response_model=ClaimResponse)
async def process_claim(
    policy_id: str = Form(...),
    image: UploadFile = File(...),
    email: Optional[str] = Form(None)
):
    """
    Process a new claim with image and policy ID.
    
    This endpoint orchestrates the three agents:
    1. Vision Agent - analyzes the damage image
    2. Policy Agent - retrieves policy information
    3. Finance Agent - calculates payout
    
    Also generates a PDF offer letter and sends notifications.
    
    NOTE: For Watsonx integration, use the individual /tools/* endpoints instead.
    """
    try:
        # Generate unique claim ID
        claim_id = str(uuid.uuid4())
        logger.info(f"Processing claim {claim_id} for policy {policy_id}")
        
        # Save uploaded image
        image_path = f"uploads/{claim_id}_{image.filename}"
        with open(image_path, "wb") as f:
            content = await image.read()
            f.write(content)
        
        # Step 1: Vision Agent - Analyze damage
        logger.info(f"Running Vision Agent for claim {claim_id}")
        with open(image_path, "rb") as img_file:
            damage_analysis = await vision_agent.analyze_damage(img_file)
        logger.info(f"Damage analysis complete: {damage_analysis.damage_type}, ${damage_analysis.estimated_cost}")
        
        # Step 2: Policy Agent - Get policy info
        logger.info(f"Running Policy Agent for claim {claim_id}")
        policy_info = await policy_agent.get_policy_info(
            policy_id=policy_id,
            damage_type=damage_analysis.damage_type
        )
        logger.info(f"Policy info retrieved: covered={policy_info.is_covered}")
        
        # Step 3: Finance Agent - Calculate payout
        logger.info(f"Running Finance Agent for claim {claim_id}")
        payout_calculation = await finance_agent.calculate_payout(
            damage_analysis=damage_analysis,
            policy_info=policy_info
        )
        logger.info(f"Payout calculated: ${payout_calculation.payout_amount}, status={payout_calculation.status}")
        
        # Create claim response
        claim_response = ClaimResponse(
            claim_id=claim_id,
            damage_analysis=damage_analysis,
            policy_info=policy_info,
            payout_calculation=payout_calculation,
            created_at=datetime.now()
        )
        
        # Generate PDF offer letter
        logger.info(f"Generating PDF for claim {claim_id}")
        pdf_path = pdf_service.generate_offer_letter(claim_response)
        claim_response.pdf_path = pdf_path
        logger.info(f"PDF generated: {pdf_path}")
        
        # Send notifications
        logger.info(f"Sending notifications for claim {claim_id}")
        notification_results = await notification_service.notify_all(
            claim=claim_response,
            email=email
        )
        logger.info(f"Notifications sent: {notification_results}")
        
        return claim_response
        
    except Exception as e:
        logger.error(f"Error processing claim: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing claim: {str(e)}")


@app.get("/api/claims/{claim_id}/pdf")
async def get_claim_pdf(claim_id: str):
    """Download the PDF offer letter for a claim."""
    # Find the PDF file
    output_dir = "output"
    pdf_files = [f for f in os.listdir(output_dir) if f.startswith(f"claim_{claim_id}_")]
    
    if not pdf_files:
        raise HTTPException(status_code=404, detail="PDF not found")
    
    # Return the most recent PDF if multiple exist
    pdf_file = sorted(pdf_files)[-1]
    pdf_path = os.path.join(output_dir, pdf_file)
    
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=f"claim_{claim_id}_offer.pdf"
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)