from html import escape
from typing import List
from pydantic import json
from multi_agent_system import run_mas

def run_tasks_and_save(tasks: List[str], filename="task_runs.json", runs_per_task=3):
    """
        Runs the Multi-Agent System for the specified tasks for a given number of times,
        and saves the results to a JSON file.

        Args:
            tasks (List): A list of task strings.
            filename (str): The name for the JSON results file.
            runs_per_task (int): Number of runs for each task

        """
    all_data = []

    for idx, task in enumerate(tasks, start=1):
        task_entry = {
            "task": task,
            "runs": []
        }
        print(f"\nTask {idx} of {len(tasks)}: {task[:60].strip()}...")
        for run_id in range(runs_per_task):
            try:
                responses = run_mas(task,
                                    reset_state=True)  # should return a list of dicts: [{"role":..., "content":...}]
                task_entry["runs"].append({"responses": responses})
                print(f"  Run {run_id + 1} done")
            except Exception as e:
                print(f"  Run {run_id + 1} failed: {e}")
                task_entry["runs"].append({"responses": [{"role": "error", "content": str(e)}]})
        all_data.append(task_entry)

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=4, ensure_ascii=False)

    print(f"\nAll {len(tasks)} tasks saved to {filename}")


def convert_results_to_html(json_filename="task_runs.json", html_filename="results.html"):
    """
        Converts the results from the JSON file into a structured HTML file and saves it.

        Args:
            json_filename (str): The name of the JSON file from where to read the results.
            html_filename (str): The name of the HTML file to be created and results saved to.

        """

    with open(json_filename, "r", encoding="utf-8") as f:
        task_data = json.load(f)

    html_parts = [
        '<html><head><meta charset="utf-8"><style>td{vertical-align:top;white-space:pre-wrap;padding:5px;border:1px solid #ccc;}</style></head><body>']

    for task_entry in task_data:
        task_text = escape(task_entry["task"])
        html_parts.append(f"<h3>Task:</h3><p>{task_text}</p>")
        html_parts.append("<table>")

        # Each run now contains a list of {"role": ..., "content": ...}
        runs = task_entry["runs"]
        response_lists = [run["responses"] for run in runs]

        # Determine the max number of rows needed (longest run)
        max_len = max(len(responses) for responses in response_lists)

        # Pad shorter runs
        for i in range(len(response_lists)):
            while len(response_lists[i]) < max_len:
                response_lists[i].append({"role": "", "content": ""})

        # Create rows
        for row_idx in range(max_len):
            html_parts.append("<tr>")
            for run in response_lists:
                role = escape(run[row_idx]["role"])
                content = escape(run[row_idx]["content"])
                html_parts.append(f"<td>{role}</td><td>{content}</td>")
            html_parts.append("</tr>")

        html_parts.append("</table><br><hr><br>")

    html_parts.append("</body></html>")

    with open(html_filename, "w", encoding="utf-8") as f:
        f.write("\n".join(html_parts))

    print(f"HTML output saved to {html_filename}")