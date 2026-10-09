"""Взаимодействие с пользователем и сохранение результатов операций"""

import prompt
from prettytable import PrettyTable

from primitive_db.constants import (
    COMMAND_PROMPT,
    DELETED_MESSAGE,
    EMPTY_TABLES_MESSAGE,
    HELP_MESSAGE,
    ID_COLUMN_NAME,
    INSERTED_MESSAGE,
    META_FILE,
    NO_MATCH_MESSAGE,
    TABLE_CREATED_MESSAGE,
    TABLE_DROPPED_MESSAGE,
    UPDATED_MESSAGE,
)
from primitive_db.core import (
    create_table,
    delete,
    drop_table,
    get_schema,
    insert,
    select,
    select_rows,
    update,
    validate_fields,
    validate_table_data,
)
from primitive_db.decorators import handle_db_errors
from primitive_db.parser import parse_command
from primitive_db.utils import (
    load_metadata,
    load_table_data,
    remove_table_data,
    save_metadata,
    save_table_data,
)


def print_help():
    """Показать команды приложения"""
    print(HELP_MESSAGE)


def print_rows(schema, rows):
    """Вывести записи в порядке столбцов схемы через PrettyTable"""
    table = PrettyTable()
    table.field_names = list(schema)
    for row in rows:
        table.add_row([row[name] for name in schema])
    print(table)


def execute_crud(metadata, operation):
    """Проверить схему, выполнить CRUD-команду и сохранить изменения"""
    command = operation["command"]
    table_name = operation["table"]
    schema = get_schema(metadata, table_name)
    if command == "insert":
        data = insert(metadata, table_name, operation["values"])
        if data is None:
            return
        save_table_data(table_name, data)
        print(INSERTED_MESSAGE.format(
            row_id=data[-1][ID_COLUMN_NAME], table_name=table_name
        ))
        return

    data = load_table_data(table_name)
    validate_table_data(schema, data)
    where = operation.get("where")
    if where is not None:
        validate_fields(schema, where)
    if command == "info":
        print(f"Таблица: {table_name}")
        print(f"Столбцы: {', '.join(metadata[table_name])}")
        print(f"Количество записей: {len(data)}")
    elif command == "select":
        rows = select(data, where)
        if rows is not None:
            print_rows(schema, rows)
    else:
        if command == "update":
            validate_fields(schema, operation["set"], allow_id=False)
        matched = select_rows(data, where)
        if not matched:
            print(NO_MATCH_MESSAGE)
            return
        if command == "update":
            changed = update(data, operation["set"], where)
            message = UPDATED_MESSAGE
        else:
            changed = delete(data, where)
            message = DELETED_MESSAGE
        if changed is None:
            return
        save_table_data(table_name, changed)
        for row in matched:
            print(message.format(row_id=row[ID_COLUMN_NAME], table_name=table_name))


@handle_db_errors
def execute_command(metadata, operation):
    """Выполнить разобранную команду; вернуть True для выхода"""
    command = operation["command"]
    if command == "exit":
        return True
    if command == "help":
        print_help()
    elif command == "list_tables":
        if not metadata:
            print(EMPTY_TABLES_MESSAGE)
        for name in metadata:
            print(f"- {name}")
    elif command == "create_table":
        name = operation["table"]
        updated_metadata = create_table(metadata, name, operation["columns"])
        if updated_metadata is None:
            return False
        save_table_data(name, [])
        save_metadata(META_FILE, metadata)
        print(TABLE_CREATED_MESSAGE.format(
            table_name=name, columns=", ".join(metadata[name])
        ))
    elif command == "drop_table":
        name = operation["table"]
        get_schema(metadata, name)
        updated_metadata = drop_table(metadata, name)
        if updated_metadata is None:
            return False
        save_metadata(META_FILE, metadata)
        remove_table_data(name)
        print(TABLE_DROPPED_MESSAGE.format(table_name=name))
    else:
        execute_crud(metadata, operation)
    return False


@handle_db_errors
def process_input(user_input):
    """Разобрать ввод и выполнить команду с централизованной обработкой ошибок."""
    operation = parse_command(user_input)
    if operation is None:
        return False
    if operation["command"] == "exit":
        return True
    metadata = load_metadata(META_FILE)
    return execute_command(metadata, operation)


def run():
    """Читать команды до exit; ошибки ввода не завершают приложение"""
    print_help()
    while True:
        try:
            user_input = prompt.string(COMMAND_PROMPT)
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if process_input(user_input) is True:
            return
