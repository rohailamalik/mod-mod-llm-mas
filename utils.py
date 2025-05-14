import os
import json

def cost_calculator(response, file_name="costs.json", verbose=False):
    """
    Extracts token usage, calculates costs, updates cumulative costs per model,
    and maintains an overall cumulative cost across all models.

    Args:
        response (dict): The API response containing messages and metadata.
        file_name (str): The name of the file where cumulative costs are stored.
        verbose (binary): The condition if the cost details are printed


    Returns:
        dict: A dictionary containing updated cumulative costs per model and overall.
    """
    try:
        ai_message = response["messages"][-1]
        model = ai_message.response_metadata.get("model_name", "")

        # Model pricing: Dollars per million tokens
        model_pricing = {
            "gpt-4o-2024-08-06": {"input_cost": 2.75, "output_cost": 11},
            "gpt-o1-2024-12-17": {"input_cost": 16.5, "output_cost": 66},
            "gpt-o1-mini-2024-09-12": {"input_cost": 1.21, "output_cost": 4.84},
        }

        # Get cost per model (0 if unknown model)
        unit_input_cost = model_pricing.get(model, {}).get("input_cost", 2.75)
        unit_output_cost = model_pricing.get(model, {}).get("output_cost", 11)

        # Extract token usage
        token_usage = ai_message.response_metadata.get("token_usage", {})
        input_tokens = token_usage.get("prompt_tokens", 0)
        output_tokens = token_usage.get("completion_tokens", 0)

        # Calculate costs
        input_costs = (unit_input_cost * input_tokens) / 1_000_000
        output_costs = (unit_output_cost * output_tokens) / 1_000_000
        total_costs = input_costs + output_costs

        # Format cost data
        new_cost_data = {
            "input_costs": round(input_costs, 6),
            "output_costs": round(output_costs, 6),
            "total_costs": round(total_costs, 6)
        }

        # Load existing cost data or initialize if file does not exist
        if os.path.exists(file_name):
            with open(file_name, "r", encoding="utf-8") as file:
                try:
                    existing_data = json.load(file)
                except json.JSONDecodeError:
                    existing_data = {}
        else:
            existing_data = {}

        # Check if cumulative cost entry exists
        existing_data.setdefault("cumulative_costs", 0)
        existing_data.setdefault(model, {"input_costs": 0, "output_costs": 0, "total_costs": 0})

        # Update per-model costs
        existing_data[model]["input_costs"] += new_cost_data["input_costs"]
        existing_data[model]["output_costs"] += new_cost_data["output_costs"]
        existing_data[model]["total_costs"] += new_cost_data["total_costs"]

        # Update cumulative total cost across all models
        existing_data["cumulative_costs"] += new_cost_data["total_costs"]

        # Save updated data to file
        with open(file_name, "w", encoding="utf-8") as file:
            json.dump(existing_data, file, indent=4)

        # Print formatted cost summary
        if verbose:
            return print(f"Call Cost: ${new_cost_data['total_costs']:.6f} | "
                  f"Model Total Cost ({model}): ${existing_data[model]['total_costs']:.6f} | "
                  f"Cumulative Cost: ${existing_data['cumulative_costs']:.6f}")

    except (IndexError, AttributeError, TypeError, KeyError) as e:
        print(f"Error: {e}")
        return None

