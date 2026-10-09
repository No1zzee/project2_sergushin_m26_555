"""Ввод команд и управление работой приложения."""

import shlex

import prompt

from primitive_db.constants import (
    COMMAND_PROMPT,
    CREATE_COMMAND,
    DROP_COMMAND,
    EMPTY_TABLES_MESSAGE,
    EXIT_COMMAND,
    HELP_COMMAND,
    HELP_MESSAGE,
    INVALID_ARGUMENTS_MESSAGE,
    INVALID_VALUE_MESSAGE,
    LIST_COMMAND,
    META_FILE,
    METADATA_ERROR_MESSAGE,
    SAVE_ERROR_MESSAGE,
    TABLE_CREATED_MESSAGE,
    TABLE_DROPPED_MESSAGE,
    UNKNOWN_COMMAND_MESSAGE,
)
from primitive_db.core import create_table, drop_table
from primitive_db.utils import load_metadata, save_metadata


def print_help():
    """Показать доступные команды."""
    print(HELP_MESSAGE)


def print_tables(metadata):
    """Вывести имена существующих таблиц."""
    if not metadata:
        print(EMPTY_TABLES_MESSAGE)
        return

    for table_name in metadata:
        print(f"- {table_name}")


def execute_command(metadata, command, arguments):
    """Выполнить команду и вернуть признак завершения приложения."""
    if command == EXIT_COMMAND:
        if arguments:
            raise ValueError(INVALID_ARGUMENTS_MESSAGE)
        return True

    if command == HELP_COMMAND:
        if arguments:
            raise ValueError(INVALID_ARGUMENTS_MESSAGE)
        print_help()

    elif command == LIST_COMMAND:
        if arguments:
            raise ValueError(INVALID_ARGUMENTS_MESSAGE)
        print_tables(metadata)

    elif command == CREATE_COMMAND:
        if not arguments:
            raise ValueError(INVALID_ARGUMENTS_MESSAGE)

        table_name, *columns = arguments
        updated_metadata = create_table(metadata, table_name, columns)
        save_metadata(META_FILE, updated_metadata)
        print(
            TABLE_CREATED_MESSAGE.format(
                table_name=table_name,
                columns=", ".join(updated_metadata[table_name]),
            )
        )

    elif command == DROP_COMMAND:
        if not arguments:
            raise ValueError(INVALID_ARGUMENTS_MESSAGE)

        table_name, *extra_arguments = arguments
        if extra_arguments:
            raise ValueError(INVALID_ARGUMENTS_MESSAGE)

        updated_metadata = drop_table(metadata, table_name)
        save_metadata(META_FILE, updated_metadata)
        print(TABLE_DROPPED_MESSAGE.format(table_name=table_name))

    else:
        print(UNKNOWN_COMMAND_MESSAGE.format(command=command))

    return False


def run():
    """Запустить цикл загрузки метаданных и обработки команд."""
    print_help()

    while True:
        try:
            metadata = load_metadata(META_FILE)
        except (OSError, ValueError) as error:
            print(METADATA_ERROR_MESSAGE.format(error=error))
            return

        try:
            user_input = prompt.string(COMMAND_PROMPT)
        except (EOFError, KeyboardInterrupt):
            print()
            return

        try:
            parts = shlex.split(user_input)
        except ValueError:
            print(INVALID_VALUE_MESSAGE.format(value=user_input))
            continue

        if not parts:
            continue

        command, *arguments = parts

        try:
            should_exit = execute_command(metadata, command, arguments)
        except ValueError as error:
            print(error)
        except OSError as error:
            print(SAVE_ERROR_MESSAGE.format(error=error))
        else:
            if should_exit:
                return