import argparse
import json
import os
import random


def get_panelists(n):
    res = {}
    for i in map(str, range(n)):
        if random.random() < 0.5:
            sex = 'm'
        else:
            sex = 'k'
        age = random.randint(0, 74)

        age_range = age // 5 * 5
        age_value = '{}-{}'.format(age_range, age_range + 4)

        res[i] = {
            "demo": {
                "sex": sex,
                "age": age_value
            },
            "metric": abs(int(100 * random.paretovariate(1.5)))
        }
    return res


POLISH_POPULATION = {
    "age": {
        "15-19": 2266634,
        "20-24": 2736154,
        "25-29": 3198618,
        "30-34": 3161358,
        "35-39": 2903573,
        "40-44": 2440834,
        "45-49": 2389500,
        "50-54": 2784254,
        "55-59": 2926281,
        "60-64": 2514619,
        "65-69": 1537157,
        "70-74": 1306461
    },
    "sex": {
        "k": 15345479,
        "m": 14819964
    },
    "total": 30165443
}


def run(population_file, panelists_file, number_of_panelists):
    panelists = get_panelists(number_of_panelists)

    os.makedirs(os.path.dirname(panelists_file), exist_ok=True)
    with open(panelists_file, 'w') as f:
        json.dump(panelists, f, indent=4, sort_keys=True)

    os.makedirs(os.path.dirname(population_file), exist_ok=True)
    with open(population_file, 'w') as f:
        json.dump(POLISH_POPULATION, f, indent=4, sort_keys=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-panelists")
    parser.add_argument("--number-of-panelists", type=int, default=1000)
    parser.add_argument("--output-population")
    args = parser.parse_args()

    run(
        population_file=args.output_population,
        number_of_panelists=args.number_of_panelists,
        panelists_file=args.output_panelists
    )
