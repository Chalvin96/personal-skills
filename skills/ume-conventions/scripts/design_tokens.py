"""Discover CSS tokens and report literal escapes without executing project code."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from token_source import (
    Declaration,
    collect_css_declarations,
    collect_javascript_strings,
    find_closing,
    mask_css_value,
    mask_functions,
)


K_CUSTOM_PROPERTY = re.compile(r"--[a-zA-Z_][\w-]*")
K_VARIABLE = re.compile(r"var\(\s*(--[\w-]+)\s*\)")
K_LENGTH = re.compile(
    r"(?<![\w.])(-?(?:\d*\.\d+|\d+))(px|rem|em|ch|ex|cm|mm|in|pt|pc|q|(?:[dsl]?v[hwib]|vmin|vmax)|fr|%)(?![\w])",
    re.I,
)
K_COLOR_FUNCTION = re.compile(
    r"\b(?:rgba?|hsla?|hwb|oklch|oklab|lch|lab|color)\(", re.I
)
K_HEX = re.compile(
    r"(?<![\w-])#(?:[0-9a-f]{8}|[0-9a-f]{6}|[0-9a-f]{4}|[0-9a-f]{3})(?![\w-])", re.I
)
K_NAMED_COLORS = set(
    """
    aliceblue antiquewhite aqua aquamarine azure beige bisque black blanchedalmond
    blue blueviolet brown burlywood cadetblue chartreuse chocolate coral cornflowerblue
    cornsilk crimson cyan darkblue darkcyan darkgoldenrod darkgray darkgreen darkgrey
    darkkhaki darkmagenta darkolivegreen darkorange darkorchid darkred darksalmon
    darkseagreen darkslateblue darkslategray darkslategrey darkturquoise darkviolet
    deeppink deepskyblue dimgray dimgrey dodgerblue firebrick floralwhite forestgreen
    fuchsia gainsboro ghostwhite gold goldenrod gray green greenyellow grey honeydew
    hotpink indianred indigo ivory khaki lavender lavenderblush lawngreen lemonchiffon
    lightblue lightcoral lightcyan lightgoldenrodyellow lightgray lightgreen lightgrey
    lightpink lightsalmon lightseagreen lightskyblue lightslategray lightslategrey
    lightsteelblue lightyellow lime limegreen linen magenta maroon mediumaquamarine
    mediumblue mediumorchid mediumpurple mediumseagreen mediumslateblue mediumspringgreen
    mediumturquoise mediumvioletred midnightblue mintcream mistyrose moccasin navajowhite
    navy oldlace olive olivedrab orange orangered orchid palegoldenrod palegreen
    paleturquoise palevioletred papayawhip peachpuff peru pink plum powderblue purple
    rebeccapurple red rosybrown royalblue saddlebrown salmon sandybrown seagreen seashell
    sienna silver skyblue slateblue slategray slategrey snow springgreen steelblue tan
    teal thistle tomato turquoise violet wheat white whitesmoke yellow yellowgreen
