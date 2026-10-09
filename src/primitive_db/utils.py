"""Чтение и запись JSON-файлов базы данных"""

import json
import os

from primitive_db.constants import (
    DATA_DIR,
    DATA_EXTENSION,
    FILE_ENCODING,
    JSON_INDENT,
    RESERVED_FILENAMES,
    SAFE_FILENAME_CHARACTERS,
    TEMP_SUFFIX,
)


def load_json(filepath, default):
    """Прочитать JSON; отсутствие файла не считать повреждением данных"""
    try:
        with open(filepath, encoding=FILE_ENCODING) as source:
            return json.load(source)
    except FileNotFoundError:
        return default


def save_json(filepath, data):
    """Записать JSON через временный файл, сохраняя старый при сбое записи"""
    temporary = filepath + TEMP_SUFFIX
    try:
        with open(temporary, "w", encoding=FILE_ENCODING) as target:
            json.dump(data, target, ensure_ascii=False, indent=JSON_INDENT)
        os.replace(temporary, filepath)
    finally:
        if os.path.exists(temporary):
            os.remove(temporary)


def load_metadata(filepath):
    """Загрузить описание таблиц или пустой словарь"""
    metadata = load_json(filepath, {})
    if not isinstance(metadata, dict) or any(
        not isinstance(columns, list)
        or not all(isinstance(column, str) for column in columns)
        for columns in metadata.values()
    ):
        raise ValueError("Ошибка: некорректная структура метаданных.")
    return metadata


def save_metadata(filepath, data):
    """Сохранить описание таблиц"""
    save_json(filepath, data)


def table_path(table_name):
    """Получить путь к данным таблицы, исключая переходы между папками"""
    if not table_name.isidentifier():
        raise ValueError("Ошибка: некорректное имя таблицы.")
    filename = "".join(
        char if char in SAFE_FILENAME_CHARACTERS else f"~{ord(char):x}~"
        for char in table_name
    )
    if filename in RESERVED_FILENAMES:
        filename = "~reserved~" + filename
    return os.path.join(DATA_DIR, filename + DATA_EXTENSION)


def load_table_data(table_name):
    """Загрузить список записей или вернуть пустой список"""
    data = load_json(table_path(table_name), [])
    if not isinstance(data, list) or not all(isinstance(row, dict) for row in data):
        raise ValueError("Ошибка: данные таблицы должны быть списком записей.")
    return data


def save_table_data(table_name, data):
    """Создать папку данных при необходимости и сохранить записи"""
    filepath = table_path(table_name)
    os.makedirs(DATA_DIR, exist_ok=True)
    save_json(filepath, data)


def remove_table_data(table_name):
    """Удалить данные таблицы, если файл существует"""
    try:
        os.remove(table_path(table_name))
    except FileNotFoundError:
        pass
