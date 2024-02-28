from sqlite3 import Connection

import pytest
from pytest import fixture, raises

from banksheets.entry import DataEntry
from banksheets.sql_commands import (
    create_sql_connection,
    get_duplicate_records,
    insert_descriptions,
    insert_potential_transactions,
    preserve_potential,
    remove_potential,
)

# TODO: just make duplicate_view check for bank_tranasction (deal with ids instead of items)
# TODO: make front end figure out if the user tries to insert multiple copies of the same thing


@fixture
def sql() -> Connection:
    return create_sql_connection(":memory:")


@fixture
def generic_entry() -> DataEntry:
    return DataEntry("01/01/2023", "100.25", "Company A", "City1, Street A")


@fixture
def generic_entry1() -> DataEntry:
    return DataEntry("01/01/2024", "100.25", "Company A", "City1, Street A")


def test_create(sql: Connection):
    with sql as conn:
        select_tables = "SELECT name FROM sqlite_master WHERE type='table';"
        c = conn.execute(select_tables)
        res = list(map(lambda x: x[0], c.fetchall()))
        assert len(res) == 3
        assert "description" in res
        assert "bank_transaction" in res
        assert "potential_transaction" in res


def test_description_none(sql: Connection):
    with raises(TypeError):
        with sql as conn:
            insert_descriptions(None, conn)


def test_description_single(sql: Connection, generic_entry: DataEntry):
    with sql as conn:
        insert_descriptions([generic_entry], conn)
        description = "SELECT name FROM description;"
        c = conn.execute(description)
        res = c.fetchone()[0]
        assert generic_entry.description == res


def test_description_empty(sql: Connection):
    with sql as conn:
        insert_descriptions([], conn)
        description = "SELECT name FROM description;"
        c = conn.execute(description)
        res = c.fetchone()
        assert res is None


def test_insert_potential_transactions_empty(sql: Connection):
    with sql as conn:
        insert_descriptions([], conn)
        insert_potential_transactions([], conn)
        description = "SELECT name FROM description;"
        c = conn.execute(description)
        res = c.fetchall()
        assert len(res) == 0

        potential = "SELECT * FROM potential_transaction;"
        c = conn.execute(potential)
        res = c.fetchall()
        assert len(res) == 0


def test_insert_potential_transactions_none(sql: Connection):
    with sql as conn:
        with raises(TypeError):
            insert_descriptions(None, conn)
            insert_potential_transactions(None, conn)


def test_insert_potential_transactions_list_none(sql: Connection):
    with sql as conn:
        insert_descriptions([None], conn)
        insert_potential_transactions([None], conn)

        potential = "SELECT * FROM potential_transaction;"
        c = conn.execute(potential)
        res = c.fetchall()
        assert len(res) == 0


def test_insert_potential_transactions_no_duplicates(
    sql: Connection, generic_entry: DataEntry
):
    with sql as conn:
        insert_descriptions([generic_entry], conn)
        insert_potential_transactions([generic_entry], conn)
        description = "SELECT name FROM description;"
        c = conn.execute(description)
        res = c.fetchone()[0]
        assert generic_entry.description == res

        potential = "SELECT * FROM potential_transaction;"
        c = conn.execute(potential)
        res = c.fetchall()
        assert len(res) == 1
        assert generic_entry.date.strftime("%d/%m/%Y") == res[0][0]
        assert generic_entry.amount == float(res[0][1])


def test_insert_potential_transactions_duplicates(
    sql: Connection, generic_entry: DataEntry, generic_entry1: DataEntry
):
    with sql as conn:
        insert_descriptions([generic_entry], conn)
        insert_potential_transactions([generic_entry, generic_entry1], conn)
        potential = "SELECT * FROM potential_transaction;"
        c = conn.execute(potential)
        res = c.fetchall()
        assert len(res) == 2


def test_get_duplicates_one_duplicate(sql: Connection, generic_entry: DataEntry):
    with sql as conn:
        insert_descriptions([generic_entry], conn)
        insert_potential_transactions([generic_entry], conn)
        records = get_duplicate_records(conn)
        assert len(records) == 1
        assert generic_entry.date.strftime("%d/%m/%Y") == records[0][0]
        assert generic_entry.amount == float(records[0][1])
        assert generic_entry.description == records[0][2]


def test_get_duplicates_multiple_same(sql: Connection, generic_entry: DataEntry):
    with sql as conn:
        insert_descriptions([generic_entry], conn)
        insert_potential_transactions(
            [generic_entry, generic_entry, generic_entry], conn
        )
        records = get_duplicate_records(conn)
        assert len(records) == 1
        assert generic_entry.date.strftime("%d/%m/%Y") == records[0][0]
        assert generic_entry.amount == float(records[0][1])
        assert generic_entry.description == records[0][2]


def test_get_duplicates_multiple_different(sql: Connection, generic_entry: DataEntry):
    with sql as conn:
        insert_descriptions([generic_entry], conn)
        insert_potential_transactions(
            [generic_entry, generic_entry, generic_entry], conn
        )
        records = get_duplicate_records(conn)
        assert len(records) == 1
        assert generic_entry.date.strftime("%d/%m/%Y") == records[0][0]
        assert generic_entry.amount == float(records[0][1])
        assert generic_entry.description == records[0][2]


