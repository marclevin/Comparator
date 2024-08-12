import click

from compare import compare_and_return_new_goal
from generator import generate_ai_hint

fg_ast_hint = 'blue'


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
    edit, _ = compare_internal(content1, content2)
    click.echo((click.style(f'Your hint is::{edit}', fg='blue')))


def compare_internal(student_solution, correct_solution):
    click.echo(click.style('Comparing the given files...', fg=fg_ast_hint))
    try:
        hint, new_goal = compare_and_return_new_goal(student_solution, correct_solution, True)
    except FileNotFoundError as e:
        raise click.ClickException(f"Error: {e}")
    return hint, new_goal


@ast_hint.command()
@click.argument('student_solution', type=click.File('r'))
@click.argument('correct_solution', type=click.File('r'))
@click.argument('problem_description', type=click.File('r'))
def generative_ai_hint(student_solution, correct_solution, problem_description):
    """
    Generate a hint using comparator & AI.
    """
    # validate that we are receiving python files and a text file
    if not student_solution.name.endswith('.py'):
        raise click.ClickException('Error: student_solution must be a python file')
    if not correct_solution.name.endswith('.py'):
        raise click.ClickException('Error: correct_solution must be a python file')
    if not problem_description.name.endswith('.txt'):
        raise click.ClickException('Error: problem_description must be a text file')

    student_solution = student_solution.read()
    correct_solution = correct_solution.read()
    problem_description = problem_description.read()
    edit, new_goal = compare_internal(student_solution, correct_solution)
    click.echo(click.style(text='Generating a hint from the AI...', fg=fg_ast_hint))
    short_hint = generate_ai_hint(problem_description, student_solution, edit, new_goal)
    click.echo(click.style(text="Your hint is:", fg=fg_ast_hint))
    click.echo(click.style(short_hint, fg='green'))


def test_generative_ai_hint():
    student_solution = open(
        'C:\\Users\\marcl\\OneDrive\\Desktop\\University\\AST-Hints\\Comparator\\problems/p1/student_code.py', 'r')
    correct_solution = open(
        'C:\\Users\\marcl\\OneDrive\\Desktop\\University\\AST-Hints\\Comparator\\problems/p1/goal_code.py', 'r')
    problem_description = open(
        'C:\\Users\\marcl\\OneDrive\\Desktop\\University\\AST-Hints\\Comparator\\problems/p1/description.txt', 'r')

    student_solution = student_solution.read()
    correct_solution = correct_solution.read()
    problem_description = problem_description.read()
    edit, new_goal = compare_internal(student_solution, correct_solution)
    click.echo(click.style(text='Generating a hint from the AI...', fg=fg_ast_hint))
    short_hint = generate_ai_hint(problem_description, student_solution, edit, new_goal)
    click.echo(click.style(text="Your hint is:", fg=fg_ast_hint))
    click.echo(click.style(short_hint, fg='green'))


if __name__ == "__main__":
    ast_hint()
