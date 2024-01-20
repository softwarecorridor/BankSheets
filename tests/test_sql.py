from sqlite3 import Connection

from pytest import fixture

from banksheets.database import create_sql_connection


@fixture
def sql() -> Connection:
    return create_sql_connection(":memory:")


def test_create(sql: Connection):
    with sql as conn:
        select_tables = "SELECT name FROM sqlite_master WHERE type='table';"
        c = conn.execute(select_tables)
        res = list(map(lambda x: x[0], c.fetchall()))
        assert len(res) == 3
        assert "description" in res
        assert "bank_transaction" in res
        assert "potential_transaction" in res
