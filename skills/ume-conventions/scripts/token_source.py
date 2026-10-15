"""Offset-preserving CSS declarations and JavaScript string literals."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable


K_CSS_STRINGS_AND_COMMENTS = re.compile(
    r""""(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|/\*[\s\S]*?\*/"""
)


@dataclass(frozen=True)
class Declaration:
    property: str
    value: str
    offset: int
    contexts: tuple[str, ...]


def collect_javascript_strings(text: str) -> Iterable[tuple[int, str]]:
    index = 0
    while index < len(text):
        next_index = _skip_javascript_comment(text, index)
        if next_index != index:
            index = next_index
        elif text[index] in "\"'`":
            strings, index = _read_javascript_string(text, index)
            yield from strings
        else:
            index += 1


def mask_css_comments(text: str) -> str:
    return K_CSS_STRINGS_AND_COMMENTS.sub(
        lambda match: (
            _mask(match.group()) if match.group().startswith("/*") else match.group()
        ),
        text,
    )


def mask_css_value(text: str) -> str:
    result = K_CSS_STRINGS_AND_COMMENTS.sub(lambda match: _mask(match.group()), text)
    return mask_functions(result, {"url"})


def mask_functions(
    text: str, names: set[str], *, with_tokens_only: bool = False
) -> str:
    result = text
    for match in re.finditer(r"\b([a-zA-Z-]+)\(", text):
        if match.group(1).lower() not in names:
            continue
        end = find_closing(text, match.end() - 1, "(", ")")
        fragment = text[match.start() : end]
        if not with_tokens_only or "var(" in fragment:
            result = result[: match.start()] + _mask(fragment) + result[end:]
    return result


def find_closing(text: str, start: int, opening: str, closing: str) -> int:
    depth = 0
    quote: str | None = None
    escaped = False
    for index in range(start, len(text)):
        char = text[index]
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
        elif char in "\"'":
            quote = char
        elif char == opening:
            depth += 1
        elif char == closing:
            depth -= 1
            if depth == 0:
                return index + 1
    return len(text)


def collect_css_declarations(text: str) -> Iterable[Declaration]:
    clean = mask_css_comments(text)
    contexts: list[str] = []
    start = 0
    index = 0
    while index < len(clean):
        char = clean[index]
        if char in "\"'":
            quote = K_CSS_STRINGS_AND_COMMENTS.match(clean, index)
            if quote:
                index = quote.end()
                continue
        if char in "([":
            index = find_closing(clean, index, char, ")" if char == "(" else "]")
            continue
        if char == "{":
            contexts.append(clean[start:index].strip())
            start = index + 1
        elif char in ";}":
            declaration = re.match(
                r"\s*(--[\w-]+|[a-zA-Z][\w-]*)\s*:\s*([\s\S]*?)\s*$", clean[start:index]
            )
            apply = re.match(r"\s*(@apply)\s+([\s\S]*?)\s*$", clean[start:index])
            declaration = declaration or apply
            if declaration and contexts:
                yield Declaration(
                    declaration.group(1),
                    declaration.group(2),
                    start + declaration.start(2),
                    tuple(contexts),
                )
            if char == "}" and contexts:
                contexts.pop()
            start = index + 1
        index += 1


def _mask(text: str) -> str:
    return re.sub(r"[^\n]", " ", text)


def _skip_javascript_comment(text: str, index: int) -> int:
    if text.startswith("//", index):
        end = text.find("\n", index + 2)
        return len(text) if end < 0 else end + 1
    if text.startswith("/*", index):
        end = text.find("*/", index + 2)
        return len(text) if end < 0 else end + 2
    return index


def _read_javascript_string(text: str, start: int) -> tuple[list[tuple[int, str]], int]:
    quote = text[start]
    strings: list[tuple[int, str]] = []
    segment = index = start + 1
    while index < len(text):
        if text[index] == "\\":
            index += 2
        elif text[index] == quote:
            strings.append((segment, text[segment:index]))
            return strings, index + 1
        elif quote == "`" and text.startswith("${", index):
            strings.append((segment, text[segment:index]))
            nested, index = _read_javascript_expression(text, index + 2)
            strings.extend(nested)
            segment = index
        else:
            index += 1
    strings.append((segment, text[segment:index]))
    return strings, index


def _read_javascript_expression(
    text: str, start: int
) -> tuple[list[tuple[int, str]], int]:
    strings: list[tuple[int, str]] = []
    index = start
    depth = 1
    while index < len(text):
        next_index = _skip_javascript_comment(text, index)
        if next_index != index:
            index = next_index
            continue
        char = text[index]
        if char in "\"'`":
            nested, index = _read_javascript_string(text, index)
            strings.extend(nested)
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return strings, index + 1
        index += 1
    return strings, index
