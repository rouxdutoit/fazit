# SPDX-License-Identifier: AGPL-3.0-or-later
from importlib.resources import files
from pathlib import Path
from typing import Annotated, Never

import typer

from . import PROJECT_NAME, __version__
from .catalogue import load_catalogue
from .errors import InputError
from .i18n import DEFAULT_LANGUAGE, SUPPORTED_LANGUAGES, error_sentence, load_locale
from .model import load_scan, load_scan_text, scan_to_json
from .output import write_inside
from .parsing import parse_yaml, read_text, reject_at_signs
from .report import render_report, report_file_name

app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    pretty_exceptions_enable=False,
    invoke_without_command=True,
)


@app.callback()
def options(
    ctx: typer.Context,
    debug: Annotated[bool, typer.Option("--debug", help="Show a traceback for errors.")] = False,
    version: Annotated[
        bool, typer.Option("--version", help="Show the tool version.", is_eager=True)
    ] = False,
) -> None:
    if version:
        typer.echo(load_locale(DEFAULT_LANGUAGE)["cli"]["version"].format(version=__version__))
        raise typer.Exit()
    ctx.obj = debug


def _check_language(lang: str) -> None:
    if lang not in SUPPORTED_LANGUAGES:
        raise InputError("unsupported_language", file=PROJECT_NAME, field="--lang")


def _exit_with_error(ctx: typer.Context, lang: str, error: InputError) -> Never:
    if ctx.obj:
        raise error
    strings = load_locale(lang if lang in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE)
    message = error_sentence(strings, error)
    typer.echo(strings["cli"]["error_prefix"].format(message=message), err=True)
    raise typer.Exit(2) from None


@app.command()
def demo(
    ctx: typer.Context,
    out: Annotated[Path, typer.Option(help="Directory for the output files.")] = Path("report"),
    lang: Annotated[str, typer.Option(help="Report language (en or de).")] = DEFAULT_LANGUAGE,
    sample: Annotated[str, typer.Option(help="Bundled sample (town or nonprofit).")] = "town",
) -> None:
    """Build a report from bundled sample data."""
    try:
        _check_language(lang)
        if sample not in ("town", "nonprofit"):
            raise InputError("unsupported_sample", file=PROJECT_NAME, field="--sample")
        sample_files = files("m365_exit_scan").joinpath("demo", sample)
        source = sample_files.joinpath("scan.json")
        inputs = sample_files.joinpath("inputs.yaml")
        catalogue = load_catalogue()
        scan = load_scan_text(read_text(source), source.name, catalogue)
        inputs_text = read_text(inputs)
        reject_at_signs(parse_yaml(inputs_text, inputs.name), inputs.name)

        html = render_report(scan, lang=lang, catalogue=catalogue)
        stamp = f"{scan.generated_at[:10]}-{lang}"
        scan_path = write_inside(out, f"scan-{stamp}.json", scan_to_json(scan))
        inputs_path = write_inside(out, f"inputs-{stamp}.yaml", inputs_text)
        path = write_inside(out, report_file_name(scan.generated_at, lang=lang), html)
    except InputError as error:
        _exit_with_error(ctx, lang, error)
    strings = load_locale(lang)["cli"]
    typer.echo(strings["sample_scan"].format(path=scan_path))
    typer.echo(strings["sample_inputs"].format(path=inputs_path))
    typer.echo(str(path))


@app.command()
def report(
    ctx: typer.Context,
    scan_json: Annotated[Path, typer.Argument(help="Scan JSON file to rebuild the report from.")],
    lang: Annotated[str, typer.Option(help="Report language (en or de).")] = DEFAULT_LANGUAGE,
    out: Annotated[Path, typer.Option(help="Directory for the report.")] = Path("report"),
) -> None:
    """Build a report from an existing scan file."""
    try:
        _check_language(lang)
        catalogue = load_catalogue()
        scan = load_scan(scan_json, catalogue)
        html = render_report(scan, lang=lang, catalogue=catalogue)
        path = write_inside(out, report_file_name(scan.generated_at, lang=lang), html)
    except InputError as error:
        _exit_with_error(ctx, lang, error)
    typer.echo(str(path))


def main() -> None:
    app()
