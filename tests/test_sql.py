from sqlite3 import Connection

from pytest import fixture, raises

from banksheets.database import create_sql_connection, insert_descriptions
from banksheets.entry import DataEntry


@fixture
def sql() -> Connection:
    return create_sql_connection(":memory:")


@fixture
def generic_entry() -> DataEntry:
    return DataEntry("01/01/2023", "100.25", "Company A", "City1, Street A")


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
