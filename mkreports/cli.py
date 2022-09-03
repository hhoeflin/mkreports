"""Implement the CLI for mkreports."""
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import sh  # type: ignore
import typer

from .config import get_mkreports_dir
from .report import Report

app = typer.Typer()


@app.command()
def dir():
    """Print the directory mkreports uses by default to the screen."""
    typer.echo(f"{get_mkreports_dir()}")


def _process_out(line: str):
    typer.echo(line, nl=False, err=False)


def _process_err(line: str):
    typer.echo(line, nl=False, err=True)


@app.command()
def serve(
    mkreports_dir: Optional[Path] = typer.Argument(
        None,
        help="mkreports directory to use to serve out of. If not given, then "
        "default directory as shown by `dir` subcommand used.",
    ),
    mkdocs_args: List[str] = typer.Argument(
        None,
        help="All values passed directly to `mkdocs serve` function. "
        "Use `--` to separate options for mkdocs from options "
        "for the core command.",
    ),
):
    """
    Serve an mkdocs site.

    This is a convenience wrapper for `mkdocs serve` that
    changes to the correct directory
    and invokes `mkdocs serve`, restarting when error occur.
    """
    if mkreports_dir is None:
        mkreports_dir = get_mkreports_dir()

    mkdocs_cmd = f"cd {mkreports_dir} && mkdocs serve {' '.join(mkdocs_args)}"

    # we first do an initial start; this has to run without error
    # for a few seconds before the automatic restart is initiated
    if not mkreports_dir.is_dir():
        typer.echo(
            f"Directory {mkreports_dir} does not exist or is not a directory.", err=True
        )
        raise typer.Exit(1)

    # we do the initial run; this needs to last for at least 5 seconds;
    # if an error occurs in this time, we do not restart
    time_first_start = datetime.now()
    try:
        while True:
            try:
                typer.echo(f"Run bash command: {mkdocs_cmd}")
                cmd = sh.bash(
                    "-c", mkdocs_cmd, _out=_process_out, _err=_process_err, _bg=True
                )  # type: ignore
                cmd.wait()
            except sh.ErrorReturnCode:
                time_error = datetime.now()

                elapsed_time = time_error - time_first_start
                if elapsed_time.total_seconds() <= 5:
                    typer.echo("Error occured before 5 seconds. Exiting.")
                    raise typer.Exit(2)
                else:
                    typer.echo("Restarting!")

    except KeyboardInterrupt:
        try:
            if cmd.is_alive():  # type: ignore
                cmd.terminate()  # type: ignore
                typer.echo("\nTerminated mkdocs serve")
            typer.Abort()
        except UnboundLocalError:
            pass


@app.command()
def new(
    mkreports_dir: Optional[Path] = typer.Argument(
        None,
        help="mkreports directory to use to serve out of. If not given, then default directory as shown by `dir` subcommand used.",
    ),
    name: str = typer.Option("Mkreports report", help="Name of the report"),
):
    """Create a new mkreports report."""
    if mkreports_dir is None:
        mkreports_dir = get_mkreports_dir()
    try:
        Report.create(mkreports_dir, report_name=name)
        typer.echo(f"Create report in {mkreports_dir}")
    except:
        if mkreports_dir.is_dir():
            typer.echo(
                f"Directory already exists and could not create report in {mkreports_dir}"
            )
        else:
            typer.echo(f"Could not create report in {mkreports_dir}")


if __name__ == "__main__":
    app()
