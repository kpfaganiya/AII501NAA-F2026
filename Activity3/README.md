# AII501NAA - Activity 3: Linear Regression (Chicago Taxi Fares)

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

To run it locally instead of in Colab:

    pip install tensorflow keras numpy pandas matplotlib plotly
    pip install --no-deps google-ml-edu==0.1.3
    jupyter notebook linear_regression_taxi.ipynb

## How to Run

1. Open `linear_regression_taxi.ipynb` in Google Colab (File → Upload notebook, or open it from GitHub).
2. Click **Runtime → Run all**.
3. The dataset downloads automatically from:
   `https://download.mlcc.google.com/mledu-datasets/chicago_taxi_train.csv`
   (31,694 rows; columns used: TRIP_MILES, TRIP_SECONDS, FARE, COMPANY, PAYMENT_TYPE, TIP_RATE)

   ## What the Notebook Does

1. **Dataset exploration**: summary statistics, a correlation matrix and a pair plot. TRIP_MILES has the strongest correlation with FARE (0.975).
2. **Experiment 1**: one feature (TRIP_MILES), learning rate 0.001, 20 epochs, batch size 50. Final RMSE ≈ $3.75.
3. **Hyperparameter experiments**:
   - Learning rate 1.0: loss bounced around (RMSE ≈ $7) and never settled, because the steps are too large.
   - Learning rate 0.0001: loss went down very slowly and had not converged after 20 epochs.
   - Batch size 500: each epoch ran faster, but there were fewer weight updates, so it did not converge in 20 epochs.
4. **Experiment 3**: two features (TRIP_MILES and TRIP_MINUTES). Final RMSE ≈ $3.48, better than one feature.
5. **Validation**: predictions on a random sample of 50 trips, compared with the actual fares using L1 loss.

## Testing / Validation

- Training was checked with the RMSE loss curves, to confirm the loss went down and levelled off (converged).
- The two models were compared side by side with `compare_experiment` (one feature vs. two features).
- Predictions on a random batch of 50 trips were checked by looking at the `L1_LOSS` (|observed - predicted|) column. Most errors were under about $1.50.
- The learned weights were compared with the known Chicago fare formula: `FARE = 2.25 × TRIP_MILES + 0.12 × TRIP_MINUTES + 3.25`.

## Assumptions and Limitations

- The tutorial trains and evaluates on the **same dataset** and has no separate test set, so the reported RMSE is likely somewhat optimistic. A real project should evaluate on held-out test data (discussed in answers.md, Q2).
- RMSE is reported as the error metric, because that is what the tutorial uses. The activity accepts MAE or MSE.
- I assume the dataset URL above stays online.
- Results can differ slightly between runs, because weight initialization and batch shuffling are random.
- The TensorFlow "tf.function retracing" warning in Experiments 2b and 2c is harmless. It appears because each experiment builds a new model and calls predict on it repeatedly. It does not affect the results.