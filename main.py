# main.py
from fastapi import FastAPI, HTTPException, Query, Body
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import uuid
from typing import List, Optional
from pydantic import BaseModel, Field
import pymongo

# Initialize FastAPI app
app = FastAPI(title="FHIR Patient API")

# MongoDB connection
MONGODB_URL = "mongodb://mongo:UmxHXTOOXKBaiFQUnsawgcTQSmwkOHBw@autorack.proxy.rlwy.net:54479"
client = AsyncIOMotorClient(MONGODB_URL)
db = client.fhir_db
collection = db.rest_patient

# Pydantic models for request/response validation
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

# Helper function to generate FHIR metadata
def generate_meta():
    new_id = str(uuid.uuid4())
    return {
        "versionId": str(uuid.uuid4().int)[:4],
        "lastUpdated": datetime.utcnow().isoformat(),
        "source": f"urn:uuid:{new_id}"
    }

# Helper function to transform Patient for storage
def prepare_patient_for_storage(patient: Patient):
    if not patient.id:
        patient.id = str(uuid.uuid4())
    
    patient_dict = patient.dict()
    patient_dict["_id"] = patient.id
    
    # Add flattened fields for easier querying
    if patient.name and len(patient.name) > 0:
        patient_dict["name_0_family"] = patient.name[0].family
        patient_dict["name_0_given"] = patient.name[0].given[0] if patient.name[0].given else None
    
    if patient.address:
        patient_dict["address_country"] = patient.address.country
        patient_dict["address_governorate"] = patient.address.governorate
        patient_dict["address_area"] = patient.address.area
    
    # Extract MRN and Passport
    for identifier in patient.identifiers:
        if identifier.type == "MRN":
            patient_dict["mrn"] = identifier.value
        elif identifier.type == "PASSPORT":
            patient_dict["identifier_passport"] = identifier.value
    
    return patient_dict

# FHIR API Endpoints

@app.post("/Patient", response_model=Patient)
async def create_patient(patient: Patient):
    """Create a new Patient resource"""
    patient.meta = Meta(**generate_meta())
    patient_dict = prepare_patient_for_storage(patient)
    
    try:
        await collection.insert_one(patient_dict)
        return patient_dict
    except pymongo.errors.DuplicateKeyError:
        raise HTTPException(status_code=400, detail="Patient with this ID already exists")

@app.get("/Patient/{patient_id}", response_model=Patient)
async def read_patient(patient_id: str):
    """Read a specific Patient resource by ID"""
    patient = await collection.find_one({"_id": patient_id})
    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

@app.put("/Patient/{patient_id}", response_model=Patient)
async def update_patient(patient_id: str, patient: Patient):
    """Update an entire Patient resource"""
    patient.id = patient_id
    patient.meta = Meta(**generate_meta())
    patient_dict = prepare_patient_for_storage(patient)
    
    result = await collection.replace_one({"_id": patient_id}, patient_dict)
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient_dict

@app.patch("/Patient/{patient_id}", response_model=Patient)
async def patch_patient(patient_id: str, updates: dict = Body(...)):
    """Partially update a Patient resource"""
    # Generate new metadata for the update
    updates["meta"] = generate_meta()
    
    result = await collection.update_one(
        {"_id": patient_id},
        {"$set": updates}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    updated_patient = await collection.find_one({"_id": patient_id})
    return updated_patient

@app.delete("/Patient/{patient_id}")
async def delete_patient(patient_id: str):
    """Delete a Patient resource"""
    result = await collection.delete_one({"_id": patient_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Patient not found")
    return {"status": "success", "message": "Patient deleted"}

# FHIR Search Operations
@app.get("/Patient", response_model=List[Patient])
async def search_patients(
    name: Optional[str] = Query(None),
    identifier: Optional[str] = Query(None),
    gender: Optional[str] = Query(None),
    birthdate: Optional[str] = Query(None),
    _count: Optional[int] = Query(10, alias="count"),
    _offset: Optional[int] = Query(0, alias="offset")
):
    """Search for Patient resources with various parameters"""
    query = {}
    
    if name:
        query["$or"] = [
            {"name_0_family": {"$regex": name, "$options": "i"}},
            {"name_0_given": {"$regex": name, "$options": "i"}}
        ]
    
    if identifier:
        query["$or"] = [
            {"mrn": identifier},
            {"identifier_passport": identifier}
        ]
    
    if gender:
        query["gender"] = gender
    
    if birthdate:
        query["birthDate"] = birthdate

    cursor = collection.find(query).skip(_offset).limit(_count)
    patients = await cursor.to_list(length=_count)
    return patients

# Add indexes for better query performance
@app.on_event("startup")
async def create_indexes():
    await collection.create_index("name_0_family")
    await collection.create_index("name_0_given")
    await collection.create_index("mrn")
    await collection.create_index("identifier_passport")
    await collection.create_index("gender")
    await collection.create_index("birthDate")

# Requirements:
# pip install fastapi uvicorn motor pydantic pymongo
