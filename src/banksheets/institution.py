from abc import ABCMeta, abstractmethod
import csv
from banksheets.entry import DataEntry


class Institution(metaclass=ABCMeta):
    def __init__(self, f, first_line):
        self.data = f
        self.first_line = first_line

    @abstractmethod
    def report(self):
        pass


class BankOfAmericaCreditCard(Institution):
    def report(self):
        return self.fetch_bofa_cc_data()

    def fetch_bofa_cc_data(self):
        reader = csv.reader(self.data)
        results = []
        for row in reader:
            if len(row) > 0:
                try:
                    entry = DataEntry(row)
                    results.append(entry)
                except ValueError:
                    pass
        return results


class BankOfAmerica(Institution):
    def report(self):
        return self.fetch_bofa_check_data()

    def fetch_bofa_check_data(self):
        reader = csv.reader(self.data)
        results = []
        counter = 0
        for row in reader:
            if len(row) > 0 and len(row[2]) > 0:
                try:
                    organized_row = [
                        row[0], None, row[1], "", row[2]]
                    entry = DataEntry(organized_row)
                    results.append(entry)
                except ValueError:
                    pass
            counter += 1
        return results


class WellsFargo(Institution):
    def report(self):
        return self.fetch_wellsfargo_check_data()

    def fetch_wellsfargo_check_data(self):
        reader = csv.reader(self.data)
        results = []
        results.append(self.__parse_first_row(self.first_line))
        counter = 1
        for row in reader:
            if len(row) > 0:
                try:
                    organized_row = [
                        row[0], None, row[4], "", row[1]]
                    entry = DataEntry(organized_row)
                    results.append(entry)
                except ValueError:
                    pass
            counter += 1
        return results

    @staticmethod
    def __parse_first_row(row_data: str) -> DataEntry:
        split_first_row = row_data.split(",")
        organized_row = [split_first_row[0][1:-1], None,
                         split_first_row[4][1:-1], "", split_first_row[1][1:-1]]
        return DataEntry(organized_row)
