"""Загрузка и сохранение метаданных базы данных."""

import json

from primitive_db.constants import FILE_ENCODING, JSON_INDENT


def load_metadata(filepath):
    """Загрузить метаданные или вернуть пустой словарь при отсутствии файла."""
    try:
        with open(filepath, encoding=FILE_ENCODING) as metadata_file:
            metadata = json.load(metadata_file)
    except FileNotFoundError:
        return {}

    if not isinstance(metadata, dict):
        raise ValueError("метаданные должны быть JSON-объектом")

    if any(
        not isinstance(columns, list)
        or not all(isinstance(column, str) for column in columns)
        for columns in metadata.values()
    ):
        raise ValueError("структура таблицы должна быть списком строк")

    return metadata


def save_metadata(filepath, data):
    """Сохранить метаданные в JSON-файл."""
    with open(filepath, "w", encoding=FILE_ENCODING) as metadata_file:
        json.dump(
            data,
            metadata_file,
            ensure_ascii=False,
            indent=JSON_INDENT,
        )