import json
import subprocess
import sys
from pathlib import Path

import pytest


K_CHECKER = Path(__file__).resolve().parents[1] / "scripts" / "mechanical_check.py"
K_TOKENS = """
:root {
  --border-strong: var(--brand-40);
  --surface: #fff;
  --private-size: 1.25rem;
}
@theme inline {
  --border-color-strong: var(--border-strong);
  --background-color-surface: var(--surface);
  --radius-sm: 0.25rem;
  --text-caption: 0.8125rem;
}
@utility container-max {
  max-width: var(--private-size);
}
"""


def run_checker(tmp_path, source, filename="Component.tsx", diff=None, extras=None):
    files = {
        "styles/tokens.css": K_TOKENS,
        "styles/palette.css": ":root { --brand-40: #abc; --primary-40: #cba; }",
        filename: source,
        **(extras or {}),
    }
    for relative, content in files.items():
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    command = [
        sys.executable,
        str(K_CHECKER),
        "--root",
        str(tmp_path),
        "--format",
        "json",
    ]
    command += ["--diff-stdin"] if diff is not None else [filename]
    result = subprocess.run(
        command, input=diff, text=True, capture_output=True, check=False
    )
    assert result.returncode in {0, 1}, result.stderr
    findings = json.loads(result.stdout)
    return [
        finding
        for finding in findings
        if finding["rule"] in {"UME-DS005", "UME-DS006", "UME-DS007", "UME-DS008"}
    ]


@pytest.mark.parametrize(
    "utility",
    [
        "border-b-[2.5px]",
        "p-[13px]",
        "bg-[#fff]",
        "bg-[rgb(0,0,0)]",
        "gap-[0.7rem]",
        "text-[15px]",
        "text-[rebeccapurple]",
        "z-[60]",
    ],
)
def test_raw_class_given_literal_value_expect_ds005(tmp_path, utility):
    findings = run_checker(tmp_path, f'<div className="{utility}" />')
    assert [finding["rule"] for finding in findings] == ["UME-DS005"]


@pytest.mark.parametrize(
    "source",
    [
        '<div className="border-b-2 text-caption p-3" />',
        '<path d="M13 15 L2.5 0.7" fill="currentColor" />',
        '<div className="data-[state=open]:bg-surface [&>svg]:p-3 transition-[color,opacity]" />',
        '<div className="w-[50%] grid-cols-[1fr_auto] min-h-[100dvh]" />',
        '<div className="w-[calc(var(--private-size)+2.5px)]" />',
        '// example: bg-[#fff]\nconst text = "hello";',
    ],
)
def test_raw_class_given_structural_or_token_value_expect_no_findings(tmp_path, source):
    assert run_checker(tmp_path, source) == []


@pytest.mark.parametrize(
    ("utility", "nearest"),
    [
        ("border-b-[2.5px]", "border-b-2"),
        ("text-[15px]", "text-sm"),
        ("text-[13px]", "text-caption"),
        ("p-[13px]", "p-3"),
    ],
)
def test_raw_class_given_known_scale_expect_nearest_utility(tmp_path, utility, nearest):
    findings = run_checker(tmp_path, f'const classes = "{utility}";')
    assert nearest in findings[0]["message"]


@pytest.mark.parametrize(
    ("utility", "message"),
    [
        ("bg-[var(--surface)]", "bg-surface"),
        ("bg-[var(--border-strong)]", "border-strong"),
        ("border-b-[var(--border-strong)]", "border-b-strong"),
        ("rounded-[var(--radius-sm)]", "rounded-sm"),
        ("max-w-[var(--private-size)]", "container-max"),
        ("text-[var(--not-defined)]", "not defined"),
    ],
)
def test_token_class_given_named_or_missing_token_expect_ds006(
    tmp_path, utility, message
):
    findings = run_checker(tmp_path, f'<div className="{utility}" />')
    assert [finding["rule"] for finding in findings] == ["UME-DS006"]
    assert message in findings[0]["message"]


@pytest.mark.parametrize(
    "utility",
    [
        "h-[var(--private-size)]",
        "w-[var(--radix-popover-trigger-width)]",
        "ring-[var(--border-strong)]",
        "ring-offset-[var(--surface)]",
    ],
)
def test_token_class_given_no_equivalent_or_runtime_token_expect_no_findings(
    tmp_path, utility
):
    assert run_checker(tmp_path, f'<div className="{utility}" />') == []


