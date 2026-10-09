from primitive_db.constants import (
    BOOL_VALUES,
    INVALID_VALUE_MESSAGE,
    PUNCTUATION,
    QUOTES,
    UNKNOWN_COMMAND_MESSAGE,
)


def invalid(value):
    """Сообщить о неправильном значении или структуре команды"""
    raise ValueError(INVALID_VALUE_MESSAGE.format(value=value))


def tokenize(text):
    """Разделить ввод на слова"""
    tokens = []
    position = 0
    while position < len(text):
        char = text[position]
        if char.isspace():
            position += 1
        elif char in PUNCTUATION:
            tokens.append(("symbol", char))
            position += 1
        elif char in QUOTES:
            quote = char
            position += 1
            value = []
            while position < len(text) and text[position] != quote:
                char = text[position]
                if (
                    char == "\\"
                    and position + 1 < len(text)
                    and text[position + 1] in (quote, "\\")
                ):
                    position += 1
                    char = text[position]
                value.append(char)
                position += 1
            if position == len(text):
                invalid("незакрытые кавычки")
            tokens.append(("string", "".join(value)))
            position += 1
        else:
            start = position
            while (
                position < len(text)
                and not text[position].isspace()
                and text[position] not in PUNCTUATION + QUOTES
            ):
                position += 1
            tokens.append(("word", text[start:position]))
    return tokens


def expect(tokens, position, kind, value=None):
    """Проверить наличие ожидаемого элемента и вернуть его текст"""
    if position >= len(tokens):
        invalid("команда не завершена")
    actual_kind, actual_value = tokens[position]
    if actual_kind != kind or (value is not None and actual_value != value):
        invalid(actual_value)
    return actual_value


def identifier(tokens, position):
    """Прочитать регистрозависимое имя без кавычек"""
    name = expect(tokens, position, "word")
    if not name.isidentifier():
        invalid(name)
    return name


def parse_literal(token):
    """Распознать строку в кавычках, целое число или булево значение"""
    kind, value = token
    if kind == "string":
        return value
    if kind != "word":
        invalid(value)
    if value.lower() in BOOL_VALUES:
        return BOOL_VALUES[value.lower()]
    digits = value[1:] if value.startswith(("+", "-")) else value
    if digits and all(char in "0123456789" for char in digits):
        return int(value)
    invalid(value)


def assignment(tokens, position):
    """Прочитать одно выражение столбец = значение"""
    name = identifier(tokens, position)
    expect(tokens, position + 1, "symbol", "=")
    if position + 2 >= len(tokens):
        invalid("не указано значение")
    return {name: parse_literal(tokens[position + 2])}, position + 3


def ensure_end(tokens, position):
    """Отклонить оставшиеся после команды элементы"""
    if position != len(tokens):
        invalid(tokens[position][1])


def parse_where(text):
    """Преобразовать одно условие вида age = 28 в словарь"""
    tokens = tokenize(text)
    result, position = assignment(tokens, 0)
    ensure_end(tokens, position)
    return result


def parse_set(text):
    """Разобрать одно присваивание"""
    return parse_where(text)


def values_from_tokens(tokens, position):
    """Разобрать ровно одну группу значений в круглых скобках"""
    expect(tokens, position, "symbol", "(")
    position += 1
    values = []
    if position < len(tokens) and tokens[position] == ("symbol", ")"):
        return values, position + 1
    while True:
        if position >= len(tokens):
            invalid("не завершён список значений")
        values.append(parse_literal(tokens[position]))
        position += 1
        if position < len(tokens) and tokens[position] == ("symbol", ")"):
            return values, position + 1
        expect(tokens, position, "symbol", ",")
        position += 1


def parse_values(text):
    """Разобрать значения со скобками и без лишних элементов после них"""
    tokens = tokenize(text)
    values, position = values_from_tokens(tokens, 0)
    ensure_end(tokens, position)
    return values


def parse_command(text):
    """Преобразовать исходную команду в описание операции"""
    tokens = tokenize(text)
    if not tokens:
        return None
    command = expect(tokens, 0, "word")
    result = {"command": command}
    if command in ("help", "exit", "list_tables"):
        ensure_end(tokens, 1)
        return result
    if command in ("create_table", "drop_table", "info", "update"):
        result["table"] = identifier(tokens, 1)
        position = 2
    elif command in ("insert", "select", "delete"):
        keyword = "into" if command == "insert" else "from"
        expect(tokens, 1, "word", keyword)
        result["table"] = identifier(tokens, 2)
        position = 3
    else:
        raise ValueError(UNKNOWN_COMMAND_MESSAGE.format(command=command))

    if command == "create_table":
        columns = []
        while position < len(tokens):
            name = identifier(tokens, position)
            expect(tokens, position + 1, "symbol", ":")
            column_type = expect(tokens, position + 2, "word")
            columns.append(f"{name}:{column_type}")
            position += 3
        result["columns"] = columns
    elif command == "insert":
        expect(tokens, position, "word", "values")
        result["values"], position = values_from_tokens(tokens, position + 1)
    elif command in ("select", "update", "delete"):
        if command == "update":
            expect(tokens, position, "word", "set")
            result["set"], position = assignment(tokens, position + 1)
        if command != "select" or position < len(tokens):
            expect(tokens, position, "word", "where")
            result["where"], position = assignment(tokens, position + 1)
    ensure_end(tokens, position)
    return result
