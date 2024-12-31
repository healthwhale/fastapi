import strawberry
from typing import Optional, List
from .human_name import HumanName

@strawberry.type
class Patient:
    id: str
    resourceType: str = "Patient"
    name: List[HumanName]
    gender: Optional[str] = None
    birthDate: Optional[str] = None
    active: Optional[bool] = True 