""".split()
)
K_COLOR_PROPERTIES = re.compile(
    r"(?:color|background|border|outline|shadow|fill|stroke|decoration|caret|accent|filter)"
)
K_LAYOUT_PROPERTIES = re.compile(
    r"^(?:(?:min-|max-)?(?:width|height|inline-size|block-size)|(?:margin|padding|inset|gap)(?:-\w+)?|top|right|bottom|left|grid-.*|flex-basis|translate|transform|background(?:-size|-position|-image)?|object-position)$"
)
K_LAYOUT_UTILITIES = re.compile(
    r"^(?:(?:min-|max-)?[wh]|size|inset(?:-[xy])?|top|right|bottom|left|translate-[xy]|slide-(?:in-from|out-to)-(?:top|right|bottom|left)|grid-(?:cols|rows)|basis|gap(?:-[xy])?|[pm][xytrblse]?)$"
)
K_COLOR_UTILITIES = {
    "bg",
    "text",
    "border",
    "ring",
    "ring-offset",
    "outline",
    "fill",
    "stroke",
    "decoration",
    "accent",
    "caret",
    "from",
    "via",
    "to",
}
K_SPACING_UTILITIES = {
    "w",
    "h",
    "size",
    "min-w",
    "max-w",
    "min-h",
    "max-h",
    "gap",
    "gap-x",
    "gap-y",
    "inset",
    "inset-x",
    "inset-y",
    "top",
    "right",
    "bottom",
    "left",
    "translate-x",
    "translate-y",
    "space-x",
    "space-y",
    "basis",
    *[
        f"{axis}{side}"
        for axis in "pm"
        for side in ("", "x", "y", "t", "r", "b", "l", "s", "e")
    ],
}
K_TEXT_SCALE = {
    "xs": 12,
    "sm": 14,
    "base": 16,
    "lg": 18,
    "xl": 20,
    "2xl": 24,
    "3xl": 30,
    "4xl": 36,
    "5xl": 48,
    "6xl": 60,
    "7xl": 72,
    "8xl": 96,
    "9xl": 128,
}
K_RADIUS_SCALE = {
    "none": 0,
    "xs": 2,
    "sm": 4,
    "md": 6,
    "lg": 8,
    "xl": 12,
    "2xl": 16,
    "3xl": 24,
    "4xl": 32,
}
K_BORDER_SCALE = (0, 1, 2, 3, 4, 8)
K_PALETTE_FALLBACK = re.compile(
    r"--(?:primary|secondary|accent|warning|destructive|black|white)-\d+$"
)
K_GENERATED = re.compile(
    r"(?im)^\s*(?://|/\*|\*|#).*?(?:@generated\b|(?:this file|code|file was|file is).*?(?:auto[- ]?generated|automatically generated)|code generated .*?do not edit)"
)
K_FIXTURE_PARTS = {
    "test",
    "tests",
    "__tests__",
    "__mocks__",
    "fixtures",
    "__fixtures__",
    "test-fixtures",
    "e2e",
}
K_THEME_SELECTOR = re.compile(
    r":(?:root|host)\b|\[\s*(?:data-)?theme\b|(?:^|[\s,.])\.(?:theme(?:-[\w-]+)?|dark|light)(?=$|[\s,.\[:])"
)


@dataclass(frozen=True)
class Utility:
    name: str
    token: str
    property: str


@dataclass(frozen=True)
class TokenCatalog:
    definitions: dict[str, str]
    utilities: tuple[Utility, ...]
    palette: frozenset[str]
    css: dict[str, tuple[Declaration, ...]]


@dataclass(frozen=True)
class TokenFinding:
    line: int
    rule: str
    message: str
    related_lines: tuple[int, ...] = ()


def is_generated_source(text: str) -> bool:
    return bool(K_GENERATED.search(text[:2048]))


def discover_tokens(files: Iterable[tuple[str, Path]]) -> TokenCatalog:
    definitions: dict[str, str] = {}
    palette: set[str] = set()
    utilities: list[Utility] = []
    css: dict[str, tuple[Declaration, ...]] = {}
    for path, file in sorted(files):
        if file.suffix.lower() != ".css" or _is_fixture_path(path):
            continue
        try:
            text = file.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if is_generated_source(text):
            continue
        declarations = tuple(collect_css_declarations(text))
        css[path] = declarations
        for declaration in declarations:
            name = declaration.property
            if not name.startswith("--"):
                continue
            definitions[name] = declaration.value.strip()
            if _is_palette_file(path):
                palette.add(name)
            if any(context.startswith("@theme") for context in declaration.contexts):
                utilities.extend(_theme_utilities(name, declaration.value))
        utility_groups: dict[str, list[Declaration]] = {}
        for declaration in declarations:
            for context in declaration.contexts:
                match = re.fullmatch(r"@utility\s+([\w-]+)", context)
                if match:
                    utility_groups.setdefault(match[1], []).append(declaration)
        for name, group in utility_groups.items():
            if len(group) == 1 and (
                variable := K_VARIABLE.fullmatch(group[0].value.strip())
            ):
                utilities.append(Utility(name, variable.group(1), group[0].property))
    return TokenCatalog(definitions, tuple(utilities), frozenset(palette), css)


def check_design_tokens(
    path: str, text: str, catalog: TokenCatalog
) -> Iterable[TokenFinding]:
    if _is_fixture_path(path) or is_generated_source(text):
        return
    if Path(path).suffix.lower() == ".css":
        yield from _check_css(path, text, catalog)
        return
    for offset, value in collect_javascript_strings(text):
        yield from _check_class_content(value, offset, text, catalog)


def _is_fixture_path(path: str) -> bool:
    parts = set(Path(path).parts)
    return (
        bool(parts & K_FIXTURE_PARTS)
        or bool(re.search(r"\.(?:test|spec)\.[cm]?[jt]sx?$", path))
        or (Path(path).suffix == ".css" and bool(parts & {"storybook", ".storybook"}))
    )


def _is_palette_file(path: str) -> bool:
    return bool(
        re.fullmatch(
            r"(?:palette|primitives)(?:[.-][\w-]+)?\.css", Path(path).name, re.I
        )
    )


def _is_theme_file(path: str) -> bool:
    return _is_palette_file(path) or bool(
        re.fullmatch(r"theme(?:[.-][\w-]+)?\.css", Path(path).name, re.I)
    )


def _theme_utilities(name: str, value: str) -> Iterable[Utility]:
    variable = K_VARIABLE.fullmatch(value.strip())
    token = variable.group(1) if variable else name
    namespaces = (
        ("--background-color-", ("bg",), "background-color"),
        ("--border-color-", ("border",), "border-color"),
        ("--text-color-", ("text",), "color"),
        ("--color-", tuple(sorted(K_COLOR_UTILITIES)), "color"),
        ("--radius-", ("rounded",), "border-radius"),
        ("--text-", ("text",), "font-size"),
        ("--leading-", ("leading",), "line-height"),
        ("--shadow-", ("shadow",), "box-shadow"),
        ("--container-", ("max-w",), "max-width"),
        ("--spacing-", tuple(sorted(K_SPACING_UTILITIES)), "spacing"),
    )
    for namespace, prefixes, property_name in namespaces:
        if name.startswith(namespace) and "--" not in name[len(namespace) :]:
            suffix = name[len(namespace) :]
            for prefix in prefixes:
                yield Utility(f"{prefix}-{suffix}", token, property_name)
                if token != name:
                    yield Utility(f"{prefix}-{suffix}", name, property_name)
            return


def _line(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def _is_palette(token: str, catalog: TokenCatalog) -> bool:
    return token in catalog.palette or bool(K_PALETTE_FALLBACK.fullmatch(token))


def _check_palette_reads(
    value: str, offset: int, text: str, catalog: TokenCatalog
) -> Iterable[TokenFinding]:
    for match in K_CUSTOM_PROPERTY.finditer(value):
        token = match.group()
        if _is_palette(token, catalog):
            yield TokenFinding(
                _line(text, offset + match.start()),
                "UME-DS008",
                f"palette step `{token}` is read outside the theme layer; read a semantic role",
            )


def _check_class_content(
    value: str,
    offset: int,
    text: str,
    catalog: TokenCatalog,
    *,
    palette_allowed: bool = False,
) -> Iterable[TokenFinding]:
    yield from _check_classes(value, offset, text, catalog)
    if palette_allowed:
        return
    yield from _check_palette_reads(value, offset, text, catalog)
    palette_utilities = {
        utility.name: utility.token
        for utility in catalog.utilities
        if _is_palette(utility.token, catalog)
    }
    for candidate in re.finditer(r"(?<![\w-])[a-z][\w-]*(?![\w-])", value):
        token = palette_utilities.get(candidate.group())
        if token:
            yield TokenFinding(
                _line(text, offset + candidate.start()),
                "UME-DS008",
                f"`{candidate.group()}` reads palette step `{token}`; use a semantic role utility",
            )


def _class_candidates(value: str) -> Iterable[tuple[str, str, int, str]]:
    for match in re.finditer(r"(?<![\w-])([a-z][\w-]*)-\[", value):
        start = match.end() - 1
        end = find_closing(value, start, "[", "]")
        if end == len(value) and not value.endswith("]"):
            continue
        if end < len(value) and value[end] == ":":
            continue
        yield (
            match.group(1),
            value[start + 1 : end - 1],
            match.start(),
            value[match.start() : end],
        )
    properties = {
        "color": "text",
        "background-color": "bg",
        "background": "bg",
        "background-image": "bg",
        "font-size": "text",
        "border-bottom": "border-b",
        "border-radius": "rounded",
        "width": "w",
        "height": "h",
        "padding": "p",
        "margin": "m",
    }
    for match in re.finditer(r"(?<![\w-])\[([a-z][\w-]*|--[\w-]+):", value):
        end = find_closing(value, match.start(), "[", "]")
        if end < len(value) and value[end] == ":":
            continue
        property_name = match.group(1)
        yield (
            properties.get(property_name, property_name),
            value[match.end() : end - 1],
            match.start(),
            value[match.start() : end],
        )


def _check_classes(
    value: str, offset: int, text: str, catalog: TokenCatalog
) -> Iterable[TokenFinding]:
    for prefix, payload, position, candidate in _class_candidates(value):
        decoded = payload.replace("_", " ")
        variable = re.fullmatch(
            r"(?:[\w-]+:)?var\(\s*(--[\w-]+)\s*(?:,\s*([\s\S]+))?\)", decoded
        )
        if variable:
            token = variable.group(1)
            named = _named_utility(prefix, token, catalog)
            if token.startswith(("--radix-", "--tw-")):
                message = None
            elif token not in catalog.definitions:
                message = f"`{candidate}` reads `{token}`, which is not defined in repository CSS"
            elif named:
                message = f"`{candidate}` bypasses the named token utility `{named}`"
                if prefix == "bg" and not named.startswith("bg-"):
                    message += "; choose a background role for this surface"
            else:
                message = None
            if message:
                yield TokenFinding(_line(text, offset + position), "UME-DS006", message)
            if variable.group(2) is None:
                continue
            decoded = variable.group(2)
        raw = mask_functions(mask_css_value(decoded), {"calc"}, with_tokens_only=True)
        colors = list(
            _raw_colors(
                raw, prefix in K_COLOR_UTILITIES or prefix.startswith("border-")
            )
        )
        dimensions = _mask_layout_calculations(raw, catalog)
        dimensions = mask_functions(
            dimensions,
            {
                "var",
                "color-mix",
                "radial-gradient",
                "linear-gradient",
                "conic-gradient",
            },
        )
        lengths = [
            match
            for match in K_LENGTH.finditer(dimensions)
            if float(match.group(1)) != 0
            and not _is_layout_length(prefix, match.group(2), utility=True)
        ]
        number = re.fullmatch(r"-?(?:\d*\.\d+|\d+)", raw.strip())
        if number and float(number.group()) == 0:
            number = None
        if not colors and not lengths and not number:
            continue
        nearest = _nearest_utility(prefix, decoded, catalog)
        message = f"`{candidate}` contains a raw literal; use the design scale or a semantic token"
        if nearest:
            message += f"; nearest utility: `{nearest}`"
        yield TokenFinding(_line(text, offset + position), "UME-DS005", message)


def _named_utility(prefix: str, token: str, catalog: TokenCatalog) -> str | None:
    compatible: list[str] = []
    available: list[str] = []
    for utility in catalog.utilities:
        if utility.token != token:
            continue
        available.append(utility.name)
        if utility.name.startswith(f"{prefix}-"):
            compatible.append(utility.name)
        if _has_utility_property(prefix, utility.property):
            compatible.append(utility.name)
        if prefix.startswith("border-") and utility.name.startswith("border-"):
            compatible.append(prefix + utility.name[len("border") :])
        if prefix.startswith("rounded-") and utility.name.startswith("rounded-"):
            compatible.append(prefix + utility.name[len("rounded") :])
    if compatible:
        return min(compatible, key=lambda name: (len(name), name))
    if prefix == "bg" and available:
        return min(available, key=lambda name: (len(name), name))
    return None


def _has_utility_property(prefix: str, property_name: str) -> bool:
    properties = {
        "max-w": "max-width",
        "min-w": "min-width",
        "w": "width",
        "max-h": "max-height",
        "min-h": "min-height",
        "h": "height",
        "rounded": "border-radius",
        "leading": "line-height",
        "shadow": "box-shadow",
        "bg": "background-color",
    }
    return properties.get(prefix) == property_name


def _mask_layout_calculations(value: str, catalog: TokenCatalog) -> str:
    result = value
    for match in re.finditer(r"\b(?:calc|max|min)\(", value):
        end = find_closing(value, match.end() - 1, "(", ")")
        fragment = value[match.start() : end]
        dimensions = list(K_LENGTH.finditer(fragment))
        if "env(" not in fragment and not any(
            _is_layout_length("width", part.group(2)) for part in dimensions
        ):
            continue
        if all(
            _is_layout_length("width", part.group(2))
            or _is_scale_length("width", part.group(), catalog)
            for part in dimensions
        ):
            result = (
                result[: match.start()] + re.sub(r"[^\n]", " ", fragment) + result[end:]
            )
    return result


def _raw_colors(value: str, named: bool) -> Iterable[tuple[int, str]]:
    yield from ((match.start(), match.group()) for match in K_HEX.finditer(value))
    for match in K_COLOR_FUNCTION.finditer(value):
        end = find_closing(value, match.end() - 1, "(", ")")
        color = value[match.start() : end]
        channels = mask_functions(color, {"var"}).split("/", 1)[0]
        if "var(" not in color or re.search(r"(?<![\w-])(?:\d*\.\d+|\d+)", channels):
            yield match.start(), color
    if named:
        for match in re.finditer(r"(?<![\w-])[a-zA-Z]+(?![\w-])", value):
            if match.group().lower() in K_NAMED_COLORS:
                yield match.start(), match.group()


def _is_layout_length(name: str, unit: str, *, utility: bool = False) -> bool:
    if not (
        K_LAYOUT_UTILITIES.fullmatch(name)
        if utility
        else K_LAYOUT_PROPERTIES.fullmatch(name)
    ):
        return False
    return unit.lower() in {
        "%",
        "fr",
        "vh",
        "vw",
        "vi",
        "vb",
        "vmin",
        "vmax",
        "dvh",
        "dvw",
        "dvi",
        "dvb",
        "svh",
        "svw",
        "svi",
        "svb",
        "lvh",
        "lvw",
        "lvi",
        "lvb",
        "ch",
        "em",
    }


def _pixels(value: str) -> float | None:
    calculation = re.fullmatch(
        r"calc\(\s*([\d.]+(?:px|rem))\s*([+-])\s*([\d.]+(?:px|rem))\s*\)", value.strip()
    )
    if calculation:
        left = _pixels(calculation.group(1))
        right = _pixels(calculation.group(3))
        if left is not None and right is not None:
            return left + right if calculation.group(2) == "+" else left - right
    match = K_LENGTH.fullmatch(value.strip())
    if not match or match.group(2).lower() not in {"px", "rem"}:
        return None
    return float(match.group(1)) * (16 if match.group(2).lower() == "rem" else 1)


def _resolve(
    token: str, catalog: TokenCatalog, visited: frozenset[str] = frozenset()
) -> str:
    if token in visited:
        return ""
    value = catalog.definitions.get(token, "")
    return K_VARIABLE.sub(
        lambda match: _resolve(match.group(1), catalog, visited | {token}), value
    )


def _scale_utilities(prefix: str, catalog: TokenCatalog) -> dict[str, float]:
    values: dict[str, float] = {}
    if prefix == "text":
        values.update(
            {f"text-{name}": float(size) for name, size in K_TEXT_SCALE.items()}
        )
    elif prefix.startswith("rounded"):
        values.update(
            {f"{prefix}-{name}": float(size) for name, size in K_RADIUS_SCALE.items()}
        )
    elif (
        prefix == "border"
        or prefix.startswith("border-")
        or prefix in {"ring", "ring-offset", "outline", "decoration"}
    ):
        values.update({f"{prefix}-{size}": float(size) for size in K_BORDER_SCALE})
    for utility in catalog.utilities:
        if (
            not utility.name.startswith(f"{prefix}-")
            or utility.property == "color"
            or utility.property.endswith("color")
        ):
            continue
        size = _pixels(_resolve(utility.token, catalog))
        if size is not None:
            values[utility.name] = size
        else:
            values.pop(utility.name, None)
    return values


def _normalize_color(value: str) -> str:
    value = re.sub(r"\s+", "", value).lower()
    if re.fullmatch(r"#[0-9a-f]{3,4}", value):
        value = "#" + "".join(char * 2 for char in value[1:])
    return {"white": "#ffffff", "black": "#000000"}.get(value, value)


def _nearest_utility(prefix: str, value: str, catalog: TokenCatalog) -> str | None:
    size = _pixels(value)
    if size is not None:
        scale = _scale_utilities(prefix, catalog)
        if scale:
            mapped = {utility.name for utility in catalog.utilities}
            return min(
                scale,
                key=lambda name: (
                    abs(scale[name] - abs(size)),
                    scale[name],
                    name not in mapped,
                    len(name),
                    name,
                ),
            )
        if prefix in K_SPACING_UTILITIES:
            magnitude = abs(size)
            spacing = _pixels(_resolve("--spacing", catalog)) or 4
            step = int(magnitude / (spacing / 2) + 0.499999) / 2
            label = str(int(step)) if step.is_integer() else str(step)
            sign = "-" if size < 0 else ""
            return f"{sign}{prefix}-{label}" if magnitude != 1 else f"{sign}{prefix}-px"
    if re.fullmatch(r"\d+", value) and prefix in {
        "z",
        "opacity",
        "order",
        "grow",
        "shrink",
        "duration",
        "delay",
    }:
        return f"{prefix}-{value}"
    if re.fullmatch(r"\d*\.\d+", value) and prefix in {"scale", "opacity"}:
        return f"{prefix}-{float(value) * 100:g}"
    if prefix == "leading" and re.fullmatch(r"\d*\.?\d+", value):
        scale = {
            "none": 1,
            "tight": 1.25,
            "snug": 1.375,
            "normal": 1.5,
            "relaxed": 1.625,
            "loose": 2,
        }
        nearest = min(
            scale, key=lambda name: (abs(scale[name] - float(value)), scale[name])
        )
        return f"leading-{nearest}"
    color = _normalize_color(value)
    matches = [
        utility.name
        for utility in catalog.utilities
        if utility.name.startswith(f"{prefix}-")
        and _normalize_color(_resolve(utility.token, catalog)) == color
    ]
    return min(matches, key=lambda name: (len(name), name)) if matches else None


def _is_token_definition(path: str, declaration: Declaration) -> bool:
    if _is_theme_file(path):
        return True
    if any(context.startswith("@theme") for context in declaration.contexts):
        return True
    return declaration.property.startswith("--") and bool(
        K_THEME_SELECTOR.search(" ".join(declaration.contexts))
    )


def _is_scale_length(property_name: str, value: str, catalog: TokenCatalog) -> bool:
    size = _pixels(value)
    if size is None:
        return False
    size = abs(size)
    if size in {0, 1}:
        return True
    if property_name.startswith(("border", "outline")) and (
        property_name.endswith("width")
        or property_name
        in {
            "border",
            "border-top",
            "border-right",
            "border-bottom",
            "border-left",
            "outline",
        }
    ):
        return size in K_BORDER_SCALE
    if property_name in {"text-decoration", "text-decoration-thickness"}:
        return size in K_BORDER_SCALE
    if property_name in {"font-size", "line-height"}:
        scale = set(K_TEXT_SCALE.values())
        for utility in catalog.utilities:
            if utility.property in {"font-size", "line-height"}:
                token_size = _pixels(_resolve(utility.token, catalog))
                if token_size is not None:
                    scale.add(abs(token_size))
        return size in scale
    spacing = _pixels(_resolve("--spacing", catalog)) or 4
    return abs(size / (spacing / 2) - round(size / (spacing / 2))) < 1e-7


def _check_css(path: str, text: str, catalog: TokenCatalog) -> Iterable[TokenFinding]:
    declarations = catalog.css.get(path)
    for declaration in (
        declarations if declarations is not None else collect_css_declarations(text)
    ):
        if declaration.property == "@apply":
            yield from _check_class_content(
                declaration.value,
                declaration.offset,
                text,
                catalog,
                palette_allowed=_is_token_definition(path, declaration),
            )
            continue
        if _is_token_definition(path, declaration):
            continue
        value = mask_css_value(declaration.value)
        yield from _check_palette_reads(value, declaration.offset, text, catalog)
        raw = mask_functions(value, {"calc"}, with_tokens_only=True)
        for position, color in _raw_colors(
            raw,
            bool(K_COLOR_PROPERTIES.search(declaration.property))
            or declaration.property.startswith("--"),
        ):
            line = _line(text, declaration.offset + position)
            related = tuple(
                range(
                    line + 1,
                    _line(text, declaration.offset + position + len(color)) + 1,
                )
            )
            yield TokenFinding(
                line,
                "UME-DS007",
                f"`{declaration.property}` uses raw colour `{color}` outside token definitions; use a semantic colour role",
                related,
            )
        color_masked = mask_functions(
            raw,
            {
                "var",
                "rgb",
                "rgba",
                "hsl",
                "hsla",
                "hwb",
                "oklch",
                "oklab",
                "lch",
                "lab",
                "color",
            },
        )
        for match in K_LENGTH.finditer(color_masked):
            if (
                float(match.group(1)) == 0
                or _is_layout_length(declaration.property, match.group(2))
                or (
                    match.group(2) == "%"
                    and re.search(r"(?:gradient|color-mix)\(", raw)
                )
                or _is_scale_length(declaration.property, match.group(), catalog)
            ):
                continue
            yield TokenFinding(
                _line(text, declaration.offset + match.start()),
                "UME-DS007",
                f"`{declaration.property}` uses non-scale length `{match.group()}` outside token definitions; use the existing scale or a size token",
            )
