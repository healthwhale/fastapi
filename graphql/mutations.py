import strawberry
from typing import Optional, List
from app.models.patient import PatientModel
from app.database import db
from app.schemas.patient import PatientSchema
from app.types.human_name import HumanName
from app.types.patient import Patient

@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_patient(
        self,
        name: List[HumanName],
        gender: Optional[str] = None,
        birthDate: Optional[str] = None,
        active: Optional[bool] = True
    ) -> Patient:
        patient_data = {
            "resourceType": "Patient",
            "name": [n.__dict__ for n in name],
            "gender": gender,
            "birthDate": birthDate,
            "active": active
        }
        
        # Validate data using Pydantic schema
        validated_data = PatientSchema(**patient_data).dict()
        
        patient_model = PatientModel(db)
        created_patient = await patient_model.create_patient(validated_data)
        return Patient(**created_patient) 
