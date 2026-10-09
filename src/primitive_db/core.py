"""Проверка схемы и операции с таблицами и записями"""

from primitive_db.constants import (
    DELETE_ACTION,
    DROP_ACTION,
    ID_COLUMN,
    ID_COLUMN_NAME,
    INVALID_VALUE_MESSAGE,
    TABLE_EXISTS_MESSAGE,
    TABLE_MISSING_MESSAGE,
    VALID_TYPES,
)
from primitive_db.decorators import (
    confirm_action,
    create_cacher,
    handle_db_errors,
    log_time,
)
from primitive_db.utils import load_table_data

SELECT_CACHE = create_cacher()


def invalid(value):
    """Сообщить о значении, не соответствующем схеме"""
    raise ValueError(INVALID_VALUE_MESSAGE.format(value=value))


def validate_columns(columns):
    """Проверить определения столбцов и поставить единственный ID первым"""
    if not columns:
        invalid("не указаны столбцы")
    result = [ID_COLUMN]
    seen = set()
    for column in columns:
        name, separator, column_type = column.partition(":")
        if (
            not separator
            or not name.isidentifier()
            or column_type not in VALID_TYPES
            or name in seen
        ):
            invalid(column)
        seen.add(name)
        if name == ID_COLUMN_NAME:
            if column != ID_COLUMN:
                invalid(column)
        else:
            result.append(column)
    return result


def get_schema(metadata, table_name):
    """Проверить существование таблицы и вернуть соответствие имён типам"""
    if table_name not in metadata:
        raise ValueError(TABLE_MISSING_MESSAGE.format(table_name=table_name))
    columns = metadata[table_name]
    if validate_columns(columns) != columns:
        invalid("повреждённая схема таблицы")
    return dict(column.split(":") for column in columns)


@handle_db_errors
def create_table(metadata, table_name, columns):
    """Добавить в метаданные таблицу с проверенной схемой"""
    if table_name in metadata:
        raise ValueError(TABLE_EXISTS_MESSAGE.format(table_name=table_name))
    if not table_name.isidentifier():
        invalid(table_name)
    metadata[table_name] = validate_columns(columns)
    SELECT_CACHE.clear()
    return metadata


@handle_db_errors
@confirm_action(DROP_ACTION)
def drop_table(metadata, table_name):
    """Удалить таблицу из метаданных"""
    get_schema(metadata, table_name)
    del metadata[table_name]
    SELECT_CACHE.clear()
    return metadata


def validate_fields(schema, fields, allow_id=True):
    """Проверить существование столбцов и точное совпадение типов значений"""
    for name, value in fields.items():
        if name not in schema:
            invalid(name)
        if not allow_id and name == ID_COLUMN_NAME:
            invalid("ID нельзя изменять вручную")
        if type(value) is not VALID_TYPES[schema[name]]:
            invalid(f"{name} = {value!r}")


def validate_table_data(schema, data):
    """Проверить обязательные поля, типы и уникальность ID загруженных записей"""
    seen_ids = set()
    for row in data:
        if set(row) != set(schema):
            invalid("набор полей сохранённой записи")
        validate_fields(schema, row)
        row_id = row[ID_COLUMN_NAME]
        if row_id <= 0 or row_id in seen_ids:
            invalid("ID сохранённой записи")
        seen_ids.add(row_id)


@handle_db_errors
@log_time
def insert(metadata, table_name, values):
    """Проверить значения, назначить ID и вернуть данные с новой записью"""
    schema = get_schema(metadata, table_name)
    columns = [name for name in schema if name != ID_COLUMN_NAME]
    if len(values) != len(columns):
        invalid(f"ожидалось значений: {len(columns)}, получено: {len(values)}")
    fields = dict(zip(columns, values, strict=True))
    validate_fields(schema, fields)
    data = load_table_data(table_name)
    validate_table_data(schema, data)
    new_id = max((row[ID_COLUMN_NAME] for row in data), default=0) + 1
    SELECT_CACHE.clear()
    return data + [{ID_COLUMN_NAME: new_id, **fields}]


def matches(row, where_clause):
    """Сопоставить запись"""
    return all(
        name in row and type(row[name]) is type(value) and row[name] == value
        for name, value in where_clause.items()
    )


def snapshot_fields(fields):
    """Получить неизменяемое представление полей с различением bool и int."""
    return tuple((name, type(value).__name__, value) for name, value in fields.items())


def select_rows(table_data, where_clause=None):
    """Отфильтровать записи без кэша и служебного вывода для внутренних вызовов"""
    return [
        dict(row) for row in table_data
        if where_clause is None or matches(row, where_clause)
    ]


@handle_db_errors
@log_time
def select(table_data, where_clause=None):
    """Вернуть копии результатов запроса, используя кэш в замыкании"""
    snapshot = tuple(snapshot_fields(row) for row in table_data)
    condition = None if where_clause is None else snapshot_fields(where_clause)
    key = (snapshot, condition)
    rows = SELECT_CACHE(key, lambda: select_rows(table_data, where_clause))
    return [dict(row) for row in rows]


@handle_db_errors
def update(table_data, set_clause, where_clause):
    """Вернуть записи с изменёнными полями для совпавших строк"""
    if ID_COLUMN_NAME in set_clause:
        invalid("ID нельзя изменять вручную")
    updated = [
        {**row, **set_clause} if matches(row, where_clause) else dict(row)
        for row in table_data
    ]
    SELECT_CACHE.clear()
    return updated


@handle_db_errors
@confirm_action(DELETE_ACTION)
def delete(table_data, where_clause):
    """Вернуть записи, не соответствующие условию удаления"""
    remaining = [row for row in table_data if not matches(row, where_clause)]
    SELECT_CACHE.clear()
    return remaining