def test_get_duplicates_no_duplicates(sql: Connection, generic_entry: DataEntry):
    with sql as conn:
        insert_descriptions([generic_entry], conn)
        insert_potential_transactions([generic_entry], conn)
        records = get_duplicate_records(conn)
        assert len(records) == 0


def test_preserve_potential(sql: Connection, generic_entry: DataEntry):
    with sql as conn:
        insert_descriptions([generic_entry], conn)
        insert_potential_transactions([generic_entry], conn)
        preserve_potential(conn)

        # check we saved
        statement = "SELECT from bank_transaction;"
        res = conn.execute(statement)
        records = res.fetchall()
        assert len(records) == 1

        # check we dumped potential
        statement = "SELECT from potential_transaction;"
        res = conn.execute(statement)
        records = res.fetchall()
        assert len(records) == 0


def test_remove_from_potential_single(sql: Connection, generic_entry: DataEntry):
    with sql as conn:
        insert_descriptions([generic_entry], conn)
        insert_potential_transactions([generic_entry], conn)
        remove_potential(conn)

        statement = "SELECT from potential_transaction;"
        res = conn.execute(statement)
        records = res.fetchall()
        assert len(records) == 0


def test_remove_from_potential_multiple(
    sql: Connection, generic_entry: DataEntry, generic_entry1: DataEntry
):
    with sql as conn:
        insert_descriptions([generic_entry], conn)
        insert_potential_transactions([generic_entry], conn)
        remove_potential(conn)

        statement = "SELECT from potential_transaction;"
        res = conn.execute(statement)
        records = res.fetchall()
        assert len(records) == 1


# def test_get_duplicates_potential_duplicates(sql: Connection, generic_entry: DataEntry):
#     with sql as conn:
#         insert_descriptions([generic_entry], conn)
#         insert_potential_transactions([generic_entry, generic_entry], conn)
#         records = get_duplicate_records(conn)
#         assert len(records) == 1
#         assert generic_entry.date.strftime("%d/%m/%Y") == records[0][0]
#         assert generic_entry.amount == float(records[0][1])
#         assert generic_entry.description == records[0][2]
#         assert 0 == records[0][3]
#         assert 1 == records[0][4]


# def test_preserve_potential_transaction(sql):
#     with sql as conn:
#         insert_potential_transactions([generic_entry], conn)
#         description = "SELECT name FROM description;"
#         c = conn.execute(description)
#         res = c.fetchone()[0]
#         assert generic_entry.description == res

# @pytest.mark.skip()
# def test_get_duplicates_combo_duplicates(sql: Connection, generic_entry: DataEntry):
#     with sql as conn:
#         insert_descriptions([generic_entry], conn)
#         insert_potential_transactions([generic_entry, generic_entry], conn)
#         records = get_duplicate_records(conn)

#         assert len(records) == 1
#         assert generic_entry.date.strftime("%d/%m/%Y") == records[0][0]
#         assert generic_entry.amount == float(records[0][1])
#         assert generic_entry.description == records[0][2]
#         assert 1 == records[0][3]
#         assert 1 == records[0][4]


# @pytest.mark.skip()
# def test_get_duplicates_commited_duplicates(sql: Connection, generic_entry: DataEntry):
#     with sql as conn:
#         insert_descriptions([generic_entry], conn)
#         insert_potential_transactions([generic_entry, generic_entry], conn)
#         records = get_duplicate_records(conn)

#         assert len(records) == 1
#         assert generic_entry.date.strftime("%d/%m/%Y") == records[0][0]
#         assert generic_entry.amount == float(records[0][1])
#         assert generic_entry.description == records[0][2]
#         assert 1 == records[0][3]
#         assert 0 == records[0][4]


# def test_clear_potential(sql: Connection, generic_entry: DataEntry):
#     with sql as conn:
#         insert_descriptions([generic_entry], conn)
#         insert_potential_transactions([generic_entry, generic_entry], conn)
#         clear_potential_records(conn)
#         potential = "SELECT * FROM potential_transaction;"
#         c = conn.execute(potential)
#         res = c.fetchall()
#         assert len(res) == 0


# def test_delete_potential(sql: Connection, generic_entry: DataEntry):
#     with sql as conn:
#         insert_descriptions([generic_entry], conn)
#         insert_potential_transactions([generic_entry, generic_entry], conn)
#         remove_from_potential_transaction([generic_entry], conn)
#         potential = "SELECT * FROM potential_transaction;"
#         c = conn.execute(potential)
#         res = c.fetchall()
#         assert len(res) == 1


# def test_mark_duplicates_to_preserver():
#     pass


# @pytest.mark.skip()
# def test_add_double_duplicate_keep_both():
#     pass


# @pytest.mark.skip()
# def test_add_double_duplicate_keep_one():
#     pass
