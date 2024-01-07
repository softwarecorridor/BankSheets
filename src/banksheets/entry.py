from dataclasses import dataclass
from datetime import datetime


@dataclass(order=True, frozen=True)
class DataEntry:
    date: datetime
    amount: float
    description: str
    extra_desc: str = ""

    def __post_init__(self):
        object.__setattr__(self, "date", datetime.strptime(self.date, "%m/%d/%Y"))
        object.__setattr__(self, "amount", float(self.amount))

    def __str__(self) -> str:
        return (
            f"{self.date.strftime('%m/%d/%Y')}\t"
            f"{self.amount}\t"
            f"{self.description}\t"
            f"{self.extra_desc}"
        )
