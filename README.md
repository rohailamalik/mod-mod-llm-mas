
# modmod-llm-mas

Modular Modelling with LLMs: A Multi-Agent System for Generating Standardized Simulation Models


## File Structure

```
.
├── PythonSim/             # Simulation library for component modeling
├── agents/                # Agent roles
├── results/               # Saved HTML outputs
└── README.md              # ReadME file
├── llm_client.py          # Creates LLM chat model
├── main.py                # Entry point script to run everything
├── multi_agent_graph.py   # Defines and compiles MAS graph
├── requirements.txt       # Dependencies required
├── results_pipeline.py    # Runs tasks and collects results
├── utils.py               # Helper functions
├── val_tests.py           # Unit tests script used by the Validator agent
```

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/rohailamalik/modmod-llm-mas.git
   cd modmod-llm-mas
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate 
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Define the LLM chat model. You can use any [model supported by LangChain](https://python.langchain.com/docs/integrations/chat/), import relevant packages, and name the model as ```model``` in ```llm_client.py``` to be automatically imported into the other files. 


## Running the System

To run tasks and generate results, define the tasks in ```main.py``` and run the file. This will:
- Run each task through the multi-agent system
- Save the results in `task_runs.json`
- Generate an HTML summary in `results.html`

## Notes

- The system currently uses the OpenAI GPT-4o model via Aalto's Azure deployment.
- All modeling is done in Python with a formal template inspired by Simscape-style modularity.

## Research Context

This project is part of an ongoing research effort to explore AI for autonomous modeling and simulation, and broader Generative Design at Aalto University School of Engineering.
