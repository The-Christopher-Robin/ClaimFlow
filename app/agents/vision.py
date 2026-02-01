"""Vision Agent - Mocked image analysis for damage assessment."""
from app.models import DamageAnalysis
from typing import BinaryIO
import random


class VisionAgent:
    """Mock vision agent that analyzes damage images."""
    
    def __init__(self):
        self.damage_types = ["Collision", "Hail", "Flood", "Fire", "Vandalism"]
        self.severities = ["minor", "moderate", "severe", "total_loss"]
    
    async def analyze_damage(self, image_file: BinaryIO) -> DamageAnalysis:
        """
        Mock analysis of damage image.
        
        In a real implementation, this would use computer vision APIs
        like IBM Watson Visual Recognition or similar.
        """
        # Mock analysis - in production would analyze actual image
        damage_type = random.choice(self.damage_types)
        severity = random.choice(self.severities)
        
        # Estimate cost based on severity
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
            severity=severity,
            estimated_cost=estimated_cost,
            confidence=round(random.uniform(0.85, 0.99), 2)
        )
