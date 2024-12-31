from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

class HumanName(BaseModel):
    use: Optional[str] = Field(None, description="usual | official | temp | nickname | anonymous | old | maiden")
    family: Optional[str]
    given: Optional[List[str]]

class PatientSchema(BaseModel):
    resourceType: str = "Patient"
    id: Optional[str]
    active: Optional[bool] = True
    name: List[HumanName]
    gender: Optional[str] = Field(None, description="male | female | other | unknown")
    birthDate: Optional[str]
    deceased: Optional[bool] = False
    meta: dict = Field(
        default_factory=lambda: {
            "versionId": "1",
            "lastUpdated": datetime.utcnow().isoformat()
        }
    ) 
