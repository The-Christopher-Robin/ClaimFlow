from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from typing import Optional, BinaryIO
import uuid
import logging
import random
import io
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "https://claimflow-backend.25rar0221uf4.us-south.codeengine.appdomain.cloud"

class DamageAnalysis(BaseModel):
    damage_type: str
    severity: str
    estimated_cost: float
    confidence: float

class PolicyInfo(BaseModel):
    policy_id: str
    deductible: float
    coverage_limit: float
    is_covered: bool
    coverage_details: str

class PayoutCalculation(BaseModel):
    estimated_cost: float
    deductible: float
    payout_amount: float
    status: str

class PayoutRequest(BaseModel):
    repair_cost: float
    deductible: float
    policy_id: str
    coverage_limit: Optional[float] = 50000.0

class PayoutResponse(BaseModel):
    final_payout: float
    status: str
    offer_letter_url: str

class PDFRequest(BaseModel):
    claim_id: str
    policy_id: str
    final_amount: float
    damage_type: str

class VisionAgent:
    def __init__(self):
        self.damage_types = ["Collision", "Hail", "Flood", "Fire", "Vandalism"]
        self.severities = ["minor", "moderate", "severe", "total_loss"]
    
    async def analyze_damage(self, image_file: BinaryIO, filename_hint: str = "") -> DamageAnalysis:
        name_lower = filename_hint.lower()
        
        if "total" in name_lower or "heavy" in name_lower:
            return DamageAnalysis(
                damage_type="Major Frontal Collision",
                severity="Total Loss",
                estimated_cost=4500.0,
                confidence=0.98
            )
        elif "scratch" in name_lower:
            return DamageAnalysis(
                damage_type="Paint Scratch",
                severity="Minor",
                estimated_cost=350.0,
                confidence=0.85
            )

        damage_type = random.choice(self.damage_types)
        severity = random.choice(self.severities)
        
        cost_ranges = {
            "minor": (500, 2000),
            "moderate": (2000, 8000),
            "severe": (8000, 20000),
            "total_loss": (20000, 50000)
        }
        
        min_cost, max_cost = cost_ranges[severity]
        estimated_cost = round(random.uniform(min_cost, max_cost), 2)
        
        return DamageAnalysis(
            damage_type=damage_type,
            severity=severity.replace("_", " ").title(),
            estimated_cost=estimated_cost,
            confidence=round(random.uniform(0.85, 0.99), 2)
        )

class PolicyAgent:
    def __init__(self):
        self.policies = {
            "POL001": {
                "deductible": 500.0,
                "coverage_limit": 50000.0,
                "covered_damages": ["collision", "hail", "flood", "fire"]
            },
            "POL002": {
                "deductible": 1000.0,
                "coverage_limit": 100000.0,
                "covered_damages": ["collision", "hail", "flood", "fire", "vandalism"]
            },
            "POL003": {
                "deductible": 250.0,
                "coverage_limit": 25000.0,
                "covered_damages": ["collision", "hail"]
            }
        }
    
    async def get_policy_info(self, policy_id: str, damage_type: str) -> PolicyInfo:
        policy = self.policies.get(policy_id, {
            "deductible": 500.0,
            "coverage_limit": 50000.0,
            "covered_damages": ["collision", "hail", "flood", "fire"]
        })
        
        damage_lower = damage_type.lower()
        is_covered = any(covered in damage_lower for covered in policy["covered_damages"])
        
        if is_covered:
            coverage_details = f"Damage type '{damage_type}' is covered under policy {policy_id}."
        else:
            coverage_details = f"Damage type '{damage_type}' is NOT covered."
        
        return PolicyInfo(
            policy_id=policy_id,
            deductible=policy["deductible"],
            coverage_limit=policy["coverage_limit"],
            is_covered=is_covered,
            coverage_details=coverage_details
        )

class FinanceAgent:
    async def calculate_payout(self, damage_analysis: DamageAnalysis, policy_info: PolicyInfo) -> PayoutCalculation:
        estimated_cost = damage_analysis.estimated_cost
        deductible = policy_info.deductible
        
        if not policy_info.is_covered:
            payout_amount = 0.0
            status = "denied_not_covered"
        else:
            payout_before_limit = max(0, estimated_cost - deductible)
            payout_amount = min(payout_before_limit, policy_info.coverage_limit)
            
            if payout_amount > 0:
                status = "Approved"
            else:
                status = "Denied (Below Deductible)"
        
        return PayoutCalculation(
            estimated_cost=estimated_cost,
            deductible=deductible,
            payout_amount=round(payout_amount, 2),
            status=status
        )

app = FastAPI(
    title="ClaimFlow Tools",
    description="Micro-skills for IBM watsonx Agent",
    version="4.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

vision_agent = VisionAgent()
finance_agent = FinanceAgent()
policy_agent = PolicyAgent()

@app.get("/")
def health_check():
    return {"status": "ClaimFlow Agents Active", "timestamp": datetime.now().isoformat()}

@app.post("/tools/analyze-image", response_model=DamageAnalysis)
async def analyze_image_tool(image_name: str = "crash.jpg"):
    logger.info(f"Vision Tool called for: {image_name}")
    
    dummy_file = io.BytesIO(b"fake_image_bytes")
    
    result = await vision_agent.analyze_damage(dummy_file, filename_hint=image_name)
    return result

@app.post("/tools/calculate-payout", response_model=PayoutResponse)
async def calculate_payout_tool(data: PayoutRequest):
    temp_policy = PolicyInfo(
        policy_id=data.policy_id,
        deductible=data.deductible,
        coverage_limit=data.coverage_limit or 50000.0,
        is_covered=True,
        coverage_details="Verified by Policy Agent"
    )
    
    temp_damage = DamageAnalysis(
        damage_type="Collision",
        severity="Unknown",
        estimated_cost=data.repair_cost,
        confidence=1.0
    )
    
    result = await finance_agent.calculate_payout(temp_damage, temp_policy)
    
    offer_id = uuid.uuid4().hex[:8].upper()
    
    return {
        "final_payout": result.payout_amount,
        "status": result.status,
        "offer_letter_url": f"{BASE_URL}/api/claims/{offer_id}/pdf"
    }

@app.post("/tools/generate-pdf")
def generate_pdf_tool(data: PDFRequest):
    offer_id = uuid.uuid4().hex[:8]
    return {
        "message": "PDF Generated",
        "filename": f"claim_{offer_id}.pdf",
        "download_url": f"{BASE_URL}/api/claims/{offer_id}/pdf"
    }

@app.get("/api/claims/{offer_id}/pdf")
def get_offer_pdf(offer_id: str):
    content = f"""
    =========================================
          OFFICIAL CLAIMFLOW RECEIPT
    =========================================
    
    CLAIM ID: {offer_id}
    DATE:     {datetime.now().strftime("%Y-%m-%d")}
    STATUS:   APPROVED
    
    -----------------------------------------
    Thank you for using ClaimFlow. 
    Your payout assessment is complete.
    
    [Authorized Signature]
    IBM watsonx Orchestrate Agent
    =========================================
    """
    return PlainTextResponse(content)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)