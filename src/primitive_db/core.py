"""Основная логика управления таблицами."""

from primitive_db.constants import (
    COLUMN_SEPARATOR,
    ID_COLUMN,
    ID_COLUMN_NAME,
    INVALID_VALUE_MESSAGE,
    TABLE_EXISTS_MESSAGE,
    TABLE_MISSING_MESSAGE,
    VALID_TYPES,
)


def validate_columns(columns):
    """Проверить столбцы и вернуть структуру с единственным ID:int."""
    if not columns:
        raise ValueError(
            INVALID_VALUE_MESSAGE.format(value="не указаны столбцы")
        )

    result = [ID_COLUMN]
    seen_names = set()

    for column in columns:
        name, separator, column_type = column.partition(COLUMN_SEPARATOR)

        if (
            not separator
            or not name.isidentifier()
            or column_type not in VALID_TYPES
            or name in seen_names
        ):
            raise ValueError(INVALID_VALUE_MESSAGE.format(value=column))

        seen_names.add(name)

        if name == ID_COLUMN_NAME:
            if column != ID_COLUMN:
                raise ValueError(INVALID_VALUE_MESSAGE.format(value=column))
            continue

        result.append(column)

    return result


def create_table(metadata, table_name, columns):
    """Добавить таблицу с проверенной структурой в метаданные."""
    if table_name in metadata:
        raise ValueError(TABLE_EXISTS_MESSAGE.format(table_name=table_name))

    if not table_name.isidentifier():
        raise ValueError(INVALID_VALUE_MESSAGE.format(value=table_name))

    validated_columns = validate_columns(columns)
    metadata[table_name] = validated_columns
    return metadata


def drop_table(metadata, table_name):
    """Удалить существующую таблицу из метаданных."""
    if table_name not in metadata:
        raise ValueError(TABLE_MISSING_MESSAGE.format(table_name=table_name))

    del metadata[table_name]
    return metadata