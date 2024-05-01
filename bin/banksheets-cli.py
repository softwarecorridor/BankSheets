import click

from banksheets.sql_commands import (
    clear_potential,
    create_sql_connection,
    get_descriptions_missing_alias,
    insert_descriptions,
    insert_potential_transactions,
    preserve_potential,
    remove_potential,
)
from banksheets.ui.common import (
    check_and_convert_source,
    convert_output,
    get_data,
    get_duplicate_groups,
)


def _check_source(path: str):
    try:
        source_path = check_and_convert_source(path)
        return source_path
    except (FileNotFoundError, TypeError) as e:
        raise click.BadArgumentUsage(f"{e}")


def _query_user(db) -> None:
    to_delete_list = []
    for group in get_duplicate_groups(db):
        entry_count = len(group[0])
        is_done = False
        while not is_done:
            val = input(
                f"Duplicated input:\n{group[2]}."
                f"\nAlready present in db: {group[1]}"
                f"\nInput number of new copies to keep (max: {entry_count}):"
            )
            num_to_keep = -1
            try:
                num_to_keep = int(val)
            except ValueError:
                print(f"{val} is not a number")
            if 0 <= num_to_keep <= entry_count:
                num_to_keep = entry_count - num_to_keep
                to_delete_list.extend(group[0][:num_to_keep])
                is_done = True
            else:
                print(f"{num_to_keep} is not in range")

    remove_potential(db, to_delete_list)


def _query_list_of_missing_descriptions(db) -> None:
    for item in get_descriptions_missing_alias(db):
        print(item[0])


@click.group()
def cli():
    """
    Banksheets is a tool for dealing with bank transactions in a quick manner that
    doesn't rely on internet traffic.
    """
    pass


@click.command()
@click.option(
    "--source",
    prompt="Input data source",
    help="Specify the input data source (directory or CSV file)",
    type=click.Path(exists=True, file_okay=True, dir_okay=True),
)
@click.option(
    "--output",
    prompt="Output database",
    help="Specify the output database location (directory or file)",
)
def insert(source, output):
    """Insert entries"""
    input_src = _check_source(source)
    output_src = convert_output(output)
    transaction_data = get_data(input_src)
    with create_sql_connection(output_src) as db:
        insert_descriptions(transaction_data, db)
        insert_potential_transactions(transaction_data, db)
        _query_user(db)
        preserve_potential(db)
        clear_potential(db)


@click.group()
def alias():
    """
    Add aliases to descriptions
    """
    pass


@alias.command(help="List all existing descriptions without an alias")
@click.option(
    "--source",
    prompt="Input data source",
    help="Specify the input data source (database only)",
    type=click.Path(exists=True, file_okay=True),
)
def missinglist(source):
    with create_sql_connection(source) as db:
        _query_list_of_missing_descriptions(db)


cli.add_command(alias)
cli.add_command(insert)

if __name__ == "__main__":
    cli()
