import json

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax


def printf(json_obj) -> None:
    """Pretty print a JSON object.
    """
    try:
        console = Console()
        json_str = json.dumps(json_obj, indent=4, sort_keys=True)
        syntax = Syntax(json_str, "json", theme="monokai", line_numbers=True)
        console.print(Panel(syntax, title="AST JSON Output", border_style="blue"))
    except (TypeError, ValueError):
        print(json.dumps(json_obj, indent=4, sort_keys=True))
