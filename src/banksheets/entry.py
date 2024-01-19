from dataclasses import dataclass
from datetime import datetime
from locale import LC_ALL, atof, setlocale


@dataclass(order=True, frozen=True)
class DataEntry:
    date: datetime
    amount: float
    description: str
    extra_desc: str = ""

    def __post_init__(self):
        setlocale(LC_ALL, "")
        object.__setattr__(self, "date", datetime.strptime(self.date, "%m/%d/%Y"))
        object.__setattr__(self, "amount", atof(self.amount))

    def __str__(self) -> str:
        return (
            f"{self.date.strftime('%m/%d/%Y')}\t"
            f"{self.amount}\t"
            f"{self.description}\t"
            f"{self.extra_desc}"
        )
