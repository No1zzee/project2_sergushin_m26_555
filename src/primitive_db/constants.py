"""Общие настройки и сообщения приложения."""

META_FILE = "db_meta.json"
FILE_ENCODING = "utf-8"
JSON_INDENT = 4

VALID_TYPES = ("int", "str", "bool")
ID_COLUMN_NAME = "ID"
ID_COLUMN = "ID:int"
COLUMN_SEPARATOR = ":"

CREATE_COMMAND = "create_table"
DROP_COMMAND = "drop_table"
LIST_COMMAND = "list_tables"
HELP_COMMAND = "help"
EXIT_COMMAND = "exit"

COMMAND_PROMPT = "Введите команду: "

HELP_MESSAGE = (
    "\n***Процесс работы с таблицей***\n"
    "Функции:\n"
    "<command> create_table <имя_таблицы> <столбец1:тип> "
    "<столбец2:тип> ... - создать таблицу\n"
    "<command> list_tables - показать список всех таблиц\n"
    "<command> drop_table <имя_таблицы> - удалить таблицу\n"
    "<command> exit - выход из программы\n"
    "<command> help - справочная информация"
)

TABLE_EXISTS_MESSAGE = 'Ошибка: Таблица "{table_name}" уже существует.'
TABLE_MISSING_MESSAGE = 'Ошибка: Таблица "{table_name}" не существует.'
TABLE_CREATED_MESSAGE = (
    'Таблица "{table_name}" успешно создана со столбцами: {columns}'
)
TABLE_DROPPED_MESSAGE = 'Таблица "{table_name}" успешно удалена.'
EMPTY_TABLES_MESSAGE = "Таблиц пока нет."

INVALID_VALUE_MESSAGE = "Некорректное значение: {value}. Попробуйте снова."
UNKNOWN_COMMAND_MESSAGE = "Функции {command} нет. Попробуйте снова."
INVALID_ARGUMENTS_MESSAGE = (
    "Некорректное значение: аргументы команды. "
    "Попробуйте снова. Введите help для справки."
)
METADATA_ERROR_MESSAGE = "Ошибка чтения метаданных: {error}"
SAVE_ERROR_MESSAGE = "Ошибка сохранения метаданных: {error}"