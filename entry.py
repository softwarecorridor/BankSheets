from datetime import datetime


class DataEntry:
    def __init__(self, data_blob: list) -> None:
        self.date = datetime.strptime(data_blob[0], "%m/%d/%Y")
        self.amount = data_blob[4]
        self.description = data_blob[2]
        self.id = data_blob[1]
        self.__invert_amount__()

    def __invert_amount__(self):
        if self.amount.startswith("-"):
            self.amount = self.amount[1:]
        else:
            self.amount = f"-{self.amount}"

    def __str__(self) -> str:
        return f"{self.date.strftime('%m/%d/%Y')}\t{self.amount}\t{self.description}"

    def __lt__(self, other):
        return self.date < other.date

    def __gt__(self, other):
        return self.date > other.date

    def __le__(self, other):
        return self.date <= other.date

    def __ge__(self, other):
        return self.date >= other.date

    def __eq__(self, other):
        return self.date == other.date and self.amount == other.amount and self.description == self.description

    def __repr__(self):
        return f"DataEntry({str(self)})"
