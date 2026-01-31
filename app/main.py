"""Main FastAPI application for ClaimFlow."""
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from typing import Optional
import os
import uuid
import logging
from datetime import datetime

from app.models import ClaimResponse
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
