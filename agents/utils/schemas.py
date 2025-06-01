from pydantic import BaseModel
from typing import Optional, List, Dict

class Event(BaseModel):
    article: Dict
    features: Optional[Dict]
    use_cases: Optional[Dict]
    industry: Optional[str]
    companies: Optional[List[Dict]]
    meta: Dict
