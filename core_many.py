import json

import matplotlib.pyplot as plt
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl


def load_config(file_path):
    with open(file_path) as f:
        return json.load(f)


def define_input_variables(config):
    input_vars = {}
    for input_name, params in config["inputs"].items():
        var = ctrl.Antecedent(np.arange(0, params["max"] + 1, 1), input_name)
        for set_name, set_params in params["sets"].items():
            var[set_name] = fuzz.trimf(var.universe, set_params)
        input_vars[input_name] = var
    return input_vars


def define_output_variable(config):
    output_name = config["output"]["name"]
    output_var = ctrl.Consequent(
        np.arange(0, config["output"]["max"] + 1, 1), output_name
    )
    for set_name, set_params in config["output"]["sets"].items():
        output_var[set_name] = fuzz.trimf(output_var.universe, set_params)
    return output_var


def define_rules(config, input_vars, output_var):
    rules = []
    for rule in config["rules"]:
        antecedents = {
            input_name: (input_vars[input_name], term)
            for input_name, term in rule["antecedents"].items()
        }
        consequent = (output_var, rule["consequent"])
        rules.append((antecedents, consequent))
    return rules


def evaluate(inputs, input_vars, rules, output_var):
    membership_values = {}
    for name, value in inputs.items():
        var = input_vars[name]
        membership_values[name] = {
            term: fuzz.interp_membership(var.universe, var[term].mf, value)
            for term in var.terms
        }

    firing_strengths = []
    rule_outputs = []
    for antecedents, consequent in rules:
        rule_strength = min(
            membership_values[name][term] for name, (var, term) in antecedents.items()
        )
        firing_strengths.append(rule_strength)
        rule_outputs.append((rule_strength, consequent))

    aggregated = np.zeros_like(output_var.universe)
    for strength, (var, term) in rule_outputs:
        aggregated = np.fmax(
            aggregated,
            np.fmin(strength, var[term].mf),
        )

    defuzzified = fuzz.defuzz(output_var.universe, aggregated, "centroid")
    return defuzzified, firing_strengths


def main():
    config = load_config("config_many.json")
    input_vars = define_input_variables(config)
    output_var = define_output_variable(config)
    rules = define_rules(config, input_vars, output_var)

    example_inputs = {name: val for name, val in config["example_inputs"].items()}
    output_value, rule_strengths = evaluate(
        example_inputs, input_vars, rules, output_var
    )

    print(f"Inputs: {example_inputs}")
    print(f"Output ({config['output']['name']}): {output_value:.2f}")
    print("Rule firing strengths:")
    for i, strength in enumerate(rule_strengths):
        print(f"  Rule {i + 1}: {strength:.2f}")

    plt.figure(figsize=(15, 8))

    for i, (name, var) in enumerate(input_vars.items(), start=1):
        plt.subplot(len(input_vars) + 1, 1, i)
        var.view()
        plt.title(name)

    plt.subplot(len(input_vars) + 1, 1, len(input_vars) + 1)
    output_var.view()
    plt.title(config["output"]["name"])

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
