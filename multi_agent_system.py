from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.types import Command
from langchain_core.messages import HumanMessage

from agents.architect import architect
from agents.engineer import engineer
from agents.validator import validator
from agents.scientist import scientist

from utils import cost_calculator


# Define state schema
class TeamState(TypedDict):
    chat: Annotated[List, add_messages]
    scientist_itr: int
    validator_itr: int


# General agent invocation function
def invoke_agent(agent, state: TeamState, agent_name: str, verbose=False, print_resp=False):
    agent_response = agent.invoke({"messages": state["chat"]})
    cost_calculator(agent_response, verbose=verbose)
    if print_resp:
        print(f"{agent_name} : {agent_response["messages"][-1].content}")
    return agent_response["messages"][-1]


# Routing decision logic
def route(state: TeamState, agent_key: str, response, max_itr: int, success_goto: str, retry_goto: str):
    if "PASS" in response.content or state[f"{agent_key}_itr"] >= max_itr:
        return success_goto
    state[f"{agent_key}_itr"] += 1
    return retry_goto


# Agent nodes
def architect_node(state: TeamState):
    response = invoke_agent(architect, state, "architect", print_resp=False)
    state["chat"].append(response)
    return Command(goto="engineer"), state

def engineer_node(state: TeamState):
    response = invoke_agent(engineer, state, "engineer", print_resp=False)
    state["chat"].append(response)
    return Command(goto="validator"), state

def validator_node(state: TeamState):
    response = validator.invoke(state["chat"][-1].content)
    #print("Validator: ", response.content)
    next_node = route(
        state=state,
        agent_key="validator",
        response=response,
        max_itr=2,
        success_goto="scientist",
        retry_goto="engineer"
    )
    if next_node == "engineer":
        state["chat"].append(response) # Only put to chat if going to engineer with errors. Otherwise pass may confuse scientist
    return Command(goto=next_node), state

def scientist_node(state: TeamState):
    response = invoke_agent(scientist, state, "scientist", print_resp=False)
    state["chat"].append(response)
    next_node = route(
        state=state,
        agent_key="scientist",
        response=response,
        max_itr=2,
        success_goto=END,
        retry_goto="engineer"
    )
    return Command(goto=next_node), state


# Build the Graph
mas_graph = StateGraph(TeamState)
mas_graph.add_node("architect", architect_node)
mas_graph.add_node("engineer", engineer_node)
mas_graph.add_node("validator", validator_node)
mas_graph.add_node("scientist", scientist_node)
mas_graph.add_edge(START, "architect")
mas_runner = mas_graph.compile()


# Function to run the graph
def run_mas(user_input: str, reset_state=False):
    if not hasattr(run_mas, "state") or reset_state:
        run_mas.state = {
            "chat": [],
            "scientist_itr": 0,
            "validator_itr": 0,
        }

    run_mas.state["chat"].append(HumanMessage(content=user_input))

    responses = []
    last_state = None

    for event in mas_runner.stream(run_mas.state):
        for role, state_update in event.items():
            last_state = state_update
            chat = state_update.get("chat", [])
            if chat:
                responses.append({"role": role, "content": chat[-1].content})

    if last_state:
        run_mas.state.update(last_state)

    return responses if responses else [{"role": "Error", "content": "Error. No response generated."}]

# Function to get the final response after one entire execution of the graph
def respond(user_input: str):
    responses = run_mas(user_input)
    return responses[-1]["content"]
