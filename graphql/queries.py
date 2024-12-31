import strawberry
from typing import Optional, List
from app.models.patient import PatientModel
from app.database import db

@strawberry.type
class HumanName:
    use: Optional[str]
    family: Optional[str]
    given: Optional[List[str]]

@strawberry.type
class Patient:
    id: str
    resourceType: str
    active: Optional[bool]
    name: List[HumanName]
    gender: Optional[str]
    birthDate: Optional[str]
    deceased: Optional[bool]

@strawberry.type
class Query:
    @strawberry.field
    async def patient(self, id: str) -> Optional[Patient]:
        patient_model = PatientModel(db)
        patient = await patient_model.get_patient(id)
        return Patient(**patient) if patient else None 
