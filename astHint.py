import click

from compare import compare_solutions


@click.group()
@click.option(
    "--log-level",
    type=str,
    default="WARNING",
    help="Log level: DEBUG|INFO|WARNING|ERROR|CRITICAL",
)
def astHint(log_level):
    pass


@astHint.command()
def hello():
    click.echo('Hello, World!')


# This command should ask the user for the path of the two files to compare
# and then call the comparator function with the two ASTs
@astHint.command()
@click.argument('student_solution', type=click.File('r'))
@click.argument('correct_solution', type=click.File('r'))
def compare(student_solution, correct_solution):
    click.echo('Comparing two files...')

    # Read the content of the first file
    content1 = student_solution.read()
    content2 = correct_solution.read()
    click.echo('Comparing the given files...')
    hint = compare_solutions(content1, content2)
    click.echo('Your hint is:')
    click.echo(hint)


@astHint.command()
def logo():
    click.echo("                                                 ")
    click.echo("                                                 ")
    click.echo(
        click.style("███████╗", fg="red")
        + click.style("██████╗ ", fg="yellow")
        + click.style("██╗  ██╗", fg="green")
        + "      "
        + click.style(" ██████╗", fg="cyan")
        + click.style("██╗     ██╗", fg="blue")
    )
    click.echo(
        click.style("██╔════╝", fg="red")
        + click.style("╚════██╗", fg="yellow")
        + click.style("╚██╗██╔╝", fg="green")
        + "      "
        + click.style("██╔════╝", fg="cyan")
        + click.style("██║     ██║", fg="blue")
    )
    click.echo(
        click.style("█████╗  ", fg="red")
        + click.style(" █████╔╝", fg="yellow")
        + click.style(" ╚███╔╝ ", fg="green")
        + "█████╗"
        + click.style("██║     ", fg="cyan")
        + click.style("██║     ██║", fg="blue")
    )
    click.echo(
        click.style("██╔══╝  ", fg="red")
        + click.style(" ╚═══██╗", fg="yellow")
        + click.style(" ██╔██╗ ", fg="green")
        + "╚════╝"
        + click.style("██║     ", fg="cyan")
        + click.style("██║     ██║", fg="blue")
    )
    click.echo(
        click.style("███████╗", fg="red")
        + click.style("██████╔╝", fg="yellow")
        + click.style("██╔╝ ██╗", fg="green")
        + "      "
        + click.style("╚██████╗", fg="cyan")
        + click.style("███████╗██║", fg="blue")
    )
    click.echo(
        click.style("╚══════╝", fg="red")
        + click.style("╚═════╝ ", fg="yellow")
        + click.style("╚═╝  ╚═╝", fg="green")
        + "      "
        + click.style(" ╚═════╝", fg="cyan")
        + click.style("╚══════╝╚═╝", fg="blue")
    )
    click.echo("                                                 ")
    click.echo("                                                 ")


if __name__ == "__main__":
    astHint()
