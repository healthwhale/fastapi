import strawberry
from typing import Optional

@strawberry.type
class HumanName:
    family: Optional[str] = None
    given: Optional[list[str]] = None
    prefix: Optional[list[str]] = None
    suffix: Optional[list[str]] = None
    use: Optional[str] = None 