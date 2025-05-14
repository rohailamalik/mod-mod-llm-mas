from langgraph.prebuilt import create_react_agent
from llm_client import llm
from langchain_core.tools import tool

system_prompt = """
You are an engineering assistant working in a team developing simulation models of dynamic engineering system components.
Your job is to create a comprehensive and to-the-point problem statement for the rest of the team.

For the given component, identify input and output variables using the given tool. Only consider electrical and mechanical domains.
Start by identifying the power flow ports for the component. If one single port acts in both directions, consider the direction which corresponds with the basic function of the component
If specific power variables or domains are provided by the user, use those as-is and do not modify them.

Finally, organize the given requirements and input and output variables into a comprehensive problem statement paragraph, without any bullets. 
It should tell what component is to be modeled and any other requirements, all the input variables first, and then output variables, as obtained from the tool. Do not mention flows here, only variables.
Then also mention any external (not internal) control input variables based on information given by the user.

Be to the point and avoid unnecessary details.

"""

@tool
def get_io_variables(domain: str, direction: str) -> dict:
    """
    Given a power domain and direction, returns input and output variables.

    Parameters:
    - domain: 'electrical', 'rotational', 'translational'
    - direction: 'in' or 'out' (with respect to the component)

    Returns:
    - dict with 'input' and 'output' variable names
    """

    domain = domain.lower()
    direction = direction.lower()

    if domain not in ['electrical', 'rotational', 'translational']:
        raise ValueError(f"Unsupported domain: {domain}. Must be 'electrical', 'rotational' or 'translational'")
    if direction not in ['in', 'out']:
        raise ValueError(f"Direction must be 'in' or 'out', got {direction}")

    # Define effort and flow variables per domain
    domain_vars = {
        'electrical': {'effort': 'voltage', 'flow': 'current'},
        'rotational': {'effort': 'torque', 'flow': 'angular_speed'},
        'translational': {'effort': 'force', 'flow': 'linear_speed'},
    }

    effort = domain_vars[domain]['effort']
    flow = domain_vars[domain]['flow']

    if direction == 'in':
        return {'input': effort, 'output': flow}
    else:  # direction == 'out'
        return {'input': flow, 'output': effort}


# Create agent
architect = create_react_agent(llm, tools = [get_io_variables], prompt=system_prompt)