@pytest.mark.parametrize(
    "declaration",
    [
        "border-bottom: 2.5px solid var(--border-strong)",
        "padding: 13px",
        "font-size: 15px",
        "gap: 0.7rem",
        "color: #fff",
        "color: rgb(0 0 0)",
        "background: hsl(0 0% 100%)",
        "color: oklch(50% .1 200)",
        "color: red",
        "box-shadow: 0 0 8px rebeccapurple",
    ],
)
def test_css_declaration_given_raw_escape_expect_ds007(tmp_path, declaration):
    findings = run_checker(tmp_path, f".item {{ {declaration}; }}", "component.css")
    assert [finding["rule"] for finding in findings] == ["UME-DS007"]


@pytest.mark.parametrize(
    "source",
    [
        ".item { padding: 0 1px; margin: -1px; width: 50%; grid-template-columns: 1fr auto; }",
        ".item { padding: .75rem; width: 480px; border-width: 3px; border-radius: 4px; }",
        ".item { min-height: 100dvh; width: 92vw; min-width: 3.5ch; }",
        ".item { color: transparent; background: currentColor; border-color: inherit; }",
        ".item { width: calc(var(--private-size) + 2.5px); color: var(--surface); }",
        "@media (min-width: 713px) { .item { width: 100%; } }",
        "@keyframes run { 13% { transform: translateX(50%); } }",
        '.item { content: "red 13px #fff"; background-image: url("data:image/svg+xml,#fff"); }',
        ":root { --custom-surface: #aabbcc; --custom-size: 13px; }",
        '[data-theme="dark"] { --surface: rgb(0 0 0); --size: 13px; }',
        ".theme-dark { --surface: #000; }",
        "@theme { --color-special: #abc; --text-special: 0.7rem; }",
    ],
)
def test_css_declaration_given_scale_or_definition_expect_no_findings(tmp_path, source):
    assert run_checker(tmp_path, source, "component.css") == []


def test_css_declaration_given_component_property_definition_expect_ds007(tmp_path):
    findings = run_checker(tmp_path, ".item { --one-off: 13px; }", "component.css")
    assert [finding["rule"] for finding in findings] == ["UME-DS007"]


@pytest.mark.parametrize(
    ("filename", "source"),
    [
        ("Component.tsx", '<div style={{ color: "var(--brand-40)" }} />'),
        ("component.css", ".item { color: var(--brand-40); }"),
        (
            "Component.tsx",
            'const color = getComputedStyle(el).getPropertyValue("--brand-40");',
        ),
        ("Component.tsx", '<div className="bg-[var(--primary-40)]" />'),
    ],
)
def test_palette_read_given_component_expect_ds008(tmp_path, filename, source):
    findings = run_checker(tmp_path, source, filename)
    assert "UME-DS008" in {finding["rule"] for finding in findings}


@pytest.mark.parametrize(
    ("filename", "source"),
    [
        ("styles/theme-dark.css", ":root { --text: var(--brand-40); }"),
        (
            "Component.tsx",
            '<div className="border-strong" style={{ color: "var(--surface)" }} />',
        ),
        ("component.css", ":root { --role: var(--brand-40); }"),
    ],
)
def test_palette_read_given_theme_or_role_expect_no_findings(
    tmp_path, filename, source
):
    assert run_checker(tmp_path, source, filename) == []


@pytest.mark.parametrize(
    ("rule", "filename", "source", "comment"),
    [
        ("UME-DS005", "Component.tsx", '<div className="p-[13px]" />', "//"),
        ("UME-DS006", "Component.tsx", '<div className="bg-[var(--surface)]" />', "//"),
        ("UME-DS007", "component.css", ".item { padding: 13px; }", "/*"),
        ("UME-DS008", "component.css", ".item { color: var(--brand-40); }", "/*"),
    ],
)
def test_token_rule_given_explicit_suppression_expect_no_findings(
    tmp_path, rule, filename, source, comment
):
    suffix = " */" if comment == "/*" else ""
    assert (
        run_checker(
            tmp_path, f"{comment} ume-ignore: {rule}{suffix}\n{source}", filename
        )
        == []
    )


@pytest.mark.parametrize(
    "comment", ["// ume-ignore", "// ume-ignore: UME-DS006", "// ume-ignore: UME-DS"]
)
def test_token_rule_given_bare_or_wrong_suppression_expect_finding(tmp_path, comment):
    findings = run_checker(tmp_path, f'{comment}\n<div className="p-[13px]" />')
    assert [finding["rule"] for finding in findings] == ["UME-DS005"]


