from __future__ import annotations
from institution import BankOfAmerica
from institution import BankOfAmericaCreditCard
from institution import WellsFargo


def decide(file_path: str, file_contents):
    current = file_contents.readline().strip()
    if current == "Posted Date,Reference Number,Payee,Address,Amount":
        return BankOfAmericaCreditCard(file_contents, current)
    elif current == "Description,,Summary Amt.":
        return BankOfAmerica(file_contents, current)
    elif file_path.startswith("input\\Checking") and len(current.split(",")) == 5:
        return WellsFargo(file_contents, current)
