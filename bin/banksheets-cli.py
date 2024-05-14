import click

from banksheets.sql_commands import (
    clear_potential,
    create_sql_connection,
    get_description_id_by_name,
    get_description_id_by_name_like,
    get_descriptions_missing_alias,
    insert_alias,
    insert_descriptions,
    insert_potential_transactions,
    preserve_potential,
    remove_potential,
    replace_alias,
    search,
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


def _keep_duplicates(db) -> None:
    to_delete_list = []
    for group in get_duplicate_groups(db):
        entry_count = len(group[0])
        db_count = group[1]

        num_to_keep = 0 if db_count > 0 else 1
        if 0 <= num_to_keep <= entry_count:
            num_to_keep = entry_count - num_to_keep
            to_delete_list.extend(group[0][:num_to_keep])

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
@click.option(
    "--skip-duplicates",
    is_flag=True,
    help=(
        "Don't prompt for possible duplicates. Instead ensure there is at least one"
        " in the database."
    ),
)
def insert(source, output, skip_duplicates):
    """Insert entries"""
    input_src = _check_source(source)
    output_src = convert_output(output)
    transaction_data = get_data(input_src)
    with create_sql_connection(output_src) as db:
        insert_descriptions(transaction_data, db)
        insert_potential_transactions(transaction_data, db)
        if skip_duplicates:
            _keep_duplicates(db)
        else:
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


@alias.command(help="Create an alias for a description ")
@click.option(
    "--source",
    prompt="Input data source",
    help="Specify the input data source (database only)",
    type=click.Path(exists=True, file_okay=True),
)
@click.option(
    "--description",
    prompt="Input description to alias (SQLITE LIKE ok)",
    help="Specify the description to create an alias for.",
)
@click.option(
    "--name",
    prompt="Name to use as an alias",
    help="Specify the name to use as an alias",
)
def create(source, description, name):
    with create_sql_connection(source) as db:
        ids = []
        if "%" or "_" in description:
            for result in get_description_id_by_name_like(db, description):
                ids.append(result[0])
        else:
            result = get_description_id_by_name(db, description)
            if result is not None:
                ids.append(result[0])

        if len(ids) > 0:
            insert_alias(db, ids, name)


@alias.command(help="Replace an alias for a description ")
@click.option(
    "--source",
    prompt="Input data source",
    help="Specify the input data source (database only)",
    type=click.Path(exists=True, file_okay=True),
)
@click.option(
    "--description",
    prompt="Input description to alias (SQLITE LIKE ok)",
    help="Specify the description to create an alias for.",
)
@click.option(
    "--name",
    prompt="Name to use as an alias",
    help="Specify the name to use as an alias",
)
def replace(source, description, name):
    with create_sql_connection(source) as db:
        ids = []
        if "%" or "_" in description:
            for result in get_description_id_by_name_like(db, description):
                ids.append(result[0])
        else:
            result = get_description_id_by_name(db, description)
            if result is not None:
                ids.append(result[0])

        if len(ids) > 0:
            replace_alias(db, ids, name)


@click.command(help="Report data out")
@click.option(
    "--source",
    prompt="Input data source",
    help="Specify the input data source (database only)",
    type=click.Path(exists=True, file_okay=True),
)
@click.option(
    "--start",
    # prompt="Input a start date",
    help="Specify the start date, if none is given report from the earliest.",
)
@click.option(
    "--end",
    # prompt="Input an end date",
    help="Specify the start date, if none is given report until the latest.",
)
@click.option(
    "--description",
    # prompt="Input a description",
    help="Specify a description to filter by",
)
@click.option(
    "--format",
    type=click.Choice(["csv"], case_sensitive=False),
    default="csv",
    help="Format of the report (default: csv)",
)
@click.option(
    "--output",
    help="Output destination. Will print to console if nothing given",
)
def report(source, start, end, description, format, output):
    with create_sql_connection(source) as db:
        result = search(db, start, end, description)

        def format(data: tuple) -> str:
            return f"{','.join(data)}\n"

        formatted_iter = map(format, result)

        if output:
            with open(output, "w") as fp:
                fp.writelines(formatted_iter)
        else:
            for line in formatted_iter:
                print(line, end="")


cli.add_command(alias)
cli.add_command(insert)
cli.add_command(report)

if __name__ == "__main__":
    cli()
