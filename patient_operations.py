from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
import uuid
import pymongo

class Identifier(BaseModel):
    system: str
    value: str
    type: str
    expiry: Optional[str] = None

class Name(BaseModel):
    use: str
    family: str
    given: List[str]

class Address(BaseModel):
    flat: Optional[str] = None
    building: Optional[str] = None
    roadName: Optional[str] = None
    roadNumber: Optional[str] = None
    block: Optional[str] = None
    area: Optional[str] = None
    governorate: Optional[str] = None
    country: Optional[str] = None

class Meta(BaseModel):
    versionId: str
    lastUpdated: str
    source: str

class Patient(BaseModel):
    id: Optional[str] = None
    resourceType: str = "Patient"
    meta: Optional[Meta] = None
    identifiers: List[Identifier]
    name: List[Name]
    address: Optional[Address] = None
    birthDate: str
    gender: str
    active: bool = True
    name_0_family: Optional[str] = None
    name_0_given: Optional[str] = None
    address_country: Optional[str] = None
    address_governorate: Optional[str] = None
    address_area: Optional[str] = None
    mrn: Optional[str] = None
    identifier_passport: Optional[str] = None

def generate_meta():
    new_id = str(uuid.uuid4())
    return {
        "versionId": str(uuid.uuid4().int)[:4],
        "lastUpdated": datetime.utcnow().isoformat(),
        "source": f"urn:uuid:{new_id}"
    }

def prepare_patient_for_storage(patient: Patient):
    if not patient.id:
        patient.id = str(uuid.uuid4())
    
    patient_dict = patient.dict()
    patient_dict["_id"] = patient.id
    
    if patient.name and len(patient.name) > 0:
        patient_dict["name_0_family"] = patient.name[0].family
        patient_dict["name_0_given"] = patient.name[0].given[0] if patient.name[0].given else None
    
    if patient.address:
        patient_dict["address_country"] = patient.address.country
        patient_dict["address_governorate"] = patient.address.governorate
        patient_dict["address_area"] = patient.address.area
    
    for identifier in patient.identifiers:
        if identifier.type == "MRN":
            patient_dict["mrn"] = identifier.value
        elif identifier.type == "PASSPORT":
            patient_dict["identifier_passport"] = identifier.value
    
    return patient_dict
