from unittest import TestCase
from banksheets.entry import DataEntry


class TestDataEntry(TestCase):

    def test_parse(self):
        data = ["02/11/2021", "491091136970529302963377", "Popeyes", "Frankfurt        IL ", "-10.02"]
        under_test = DataEntry(*data)
        self.assertEqual(under_test.date.strftime("%m/%d/%Y"), data[0])
        self.assertEqual(under_test.amount, data[4])
        self.assertEqual(under_test.description, data[2])

    def test_fail_parse(self):
        data = ["Posted Date", "Reference Number", "Payee", "Address", "Amount"]
        self.assertRaises(ValueError, DataEntry, *data)

    def test_order_simple(self):
        data_1 = ["02/11/2021", "772566432424956988368115", "RALLY", "Frankfurt        IL ", "-10.02"]
        data_2 = ["04/11/2021", "013389515160328025198240", "RALLY", "Frankfurt        IL ", "-10.02"]
        data_3 = ["03/11/2021", "970623919179822408572244", "RALLY", "Frankfurt        IL ", "-10.02"]

        ut_1 = DataEntry(*data_1)
        ut_2 = DataEntry(*data_2)
        ut_3 = DataEntry(*data_3)
        under_test = [ut_1, ut_2, ut_3]
        under_test.sort()
        self.assertEqual(under_test, [ut_1, ut_3, ut_2])

    def test_equality(self):
        data_1 = ["01/04/2021", "491298688675177918190816", "RALLY", "PARIS       WA ", "-13.59"]
        data_2 = ["01/04/2021", "728955390304896999654613", "RALLY", "PARIS       WA ", "13.59"]
        data_3 = ["01/02/2021", "240042477354516622049970", "RALLY", "PARIS       WA ", "-13.59"]

        ut_1 = DataEntry(*data_1)
        ut_2 = DataEntry(*data_2)
        ut_3 = DataEntry(*data_3)
        self.assertNotEqual(ut_1, ut_2)
        self.assertNotEqual(ut_1, ut_3)
        self.assertNotEqual(ut_2, ut_3)

    def test_inequality(self):
        data_1 = ["02/11/2021", "740387467554245504019699", "RALLY", "SEATTLE        NY ", "-10.02"]
        data_2 = ["03/11/2021", "559212285141588665464875", "RALLY", "SEATTLE        NY ", "-10.02"]

        ut_1 = DataEntry(*data_1)
        ut_2 = DataEntry(*data_2)
        self.assertNotEqual(ut_1, ut_2)

    def test_lt(self):
        data_1 = ["02/11/2021", "640385912017924538143779", "RALLY", "SEATTLE        NY ", "-10.02"]
        data_2 = ["03/11/2021", "077418787182427846248758", "RALLY", "SEATTLE        NY ", "-10.02"]

        ut_1 = DataEntry(*data_1)
        ut_2 = DataEntry(*data_2)
        self.assertLess(ut_1, ut_2)
