import os
import institution_parser
import sqlite3


def parse(file_path: str, file_contents):
    institution = institution_parser.decide(file_path, file_contents)
    if institution:
        return institution.report()


def get_data_from_folder(path):
    transactions = []
    for entry in os.scandir(path):
        print(type(entry.path))
        with (open(entry.path)) as f:
            data = parse(entry.path, f)
            if data:
                transactions.extend(data)

    return transactions


def write_to_output(transactions, filename):
    arr = transactions.copy()
    arr.sort()

    with open(os.path.join(os.getcwd(), "output", filename), "w") as f:
        for item in arr:
            f.write(f"{str(item)}\n")


def create_sql_connection():
    connection = None
    with open("tools\schema.sql") as fp:
        connection = sqlite3.connect("output\output.db")
        connection.execute("PRAGMA foreign_keys = 1")
        connection.executescript(fp.read())

    return connection


def insert_descriptions(data_entries, sql_connection):
    to_insert = []
    for datum in data_entries:
        to_insert.append((datum.description,))

    sql_connection.executemany(
        "INSERT OR IGNORE INTO descriptions(name) VALUES (?);", to_insert)
    sql_connection.commit()


def insert_transactions(data_entries, sql_connection):
    to_insert = []
    for datum in data_entries:
        desc_id_query = sql_connection.execute(
            "SELECT description_id FROM descriptions WHERE name=?", (datum.description,))
        query_result = desc_id_query.fetchone()
        if query_result:
            to_insert.append((datum.date.strftime('%Y-%m-%d'), datum.id,
                             datum.amount, query_result[0]))
    sql_connection.executemany(
        "INSERT OR IGNORE INTO transactions(date, transaction_id, amount, description ) VALUES (?, ?, ?, ?);", to_insert)
    sql_connection.commit()


if __name__ == '__main__':
    transaction_data = get_data_from_folder("input")
    sql_conn = create_sql_connection()
    if sql_conn:
        insert_descriptions(transaction_data, sql_conn)
        insert_transactions(transaction_data, sql_conn)