@pytest.mark.parametrize(
    ("filename", "source", "rule"),
    [
        ("Component.tsx", '<div className="p-[13px]" />', "UME-DS005"),
        ("Component.tsx", '<div className="bg-[var(--surface)]" />', "UME-DS006"),
        ("component.css", ".item { padding: 13px; }", "UME-DS007"),
        ("component.css", ".item { color: var(--brand-40); }", "UME-DS008"),
    ],
)
def test_diff_given_unchanged_escape_expect_only_changed_line(
    tmp_path, filename, source, rule
):
    content = f"{source}\n{source}\n"
    diff = f"--- a/{filename}\n+++ b/{filename}\n@@ -2 +2 @@\n-old\n+{source}\n"
    findings = run_checker(tmp_path, content, filename, diff)
    assert [(finding["rule"], finding["line"]) for finding in findings] == [(rule, 2)]


def test_diff_given_multiline_css_expect_literal_line(tmp_path):
    source = ".item {\n  border-bottom:\n    2.5px solid var(--border-strong);\n}\n"
    diff = "--- a/component.css\n+++ b/component.css\n@@ -3 +3 @@\n-old\n+    2.5px solid var(--border-strong);\n"
    findings = run_checker(tmp_path, source, "component.css", diff)
    assert [(finding["rule"], finding["line"]) for finding in findings] == [
        ("UME-DS007", 3)
    ]


@pytest.mark.parametrize(
    ("filename", "source"),
    [
        ("component.test.tsx", '<div className="p-[13px]" />'),
        ("tests/fixture.tsx", '<div className="bg-[var(--unknown)]" />'),
        ("fixtures/example.css", ".item { color: red; }"),
        (
            "Component.generated.tsx",
            '// This file was automatically generated.\nconst classes = "p-[13px]";',
        ),
    ],
)
def test_tokens_given_fixture_or_generated_source_expect_no_findings(
    tmp_path, filename, source
):
    assert run_checker(tmp_path, source, filename) == []


def test_tokens_given_rendered_story_expect_finding(tmp_path):
    findings = run_checker(
        tmp_path, '<div className="p-[13px]" />', "Component.stories.tsx"
    )
    assert [finding["rule"] for finding in findings] == ["UME-DS005"]


def test_token_discovery_given_unrelated_css_file_expect_named_mapping(tmp_path):
    findings = run_checker(
        tmp_path,
        '<div className="bg-[var(--paper)]" />',
        extras={
            "another/package/tokens.css": ":root { --paper: #fff; } @theme { --color-paper: var(--paper); }",
        },
    )
    assert [finding["rule"] for finding in findings] == ["UME-DS006"]
    assert "bg-paper" in findings[0]["message"]


@pytest.mark.parametrize(
    "utility",
    [
        "grid-cols-[minmax(0,1fr)_0rem]",
        "pb-[max(0.75rem,env(safe-area-inset-bottom))]",
        "w-[min(var(--private-size),calc(100%-3rem))]",
        "max-w-[calc(100vw-24px)]",
        "bg-[color-mix(in_srgb,var(--surface)_55%,transparent)]",
        "bg-[radial-gradient(ellipse_at_50%_30%,var(--surface),transparent_65%)]",
        "slide-in-from-top-[48%]",
    ],
)
def test_raw_class_given_relative_layout_formula_expect_no_findings(tmp_path, utility):
    assert run_checker(tmp_path, f'<div className="{utility}" />') == []


@pytest.mark.parametrize(
    "utility",
    [
        "max-w-[calc(100vw-13px)]",
        "pb-[max(13px,env(safe-area-inset-bottom))]",
        "bg-[color-mix(in_srgb,#fff_55%,transparent)]",
        "bg-[linear-gradient(#fff,transparent)]",
    ],
)
def test_raw_class_given_formula_with_escape_expect_ds005(tmp_path, utility):
    findings = run_checker(tmp_path, f'<div className="{utility}" />')
    assert [finding["rule"] for finding in findings] == ["UME-DS005"]


def test_css_declaration_given_token_calc_and_raw_sibling_expect_ds007(tmp_path):
    source = ".item { border: calc(var(--private-size) + 2.5px) solid #fff; padding: calc(var(--private-size) + 2px) 13px; }"
    findings = run_checker(tmp_path, source, "component.css")
    assert [finding["rule"] for finding in findings] == ["UME-DS007", "UME-DS007"]
    assert "#fff" in findings[0]["message"]
    assert "13px" in findings[1]["message"]


