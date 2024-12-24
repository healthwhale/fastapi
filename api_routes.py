from fastapi import FastAPI, HTTPException, Query, Body
from typing import List, Optional
from pymongo.errors import DuplicateKeyError
from .db_connection import collection
from .patient_operations import Patient, generate_meta, prepare_patient_for_storage

app = FastAPI(title="FHIR Patient API")

@app.post("/Patient", response_model=Patient)
async def create_patient(patient: Patient):
    patient.meta = Meta(**generate_meta())
    patient_dict = prepare_patient_for_storage(patient)
    
    try:
        await collection.insert_one(patient_dict)
        return patient_dict
    except DuplicateKeyError:
        raise HTTPException(status_code=400, detail="Patient with this ID already exists")

@app.get("/Patient/{patient_id}", response_model=Patient)
async def read_patient(patient_id: str):
    patient = await collection.find_one({"_id": patient_id})
    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

@app.put("/Patient/{patient_id}", response_model=Patient)
async def update_patient(patient_id: str, patient: Patient):
    patient.id = patient_id
    patient.meta = Meta(**generate_meta())
    patient_dict = prepare_patient_for_storage(patient)
    
    result = await collection.replace_one({"_id": patient_id}, patient_dict)
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient_dict

@app.patch("/Patient/{patient_id}", response_model=Patient)
async def patch_patient(patient_id: str, updates: dict = Body(...)):
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
    result = await collection.delete_one({"_id": patient_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Patient not found")
    return {"status": "success", "message": "Patient deleted"}

@app.get("/Patient", response_model=List[Patient])
async def search_patients(
    name: Optional[str] = Query(None),
    identifier: Optional[str] = Query(None),
    gender: Optional[str] = Query(None),
    birthdate: Optional[str] = Query(None),
    _count: Optional[int] = Query(10, alias="count"),
    _offset: Optional[int] = Query(0, alias="offset")
):
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

@app.on_event("startup")
async def create_indexes():
    await collection.create_index("name_0_family")
    await collection.create_index("name_0_given")
    await collection.create_index("mrn")
    await collection.create_index("identifier_passport")
    await collection.create_index("gender")
    await collection.create_index("birthDate")
