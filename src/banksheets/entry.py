from datetime import datetime
from dataclasses import dataclass

@dataclass(order=True, frozen = True)
class DataEntry:
        date: datetime
        data_id: int
        description: str
        amount: float

        def __post_init__(self):
            self.date = datetime.strptime(self.t, "%Y-%m-%d")

        def __str__(self) -> str:
            return f"{self.date.strftime('%m/%d/%Y')}\t{self.amount}\t{self.description}"