def test_css_declaration_given_gradient_layout_percentages_expect_no_findings(tmp_path):
    source = ".item { background-image: radial-gradient(ellipse at 50% 30%, var(--surface), transparent 65%); --glow: linear-gradient(var(--surface) 42%, transparent); }"
    assert run_checker(tmp_path, source, "component.css") == []


def test_diff_given_multiline_color_change_expect_changed_channel_line(tmp_path):
    source = ".item {\n  color: rgb(\n    255 0 0\n  );\n}\n"
    diff = "--- a/component.css\n+++ b/component.css\n@@ -3 +3 @@\n-old\n+    255 0 0\n"
    findings = run_checker(tmp_path, source, "component.css", diff)
    assert [(finding["rule"], finding["line"]) for finding in findings] == [
        ("UME-DS007", 3)
    ]


def test_diff_given_changed_selector_and_unchanged_literal_expect_no_findings(tmp_path):
    source = ".renamed {\n  padding: 13px;\n}\n"
    diff = (
        "--- a/component.css\n+++ b/component.css\n@@ -1 +1 @@\n-.old {\n+.renamed {\n"
    )
    assert run_checker(tmp_path, source, "component.css", diff) == []


def test_palette_class_given_discovered_palette_utility_expect_ds008(tmp_path):
    findings = run_checker(
        tmp_path,
        '<div className="bg-ink-40" />',
        extras={
            "styles/palette.css": ":root { --ink-40: #abc; }",
            "styles/bridge.css": "@theme { --color-ink-40: var(--ink-40); }",
        },
    )
    assert [finding["rule"] for finding in findings] == ["UME-DS008"]


def test_palette_read_given_numbered_role_expect_no_findings(tmp_path):
    findings = run_checker(
        tmp_path,
        '<div className="bg-chart-neutral-1" />',
        extras={
            "styles/roles.css": ":root { --chart-neutral-1: #abc; } @theme { --color-chart-neutral-1: var(--chart-neutral-1); }",
        },
    )
    assert findings == []


def test_tokens_given_storybook_css_host_expect_no_findings(tmp_path):
    assert (
        run_checker(
            tmp_path,
            "body { background: white; padding: 13px; }",
            "src/storybook/storyHost.css",
        )
        == []
    )


def test_token_class_given_generic_colour_namespace_expect_ring_utility(tmp_path):
    findings = run_checker(
        tmp_path,
        '<div className="ring-[var(--paper)]" />',
        extras={
            "styles/bridge.css": ":root { --paper: #fff; } @theme { --color-paper: var(--paper); }",
        },
    )
    assert [finding["rule"] for finding in findings] == ["UME-DS006"]
    assert "ring-paper" in findings[0]["message"]


def test_raw_class_given_theme_radius_override_expect_actual_scale_utility(tmp_path):
    findings = run_checker(
        tmp_path,
        '<div className="rounded-[8px]" />',
        extras={
            "styles/tokens.css": ":root { --radius: .75rem; } @theme { --radius-sm: calc(var(--radius) - 4px); }",
        },
    )
    assert "rounded-sm" in findings[0]["message"]


def test_palette_class_given_css_apply_expect_ds008(tmp_path):
    findings = run_checker(
        tmp_path,
        ".item { @apply bg-ink-40; }",
        "component.css",
        extras={
            "styles/palette.css": ":root { --ink-40: #abc; }",
            "styles/bridge.css": "@theme { --color-ink-40: var(--ink-40); }",
        },
    )
    assert [finding["rule"] for finding in findings] == ["UME-DS008"]


def test_css_declaration_given_unquoted_url_before_literals_expect_ds007(tmp_path):
    source = ".item { background-image: url(https://example.com/a.svg); color: #fff; padding: 13px; }"
    findings = run_checker(tmp_path, source, "component.css")
    assert [finding["rule"] for finding in findings] == ["UME-DS007", "UME-DS007"]


def test_css_declaration_given_url_and_colour_in_same_value_expect_ds007(tmp_path):
    source = ".item { background-image: url(https://example.com/a.svg), linear-gradient(red, transparent); }"
    findings = run_checker(tmp_path, source, "component.css")
    assert [finding["rule"] for finding in findings] == ["UME-DS007"]


