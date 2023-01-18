from dataclasses import dataclass
from datetime import datetime


@dataclass
class Issue:
    key: str
    description: str
    created: datetime = datetime.now()
