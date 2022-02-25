import numpy as np

"""
A series of dictionaries and functions for generating example requests to PdfRenderer
"""

dp_release = {"name": "Test Experiment", "created": {"human_readable": "January 04, 2022 at 18:34:53:991957"}}


statistics = [{
    "result": {
        "value": 187
    },
    "epsilon": 1.0,
    "delta": 0.0,
    "accuracy": {
        "value": 8.987196833391316,
        "message": "There is a probability of 95.0% that the DP Count will differ from the true Count by at "
                   "most 8.987196833391316 units. Here the units are the same units the variable "
                   "BlinkFrequency has in the dataset."
    },
    "variable": "BlinkFrequency",
    "statistic": "count",
    "description": {
        "html": "A differentially private <b>Count</b> for variable <b>BlinkFrequency</b> was calculated with "
                "the result <b>187</b>.  There is a probability of <b>95.0%</b> that the <b>DP Count</b> will "
                "differ from the true Count by at most <b>8.987196833391316</b> units. Here the units are the "
                "same units the variable <b>BlinkFrequency</b>} has in the dataset.",
        "text": "A differentially private Count for variable \"BlinkFrequency\" was calculated with the result "
                "187. There is a probability of 95.0% that the DP Count will differ from the true Count by at "
                "most 8.987196833391316 units. Here the units are the same units the variable BlinkFrequency "
                "has in the dataset."
    },
    "confidence_level": 0.95,
    "confidence_level_alpha": 0.05,
    "missing_value_handling": {
        "type": "insert_fixed",
        "fixed_value": "4"
    }
}, {
    "result": {
        "value": 3.14
    },
    "epsilon": 1.0,
    "delta": 0.0,
    "accuracy": {
        "value": 2.71,
        "message": "There is a probability of 95.0% that the DP Mean will differ from the true Mean by at "
                   "most 2.71 units. Here the units are the same units the variable "
                   "EyeHeight has in the dataset."
    },
    "variable": "EyeHeight",
    "statistic": "Mean",
    "description": {
        "html": "A differentially private <b>Mean</b> for variable <b>EyeHeight</b> was calculated with "
                "the result <b>3.14</b>.  There is a probability of <b>95.0%</b> that the <b>DP Mean</b> will "
                "differ from the true Mean by at most <b>8.987196833391316</b> units. Here the units are the "
                "same units the variable <b>EyeHeight</b>} has in the dataset.",
        "text": "A differentially private Mean for variable \"EyeHeight\" was calculated with the result "
                "3.14. There is a probability of 95.0% that the DP Mean will differ from the true Mean by at "
                "most 8.987196833391316 units. Here the units are the same units the variable EyeHeight "
                "has in the dataset."
    },
    "confidence_level": 0.95,
    "confidence_level_alpha": 0.05,
    "missing_value_handling": {
        "type": "insert_fixed",
        "fixed_value": "4"
    }
}, {
    "result": {
        "value": [1, 2, 3, 4],
        "categories": ["a", "b", "c", "d"]
    },
    "epsilon": 1.0,
    "delta": 0.0,
    "accuracy": {
        "value": 8.987196833391316,
        "message": "There is a probability of 95.0% that the DP Histogram will differ from the true Histogram "
                   "by at most 8.987196833391316 units. Here the units are the same units the variable "
                   "EyeWidth has in the dataset."
    },
    "variable": "EyeWidth",
    "statistic": "histogram",
    "description": {
        "html": "A differentially private <b>Histogram</b> for variable <b>EyeWidth</b> was calculated with "
                "the result <b>[1,2,3,4]</b>.  There is a probability of <b>95.0%</b> that the <b>DP "
                "Histogram</b> will differ from the true Count by at most <b>8.987196833391316</b> units. Here "
                "the units are the same units the variable <b>EyeWidth</b>} has in the dataset.",
        "text": "A differentially private Histogram for variable \"EyeWidth\" was calculated with the result "
                "[1,2,3,4]. There is a probability of 95.0% that the DP Histogram will differ from the true "
                "Histogram by at most 8.987196833391316 units. Here the units are the same units the variable "
                "EyeWidth has in the dataset."
    },
    "confidence_level": 0.95,
    "confidence_level_alpha": 0.05,
    "missing_value_handling": {
        "type": "insert_fixed",
        "fixed_value": "4"
    }
}]

def generate_example_histogram(variable, data_size):
    import string
    heights = np.random.randint(low=5, high=10, size=data_size)
    categories = np.random.choice(list(string.ascii_letters), size=data_size)
    epsilon = np.random.random()
    delta = np.random.random()
    accuracy = 10 * np.random.random()
    return {
        "result": {
            "value": heights,
            "categories": categories
        },
        "epsilon": epsilon,
        "delta": delta,
        "accuracy": {
            "value": accuracy,
            "message": f"There is a probability of 95.0% that the DP Histogram will differ from the true Histogram "
                       f"by at most {accuracy} units. Here the units are the same units the variable "
                       f"{variable} has in the dataset."
        },
        "variable": variable,
        "statistic": "histogram",
        "description": {
            "html": "A differentially private <b>Histogram</b> for variable <b>EyeWidth</b> was calculated with "
                    f"the result <b>{heights}</b>.  There is a probability of <b>95.0%</b> that the <b>DP "
                    f"Histogram</b> will differ from the true Count by at most <b>{accuracy}</b> units. Here "
                    f"the units are the same units the variable <b>{variable}</b> has in the dataset.",
            "text": f"A differentially private Histogram for variable \"{variable}\" was calculated with the result "
                    f"{heights}. There is a probability of 95.0% that the DP Histogram will differ from the true "
                    f"Histogram by at most {accuracy} units. Here the units are the same units the variable "
                    f"EyeWidth has in the dataset."
        },
        "confidence_level": 0.95,
        "confidence_level_alpha": 0.05,
        "missing_value_handling": {
            "type": "insert_fixed",
            "fixed_value": "4"
        }
    }
