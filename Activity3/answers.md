# Activity 3 - Answers

All numbers below come from my runs in `linear_regression_taxi.ipynb`.

## 1. Target variable, input features, and why this is regression

The **target variable (label)** is `FARE`, the cost of the taxi trip in dollars.
The **input features** I used were `TRIP_MILES` (Experiment 1) and `TRIP_MILES` + `TRIP_MINUTES` (Experiment 3). `TRIP_MINUTES` is calculated from `TRIP_SECONDS / 60`.

This is a **regression** problem because the model predicts a continuous number, for example $27.63, and not a category. A classification problem would predict a label from a fixed set, such as "cash vs. credit card" or "expensive vs. cheap trip".

# 2. Why split into training and test sets?

We split the data so we can check how the model does on data it has **never seen**, which is what happens when it's used in real life. The training set is used to learn the weights, and the test set is used only to measure performance.

If we test on the training data, the score is too optimistic. The model has already seen those exact examples, so a model that memorized the data (overfitting) would look great but fail on new trips. We wouldn't find out until it was deployed.

Note: this tutorial trains and predicts on the same dataset (it says so in Part 4). That means my RMSE is probably a bit better than what I'd get on truly new data.

## 3. What does the error metric measure? My model's value