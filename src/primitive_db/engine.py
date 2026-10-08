"""Основной цикл взаимодействия с пользователем."""

import prompt

from primitive_db.constants import (
    COMMAND_PROMPT,
    EXIT_COMMAND,
    HELP_COMMAND,
    HELP_MESSAGE,
    UNKNOWN_COMMAND_MESSAGE,
    WELCOME_MESSAGE,
)


def welcome():
    """Показать приветствие и обрабатывать команды пользователя."""
    print(WELCOME_MESSAGE)
    print()
    print("***")
    print(HELP_MESSAGE)

    while True:
        command = prompt.string(COMMAND_PROMPT).strip()

        if command == EXIT_COMMAND:
            return

        if command == HELP_COMMAND:
            print(HELP_MESSAGE)
        else:
            print(UNKNOWN_COMMAND_MESSAGE)