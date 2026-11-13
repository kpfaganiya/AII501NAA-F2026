# AII501NAA – Activity 3: Linear Regression (Chicago Taxi Fares)

This folder contains my completed Activity 3 for AII501NAA. I worked through Google's Machine Learning Crash Course linear regression notebook, which trains a model to predict the fare of a Chicago taxi trip, and answered the activity questions.

## Contents

| File | Description |
|------|-------------|
| `linear_regression_taxi.ipynb` | Completed notebook with all cells run and outputs saved |
| `answers.md` | Answers to the 8 activity questions |
| `README.md` | Setup, execution, testing notes and assumptions |

## Setup

The notebook was developed and run in **Google Colab** (Python 3.13).

Library versions used (printed in the "Load dependencies" cell):

- Keras 3.13.2
- TensorFlow 2.21.0
- NumPy 2.4.6
- pandas 2.2.3
- matplotlib, plotly
- google-ml-edu 0.1.3

**Note on installation:** the original install cell gave a dependency error in Colab. I changed it to:

    !pip install --no-deps google-ml-edu==0.1.3

`--no-deps` stops pip from trying to reinstall or downgrade packages Colab already has (TensorFlow, Keras, pandas, etc.), and that fixed the error.

