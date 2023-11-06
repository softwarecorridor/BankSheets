from datetime import datetime
from dataclasses import dataclass

@dataclass(order=True, frozen = True)
class DataEntry:
        date: datetime
        data_id: int
        description: str
        extra_description:str
        amount: float

        def __post_init__(self):
            object.__setattr__(self, 'date', datetime.strptime(self.date, "%m/%d/%Y"))

        def __str__(self) -> str:
            return f"{self.date.strftime('%m/%d/%Y')}\t{self.amount}\t{self.description}\t{self.extra_description}"
