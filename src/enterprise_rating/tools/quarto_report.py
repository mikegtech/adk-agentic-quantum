"""- Accepts a JSON-serializable list of dicts (e.g. AST nodes, 60 steps, etc.) as its single argument.
- Writes out a `report.qmd` by copying `report_template.qmd` into a temp folder and injecting the JSON into it.
- Calls `quarto render report.qmd --to html --output report.html`.
- Reads back `report.html` and returns its contents as a string. ADK will then present it as “HTML” in the web UI.
"""

import json
import os
import subprocess
import tempfile
from typing import Any

from google.adk.agents.callback_context import CallbackContext


class QuartoReportTool:
    """Tool: render a JSON‐list into a Quarto HTML report.
    - arguments["data"] should be a list of dicts, for example:
        [ { "step": 1, "description": "Init", "status": "Done" }, … ]
    """

    name = "generate_quarto_report"
    description = (
        "Given a JSON array of rows (e.g. AST nodes or process steps), produce a "
        "formatted HTML report via Quarto. Returns the raw HTML string."
    )

    def schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "data": {
                    "type": "array",
                    "description": "A list of objects (dicts) to report on.",
                    "items": { "type": "object" }
                }
            },
            "required": ["data"]
        }

    def run(self, arguments: dict[str, Any], context: CallbackContext) -> str:
        # 1) Grab the list of dicts
        rows = arguments["data"]
        data_json = json.dumps(rows)

        # 2) Create a temporary directory to hold the .qmd and outputs
        with tempfile.TemporaryDirectory() as tmpdir:
            # a) Write data_json to a file so our template can read it
            #    (alternatively, we inject directly into the .qmd)
            data_file = os.path.join(tmpdir, "rows.json")
            with open(data_file, "w") as f:
                f.write(data_json)

            # b) Copy the “report_template.qmd” into tmpdir, but replace a placeholder
            #    For simplicity, we'll just read a fixed template and substitute a variable.
            #    (You could also use Jinja2 or string.replace.)
            template_path = os.path.join(os.path.dirname(__file__), "report_template.qmd")
            with open(template_path) as src:
                template = src.read()

            # Replace a placeholder like {{DATA_JSON}} in the template with our JSON string.
            # In our example template above, we expected a variable "data_json" in Python chunks.
            # So we can simply prepend a Python chunk that sets data_json.
            injection = f"```{{python}}\n" \
                        f"data_json = '''{data_json}'''\n" \
                        f"```"
            final_qmd = injection + "\n\n" + template

            qmd_path = os.path.join(tmpdir, "report.qmd")
            with open(qmd_path, "w") as out:
                out.write(final_qmd)

            # 3) Run Quarto to render HTML
            html_out = os.path.join(tmpdir, "report.html")
            try:
                subprocess.run(
                    ["quarto", "render", qmd_path, "--to", "html", "--output", html_out],
                    check=True,
                    cwd=tmpdir
                )
            except subprocess.CalledProcessError as e:
                return f"<pre>Quarto failed: {e}</pre>"

            # 4) Read back the generated HTML
            with open(html_out, encoding="utf-8") as f_html:
                html_content = f_html.read()

        # 5) Return the raw HTML. ADK will treat it as “web content.”
        return html_content
