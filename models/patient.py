from typing import List, Optional
from datetime import datetime
from bson import ObjectId

class PatientModel:
    def __init__(self, db):
        self.collection = db.patients

    async def create_patient(self, patient_data: dict) -> dict:
        patient_data["meta"] = {
            "versionId": "1",
            "lastUpdated": datetime.utcnow().isoformat()
        }
        result = await self.collection.insert_one(patient_data)
        patient_data["id"] = str(result.inserted_id)
        return patient_data

    async def get_patient(self, patient_id: str) -> Optional[dict]:
        patient = await self.collection.find_one({"_id": ObjectId(patient_id)})
        if patient:
            patient["id"] = str(patient["_id"])
            del patient["_id"]
        return patient