def test_raw_class_given_arbitrary_property_expect_ds005(tmp_path):
    findings = run_checker(
        tmp_path,
        '<div className="[color:#fff] [border-bottom:2.5px_solid_var(--surface)]" />',
    )
    assert [finding["rule"] for finding in findings] == ["UME-DS005", "UME-DS005"]


def test_class_string_given_nested_templates_expect_all_token_rules(tmp_path):
    source = 'const classes = `${enabled ? `p-[13px] bg-[var(--missing)] text-[var(--primary-40)]` : ""}`;'
    findings = run_checker(tmp_path, source)
    assert {finding["rule"] for finding in findings} == {
        "UME-DS005",
        "UME-DS006",
        "UME-DS008",
    }


def test_palette_class_given_theme_css_apply_expect_no_findings(tmp_path):
    findings = run_checker(
        tmp_path,
        ".theme-root { @apply bg-ink-40; }",
        "styles/theme-light.css",
        extras={
            "styles/palette.css": ":root { --ink-40: #abc; }",
            "styles/bridge.css": "@theme { --color-ink-40: var(--ink-40); }",
        },
    )
    assert findings == []


def test_raw_class_given_custom_spacing_unit_expect_correct_utility(tmp_path):
    findings = run_checker(
        tmp_path,
        '<div className="p-[13px]" />',
        extras={
            "styles/tokens.css": "@theme { --spacing: 2px; }",
        },
    )
    assert "p-6.5" in findings[0]["message"]


def test_token_class_given_unknown_token_with_fallback_expect_ds006(tmp_path):
    findings = run_checker(
        tmp_path, '<div className="bg-[var(--missing,transparent)]" />'
    )
    assert [finding["rule"] for finding in findings] == ["UME-DS006"]


def test_token_class_given_raw_fallback_expect_ds005(tmp_path):
    findings = run_checker(tmp_path, '<div className="h-[var(--private-size,13px)]" />')
    assert [finding["rule"] for finding in findings] == ["UME-DS005"]


@pytest.mark.parametrize(
    "colour",
    [
        "rgb(255 0 0 / var(--opacity))",
        "rgba(255, 0, 0, var(--opacity))",
        "hsl(30 50% 50% / var(--opacity))",
        "oklch(50% .1 200 / var(--opacity))",
    ],
)
def test_css_colour_given_literal_channels_and_token_alpha_expect_ds007(
    tmp_path, colour
):
    findings = run_checker(tmp_path, f".item {{ color: {colour}; }}", "component.css")
    assert [finding["rule"] for finding in findings] == ["UME-DS007"]


def test_raw_class_given_literal_channels_and_token_alpha_expect_ds005(tmp_path):
    findings = run_checker(
        tmp_path, '<div className="bg-[rgb(255_0_0_/_var(--opacity))]" />'
    )
    assert [finding["rule"] for finding in findings] == ["UME-DS005"]


@pytest.mark.parametrize(
    "colour",
    [
        "rgb(var(--rgb-channels) / var(--opacity))",
        "rgb(var(--rgb-channels) / .5)",
        "hsl(var(--hsl-channels))",
    ],
)
def test_css_colour_given_token_channels_expect_no_findings(tmp_path, colour):
    assert run_checker(tmp_path, f".item {{ color: {colour}; }}", "component.css") == []


@pytest.mark.parametrize(
    "property_name", ["text-decoration", "text-decoration-thickness"]
)
def test_css_underline_given_integer_scale_thickness_expect_no_findings(
    tmp_path, property_name
):
    value = (
        "underline solid var(--border-strong) 3px"
        if property_name == "text-decoration"
        else "3px"
    )
    assert (
        run_checker(tmp_path, f".item {{ {property_name}: {value}; }}", "component.css")
        == []
    )


@pytest.mark.parametrize(
    "property_name", ["text-decoration", "text-decoration-thickness"]
)
def test_css_underline_given_non_scale_thickness_expect_ds007(tmp_path, property_name):
    value = (
        "underline solid var(--border-strong) 2.5px"
        if property_name == "text-decoration"
        else "2.5px"
    )
    findings = run_checker(
        tmp_path, f".item {{ {property_name}: {value}; }}", "component.css"
    )
    assert [finding["rule"] for finding in findings] == ["UME-DS007"]


def test_raw_class_given_underline_thickness_expect_nearest_utility(tmp_path):
    findings = run_checker(tmp_path, '<div className="decoration-[2.5px]" />')
    assert [finding["rule"] for finding in findings] == ["UME-DS005"]
    assert "decoration-2" in findings[0]["message"]
