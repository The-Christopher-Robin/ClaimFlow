"""Main FastAPI application for ClaimFlow."""
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from typing import Optional
import os
import uuid
import logging
import json
from datetime import datetime

from app.models import ClaimResponse, DamageAnalysis, PolicyInfo, PayoutCalculation
from app.agents.vision import VisionAgent
from app.agents.policy import PolicyAgent
from app.agents.finance import FinanceAgent
from app.services.pdf_service import PDFService
from app.services.notification_service import NotificationService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="ClaimFlow API",
    description="Instant Auto-Claims Adjuster API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agents and services
vision_agent = VisionAgent()
policy_agent = PolicyAgent()
finance_agent = FinanceAgent()
pdf_service = PDFService()
notification_service = NotificationService(
    slack_webhook_url=os.getenv("SLACK_WEBHOOK_URL")
)

# Ensure directories exist
os.makedirs("uploads", exist_ok=True)
os.makedirs("output", exist_ok=True)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "message": "ClaimFlow API is running",
        "version": "1.0.0",
        "status": "healthy"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


# ============================================================================
# NEW SKILL ENDPOINTS - For Watsonx Integration
# ============================================================================

@app.post("/tools/analyze_image", response_model=DamageAnalysis)
async def analyze_image(image: UploadFile = File(...)):
    """
    Skill 1: Analyze damage image.
    
    This endpoint only does image analysis and returns damage data.
    It can be called independently by Watsonx as a "Skill".
    
    Input: Image file
    Output: DamageAnalysis with damage_type, severity, estimated_cost, confidence
    """
    try:
        logger.info(f"Analyzing image: {image.filename}")
        
        # Save uploaded image temporarily
        temp_path = f"uploads/temp_{uuid.uuid4()}_{image.filename}"
        with open(temp_path, "wb") as f:
            content = await image.read()
            f.write(content)
        
        # Analyze damage
        with open(temp_path, "rb") as img_file:
            damage_analysis = await vision_agent.analyze_damage(img_file)
        
        # Clean up temp file
        os.remove(temp_path)
        
        logger.info(f"Image analysis complete: {damage_analysis.damage_type}, ${damage_analysis.estimated_cost}")
        return damage_analysis
        
    except Exception as e:
        logger.error(f"Error analyzing image: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error analyzing image: {str(e)}")


@app.post("/tools/calculate_payout", response_model=PayoutCalculation)
async def calculate_payout(
    estimated_cost: float = Form(...),
    damage_type: str = Form(...),
    policy_id: str = Form(...)
):
    """
    Skill 2: Calculate payout based on damage and policy.
    
    This endpoint only does math - it calculates what to pay.
    It can be called independently by Watsonx as a "Skill".
    
    Input: estimated_cost, damage_type, policy_id
    Output: PayoutCalculation with payout_amount and status
    """
    try:
        logger.info(f"Calculating payout for policy {policy_id}, damage ${estimated_cost}")
        
        # Create mock DamageAnalysis for finance calculation
        damage_analysis = DamageAnalysis(
            damage_type=damage_type,
            severity="moderate",  # Default, in real flow would come from image analysis
            estimated_cost=estimated_cost,
            confidence=0.9
        )
        
        # Get policy info
        policy_info = await policy_agent.get_policy_info(
            policy_id=policy_id,
            damage_type=damage_type
        )
        
        # Calculate payout
        payout_calculation = await finance_agent.calculate_payout(
            damage_analysis=damage_analysis,
            policy_info=policy_info
        )
        
        logger.info(f"Payout calculated: ${payout_calculation.payout_amount}, status={payout_calculation.status}")
        return payout_calculation
        
    except Exception as e:
        logger.error(f"Error calculating payout: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error calculating payout: {str(e)}")


@app.post("/tools/generate_pdf", response_model=dict)
async def generate_pdf(
    claim_id: str = Form(...),
    policy_id: str = Form(...),
    damage_type: str = Form(...),
    severity: str = Form(...),
    estimated_cost: float = Form(...),
    deductible: float = Form(...),
    coverage_limit: float = Form(...),
    is_covered: bool = Form(...),
    payout_amount: float = Form(...)
):
    """
    Skill 3: Generate PDF offer letter.
    
    This endpoint only generates the PDF.
    It can be called independently by Watsonx as a "Skill".
    
    Input: All claim details (damage, policy, payout info)
    Output: JSON with pdf_path
    """
    try:
        logger.info(f"Generating PDF for claim {claim_id}")
        
        # Reconstruct the claim response from the input parameters
        damage_analysis = DamageAnalysis(
            damage_type=damage_type,
            severity=severity,
            estimated_cost=estimated_cost,
            confidence=0.9
        )
        
        policy_info = PolicyInfo(
            policy_id=policy_id,
            deductible=deductible,
            coverage_limit=coverage_limit,
            is_covered=is_covered,
            coverage_details="Policy details from Watsonx"
        )
        
        payout_calculation = PayoutCalculation(
            estimated_cost=estimated_cost,
            deductible=deductible,
            payout_amount=payout_amount,
            status="approved" if is_covered else "denied"
        )
        
        claim_response = ClaimResponse(
            claim_id=claim_id,
            damage_analysis=damage_analysis,
            policy_info=policy_info,
            payout_calculation=payout_calculation,
            created_at=datetime.now()
        )
        
        # Generate PDF
        pdf_path = pdf_service.generate_offer_letter(claim_response)
        logger.info(f"PDF generated: {pdf_path}")
        
        return {
            "success": True,
            "pdf_path": pdf_path,
            "claim_id": claim_id
        }
        
    except Exception as e:
        logger.error(f"Error generating PDF: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")


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
