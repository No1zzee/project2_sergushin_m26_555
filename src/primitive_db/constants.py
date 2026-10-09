"""Общие настройки базы данных"""

META_FILE = "db_meta.json"
DATA_DIR = "data"
DATA_EXTENSION = ".json"
TEMP_SUFFIX = ".tmp"
SAFE_FILENAME_CHARACTERS = "abcdefghijklmnopqrstuvwxyz0123456789_"
RESERVED_FILENAMES = {"con", "prn", "aux", "nul"} | {
    f"{prefix}{number}" for prefix in ("com", "lpt") for number in range(1, 10)
}
FILE_ENCODING = "utf-8"
JSON_INDENT = 4
ID_COLUMN_NAME = "ID"
ID_COLUMN = "ID:int"
VALID_TYPES = {"int": int, "str": str, "bool": bool}
BOOL_VALUES = {"true": True, "false": False}
QUOTES = "\"'"
PUNCTUATION = "(),=:"
COMMAND_PROMPT = "Введите команду: "
CONFIRM_PROMPT = 'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: '
CONFIRM_ANSWER = "y"
CANCELLED_MESSAGE = "Операция отменена."
DROP_ACTION = "удаление таблицы"
DELETE_ACTION = "удаление записи"
TIME_MESSAGE = "Функция {function_name} выполнилась за {elapsed:.3f} секунд"
FILE_NOT_FOUND_MESSAGE = (
    "Ошибка: Файл данных не найден. Возможно, база данных не инициализирована."
)
KEY_ERROR_MESSAGE = "Ошибка: Таблица или столбец {error} не найден."
VALIDATION_ERROR_MESSAGE = "Ошибка валидации: {error}"
FILE_ERROR_MESSAGE = "Ошибка работы с файлами: {error}"
UNEXPECTED_ERROR_MESSAGE = "Произошла непредвиденная ошибка: {error}"
KNOWN_ERROR_PREFIXES = ("Ошибка", "Некорректное значение:", "Функции ")
INVALID_VALUE_MESSAGE = "Некорректное значение: {value}. Попробуйте снова."
UNKNOWN_COMMAND_MESSAGE = "Функции {command} нет. Попробуйте снова."
TABLE_EXISTS_MESSAGE = 'Ошибка: Таблица "{table_name}" уже существует.'
TABLE_MISSING_MESSAGE = 'Ошибка: Таблица "{table_name}" не существует.'
TABLE_CREATED_MESSAGE = (
    'Таблица "{table_name}" успешно создана со столбцами: {columns}'
)
TABLE_DROPPED_MESSAGE = 'Таблица "{table_name}" успешно удалена.'
INSERTED_MESSAGE = 'Запись с ID={row_id} успешно добавлена в таблицу "{table_name}".'
UPDATED_MESSAGE = 'Запись с ID={row_id} в таблице "{table_name}" успешно обновлена.'
DELETED_MESSAGE = 'Запись с ID={row_id} успешно удалена из таблицы "{table_name}".'
NO_MATCH_MESSAGE = "Подходящих записей не найдено."
EMPTY_TABLES_MESSAGE = "Таблиц пока нет."
HELP_MESSAGE = (
    "\n***Операции с данными***\nФункции:\n"
    "create_table <таблица> <столбец:тип> ... - создать таблицу\n"
    "list_tables - показать список таблиц\n"
    "drop_table <таблица> - удалить таблицу и её данные\n"
    "insert into <таблица> values (<значение>, ...) - добавить запись\n"
    "select from <таблица> [where <столбец> = <значение>] - прочитать записи\n"
    "update <таблица> set <столбец> = <значение> "
    "where <столбец> = <значение> - обновить записи\n"
    "delete from <таблица> where <столбец> = <значение> - удалить записи\n"
    "info <таблица> - информация о таблице\n"
    "help - справка\nexit - выход"
)
