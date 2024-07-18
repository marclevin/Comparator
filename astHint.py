import click

from compare import compare_solutions
from generator import generate_ai_hint


@click.group()
@click.option(
    "--log-level",
    type=str,
    default="WARNING",
    help="Log level: DEBUG|INFO|WARNING|ERROR|CRITICAL",
)
def ast_hint(log_level):
    pass


# Define the ASCII art by lines
ascii_art_lines = [
    "            _____ _______     _    _ _       _       ",
    "     /\\    / ____|__   __|   | |  | (_)     | |      ",
    "    /  \\  | (___    | |______| |__| |_ _ __ | |_ ___ ",
    "   / /\\ \\  \\___ \\   | |______|  __  | | '_ \\| __/ __|",
    "  / ____ \\ ____) |  | |      | |  | | | | | | |_\\__ \\",
    " /_/    \\_\\_____/   |_|      |_|  |_|_|_| |_|\\__|___/"
]

# Define rainbow colors using ANSI escape codes
rainbow_colors = [
    "\033[31m",  # Red
    "\033[33m",  # Yellow
    "\033[32m",  # Green
    "\033[34m",  # Blue
    "\033[35m",  # Magenta (for indigo)
    "\033[36m"  # Cyan (for violet)
]


@ast_hint.command()
def logo():
    """Shows the ASCII art logo for AST-Hints"""
    for i, line in enumerate(ascii_art_lines):
        color = rainbow_colors[i % len(rainbow_colors)]
        click.echo(f"{color}{line}\033[0m")


@ast_hint.command()
@click.argument('student_solution', type=click.File('r'))
@click.argument('correct_solution', type=click.File('r'))
def compare(student_solution, correct_solution):
    """
    Compare the given files.
    """
    content1 = student_solution.read()
    content2 = correct_solution.read()
    compare_internal(content1, content2)


def compare_internal(student_solution, correct_solution) -> str:
    click.echo('Comparing the given files...')
    try:
        hint = compare_solutions(student_solution, correct_solution)
    except FileNotFoundError as e:
        raise click.ClickException(f"Error: {e}")
    return hint


@ast_hint.command()
@click.argument('student_solution', type=click.File('r'))
@click.argument('correct_solution', type=click.File('r'))
@click.argument('problem_description', type=click.File('r'))
def generative_ai_hint(student_solution, correct_solution, problem_description):
    """
    Generate a hint using comparator & AI.
    """
    student_solution = student_solution.read()
    correct_solution = correct_solution.read()
    problem_description = problem_description.read()
    edit = compare_internal(student_solution, correct_solution)
    click.echo('Generating a hint from the AI...')
    short_hint = generate_ai_hint(problem_description, student_solution, edit)
    click.echo('Your hint is:')
    click.echo(short_hint)


if __name__ == "__main__":
    ast_hint()
