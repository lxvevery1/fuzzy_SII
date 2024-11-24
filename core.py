import json

import matplotlib.pyplot as plt
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

with open("config_1.json") as f:
    config = json.load(f)

input_var = ctrl.Antecedent(
    np.arange(0, config["input_max"] + 1, 1), config["input_name"]
)
output_var = ctrl.Consequent(
    np.arange(0, config["output_max"] + 1, 1), config["output_name"]
)

for name, params in config["input_sets"].items():
    input_var[name] = fuzz.trimf(input_var.universe, params)

for name, params in config["output_sets"].items():
    output_var[name] = fuzz.trimf(output_var.universe, params)

rules = []
for rule in config["rules"]:
    antecedent = " & ".join([f"input_var['{name}']" for name in rule["antecedents"]])
    consequent = f"output_var['{rule['consequent']}']"
    rules.append(ctrl.Rule(eval(antecedent), eval(consequent)))

control_system = ctrl.ControlSystem(rules)
evaluation = ctrl.ControlSystemSimulation(control_system)


def evaluate(input_value):
    evaluation.input[config["input_name"]] = input_value
    evaluation.compute()
    return evaluation.output[config["output_name"]]


input_consumed = 20
output_level = evaluate(input_consumed)
print(
    f"{config['output_name']} level for {input_consumed} {config['input_name']} consumed: {output_level:.2f}"
)

output_var.defuzzify_method = "centroid"  # Centroid (default)
evaluation.compute()
print(f"Defuzzified value: {evaluation.output[config['output_name']]}")

plt.figure(figsize=(10, 6))

plt.subplot(2, 1, 1)
input_var.view()
plt.title(config["input_name"])

plt.subplot(2, 1, 2)
output_var.view(sim=evaluation)
plt.title(config["output_name"])

plt.show()
