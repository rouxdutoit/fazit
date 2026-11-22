# SPDX-License-Identifier: AGPL-3.0-or-later
from importlib.resources import files
from os.path import join
from pathlib import Path
from typing import Annotated, Never

import typer
from typer.core import TyperCommand

from . import __version__
from .catalogue import load_catalogue
from .errors import InputError
from .i18n import (
    DEFAULT_LANGUAGE,
    SUPPORTED_LANGUAGES,
    error_sentence,
    escape_controls,
    load_locale,
)
from .inputs import Inputs, load_inputs, load_inputs_text
from .model import load_scan, load_scan_text
from .output import write_files, write_inside
from .parsing import read_text
from .report import render_demo, render_report, report_file_name
from .rules import PROFILES

app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    pretty_exceptions_enable=False,
    invoke_without_command=True,
)
_PROFILE_HELP = f"Target profile ({', '.join(PROFILES)})."
_SCAN_JSON = "SCAN_JSON"


class _ReportCommand(TyperCommand):
    def collect_usage_pieces(self, ctx: typer.Context) -> list[str]:
        return [
            _SCAN_JSON if piece == f"{{{_SCAN_JSON}}}" else piece
            for piece in super().collect_usage_pieces(ctx)
        ]


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
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit(2)
    ctx.obj = debug


def _check_language(lang: str) -> None:
    if lang not in SUPPORTED_LANGUAGES:
        raise InputError("unsupported_language", field="--lang")


def _printed_path(path: Path, out: str) -> str:
    cwd = Path.cwd()
    if path.is_relative_to(cwd):
        # A resolved path can expose directory names behind a user-supplied link.
        try:
            relative = Path(out).absolute().relative_to(cwd, walk_up=True)
        except ValueError:
            pass
        else:
            return escape_controls(str(relative / path.name))
    return escape_controls(join(out, path.name))


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
    out: Annotated[str, typer.Option(help="Directory for the output files.")] = "report",
    lang: Annotated[str, typer.Option(help="Report language (en or de).")] = DEFAULT_LANGUAGE,
    sample: Annotated[str, typer.Option(help="Bundled sample (town or nonprofit).")] = "town",
    profile: Annotated[str, typer.Option(help=_PROFILE_HELP)] = "opendesk",
) -> None:
    """Build a report from bundled sample data."""
    try:
        _check_language(lang)
        if sample not in ("town", "nonprofit"):
            raise InputError("unsupported_sample", field="--sample")
        sample_files = files("fazit").joinpath("demo", sample)
        source = sample_files.joinpath("scan.json")
        answers = sample_files.joinpath("inputs.yaml")
        catalogue = load_catalogue()
        scan = load_scan_text(read_text(source), source.name, catalogue)
        inputs_text = read_text(answers)
        inputs = load_inputs_text(inputs_text, answers.name, catalogue)

        html, scan_copy = render_demo(
            scan, lang=lang, profile=profile, catalogue=catalogue, inputs=inputs
        )
        stamp = f"{scan.generated_at[:10]}-{lang}"
        scan_path, inputs_path, path = write_files(
            out,
            {
                f"scan-{stamp}.json": scan_copy,
                f"inputs-{stamp}.yaml": inputs_text,
                report_file_name(scan.generated_at, lang=lang): html,
            },
        )
    except InputError as error:
        _exit_with_error(ctx, lang, error)
    strings = load_locale(lang)["cli"]
    typer.echo(strings["sample_scan"].format(path=_printed_path(scan_path, out)))
    typer.echo(strings["sample_inputs"].format(path=_printed_path(inputs_path, out)))
    typer.echo(_printed_path(path, out))


@app.command(cls=_ReportCommand)
def report(
    ctx: typer.Context,
    scan_json: Annotated[
        Path,
        typer.Argument(
            metavar=_SCAN_JSON, readable=False, help="Scan JSON file to rebuild the report from."
        ),
    ],
    inputs: Annotated[
        Path | None, typer.Option(readable=False, help="YAML file with manual answers and costs.")
    ] = None,
    lang: Annotated[str | None, typer.Option(help="Report language (en or de).")] = None,
    out: Annotated[str, typer.Option(help="Directory for the report.")] = "report",
    profile: Annotated[str | None, typer.Option(help=_PROFILE_HELP)] = None,
) -> None:
    """Build a report from an existing scan file."""
    message_lang = lang if lang is not None else DEFAULT_LANGUAGE
    try:
        _check_language(message_lang)
        catalogue = load_catalogue()
        scan = load_scan(scan_json, catalogue)
        answers = load_inputs(inputs, catalogue) if inputs is not None else Inputs()
        report_lang = lang if lang is not None else answers.language or DEFAULT_LANGUAGE
        target = profile if profile is not None else answers.target_profile or "opendesk"
        html = render_report(
            scan,
            lang=report_lang,
            profile=target,
            catalogue=catalogue,
            inputs=answers if inputs is not None else None,
            scan_file_name=scan_json.name,
        )
        path = write_inside(out, report_file_name(scan.generated_at, lang=report_lang), html)
    except InputError as error:
        _exit_with_error(ctx, message_lang, error)
    typer.echo(_printed_path(path, out))


def main() -> None:
    app()
