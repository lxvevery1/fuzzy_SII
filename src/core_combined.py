import json
import os
import sys

import numpy as np

# Import script with plots drawings
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from plt.plotting import plot_implication_methods, plot_input_sets, plot_output_sets

f = open("config_combined.json")
config = json.load(f)

input_universe = np.arange(0, config["input_max"] + 1, 1)
output_universe = np.arange(0, config["output_max"] + 1, 1)


def create_fuzzy_sets(universe, sets_config):
    fuzzy_sets = {}
    for name, params in sets_config.items():
        fuzzy_sets[name] = np.array(
            [
                max(
                    0,
                    min(
                        1,
                        (
                            (x - params[0]) / (params[1] - params[0])
                            if params[1] > params[0] and x < params[1]
                            else (
                                (params[2] - x) / (params[2] - params[1])
                                if params[2] > params[1]
                                else 0
                            )
                        ),
                    ),
                )
                for x in universe
            ]
        )
    return fuzzy_sets


example_input_value = config["example_inputs"]["apples_eaten"]
input_sets = create_fuzzy_sets(input_universe, config["input_sets"])
output_sets = create_fuzzy_sets(output_universe, config["output_sets"])


def mandani_implication(truth_value, output_set):
    return np.minimum(truth_value, output_set)


def larsen_implication(truth_value, output_set):
    return np.minimum(1, np.maximum(0, truth_value + output_set - 1))


def premise_truth_implication(truth_value, output_set):
    return truth_value * output_set


def evaluate(input_value, method):
    input_truths = {name: input_sets[name][int(input_value)] for name in input_sets}

    aggregated_output = np.zeros_like(output_universe)
    for rule in config["rules"]:
        antecedent_truth = min(input_truths[cond] for cond in rule["antecedents"])
        consequent_set = output_sets[rule["consequent"]]

        if method == "mamdani":
            implication_result = mandani_implication(antecedent_truth, consequent_set)
        elif method == "larsen":
            implication_result = larsen_implication(antecedent_truth, consequent_set)
        elif method == "premise_truth":
            implication_result = premise_truth_implication(
                antecedent_truth, consequent_set
            )
        else:
            raise ValueError(f"Неизвестный метод: {method}")

        aggregated_output = np.maximum(aggregated_output, implication_result)

    if np.sum(aggregated_output) > 0:
        result = np.sum(aggregated_output * output_universe) / np.sum(aggregated_output)
    else:
        result = 0

    return result, aggregated_output


input_values = np.linspace(0, config["input_max"], 100)
example_input_value = config["example_inputs"]["apples_eaten"]

results_mamdani = [evaluate(i, "mamdani") for i in input_values]
results_larsen = [evaluate(i, "larsen") for i in input_values]

larsen_result, _ = evaluate(example_input_value, "larsen")
results_premise_truth = [evaluate(i, "premise_truth") for i in input_values]

mamdani_result, _ = evaluate(example_input_value, "mamdani")
larsen_result, _ = evaluate(example_input_value, "larsen")
premise_truth_result, _ = evaluate(example_input_value, "premise_truth")

print(f"Скилл игрока при съеденных {example_input_value} яблоках:")
print(f"  Метод Мандани: {mamdani_result:.2f}")
print(f"  Метод Ларсена: {larsen_result:.2f}")
print(f"  Метод истинности предпосылки: {premise_truth_result:.2f}")

output_values_mamdani = [res[0] for res in results_mamdani]
output_values_larsen = [res[0] for res in results_larsen]
output_values_premise_truth = [res[0] for res in results_premise_truth]

# Plot part!
plot_input_sets(input_universe, input_sets, config)
plot_output_sets(output_universe, output_sets, config)
plot_implication_methods(
    input_values,
    output_values_mamdani,
    output_values_larsen,
    output_values_premise_truth,
    example_input_value,
    mamdani_result,
    larsen_result,
    premise_truth_result,
    config,
)
