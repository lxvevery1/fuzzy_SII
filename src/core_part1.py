import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt
import json

# Load configuration from file
with open("config_1.json") as f:
    config = json.load(f)

# Define the input and output variables
input_var = ctrl.Antecedent(
    np.arange(0, config["input_max"] + 1, 1), config["input_name"]
)
output_var = ctrl.Consequent(
    np.arange(0, config["output_max"] + 1, 1), config["output_name"]
)

# Define fuzzy sets for input variable
for name, params in config["input_sets"].items():
    input_var[name] = fuzz.trimf(input_var.universe, params)

# Define fuzzy sets for output variable
for name, params in config["output_sets"].items():
    output_var[name] = fuzz.trimf(output_var.universe, params)

# Define the rules
rules = []
for rule in config["rules"]:
    antecedent = " & ".join([f"input_var['{name}']" for name in rule["antecedents"]])
    consequent = f"output_var['{rule['consequent']}']"
    rules.append(ctrl.Rule(eval(antecedent), eval(consequent)))

# Create the control system
control_system = ctrl.ControlSystem(rules)
evaluation = ctrl.ControlSystemSimulation(control_system)


# Function to evaluate skill based on input
def evaluate(input_value):
    evaluation.input[config["input_name"]] = input_value
    evaluation.compute()
    return evaluation.output[config["output_name"]]


# Example usage
input_consumed = 20
output_level = evaluate(input_consumed)
print(
    f"{config['output_name']} level for {input_consumed} {config['input_name']} consumed: {output_level:.2f}"
)

# Visualization
# Plot the input variable
plt.figure(figsize=(10, 6))

plt.subplot(2, 1, 1)
input_var.view()
plt.title(config["input_name"])

# Plot the output variable
plt.subplot(2, 1, 2)
output_var.view(sim=evaluation)
plt.title(config["output_name"])

plt.show()
