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

The tutorial uses **RMSE (Root Mean Squared Error)**: the square root of the average of the squared differences between predicted and actual fares. It is in the same units as the label (dollars). Because errors are squared before averaging, big mistakes count more than small ones. MAE (Mean Absolute Error) is similar but just averages the absolute errors.

My results:
- One feature (TRIP_MILES): **RMSE ≈ $3.75**
- Two features (TRIP_MILES + TRIP_MINUTES): **RMSE ≈ $3.48**

In plain words: **on average, my best model's predictions are off by about $3.50.** In the 50-trip prediction sample, most of the individual errors (`L1_LOSS`) were under $1. The RMSE is pulled up by a few trips with big errors.

## 4. Predicted vs. actual: where does the model do well and where does it struggle?

**Does well:** short and medium trips (roughly under 20 miles). Most points sit close to the model's line/plane, and in the prediction sample many errors were only a few cents. For example, a 15-mile trip was predicted at $39.78 vs. an actual $39.75.

**Struggles:**
- **Long trips (20+ miles).** Fares are more spread out, probably because of airport flat rates, tolls and traffic. The worst case in my sample was a 27.7-mile, 91-minute trip predicted at **$73.16** when the actual fare was **$120.00**, an error of $46.84.
- **Very short trips.** There's a minimum fare, so some short trips cost more than the line predicts. For example, a 0.67-mile trip was predicted at $5.71 vs. an actual $9.00.

A straight line can't capture these special cases.

## 5. Changing one setting

I changed the **learning rate** from 0.001 to **1.0** (same features, 20 epochs, batch size 50).

- With 0.001, RMSE dropped from about $29 at epoch 1 to about $4.21 by epoch 5, and ended at **$3.75**.
- With 1.0, RMSE stayed around **$6.85–$6.96** the whole time and jumped up and down instead of decreasing.

Why: the learning rate controls how big a step the optimizer takes when it updates the weights. At 1.0 the steps are too big, so the model keeps overshooting the best weights and never settles (it doesn't converge).

I also tried a learning rate of 0.0001: RMSE was still about $19.50 after 20 epochs, because the steps are so small it learns too slowly. With a batch size of 500, it was still about $26.28 after 20 epochs, because there are 10× fewer weight updates per epoch. Both would need more epochs to converge.

## 6. Most important feature

**TRIP_MILES** is the most important feature. I decided based on:
1. **The correlation matrix:** TRIP_MILES has a correlation of **0.975** with FARE, the highest of any feature. TRIP_SECONDS is 0.830, and TIP_RATE is only −0.071.
2. **The experiments:** using TRIP_MILES alone already gave RMSE ≈ $3.75. Adding TRIP_MINUTES only improved it to about $3.48, so most of the predictive power comes from distance.

This also makes sense in real life, because taxis mainly charge by distance. The real Chicago formula is roughly `2.25 × miles + 0.12 × minutes + 3.25`.

## 7. Classification vs. regression, with examples from my life

**Regression** predicts a **continuous number**. **Classification** predicts a **category/label** from a fixed set of options.

- **Regression example:** *(replace with your own)* Predicting how long my commute to Seneca will take in minutes, based on the time I leave and the weather.
- **Classification example:** *(replace with your own)* My email deciding whether a message is **spam or not spam**.

## 8. What could go wrong if this model were deployed?

- **Bad data:** errors in the data, like GPS mistakes giving wrong mileage, trips recorded as 0 seconds, or typos in the fare, would teach the model wrong patterns or give wrong predictions.
- **New situations it hasn't seen:** the model learned from one Chicago dataset. Fare price changes, new surcharges, holidays, snowstorms, big events or a different city would make predictions wrong. It also already struggles with long and airport trips (my $120 trip predicted at $73).
- **Bias:** if some areas or kinds of trips (for example, certain neighbourhoods or late-night trips) are under-represented in the data, the model will be less accurate for them. Those riders or drivers could be quoted unfair prices.
- **Too simple:** a linear model can't handle flat rates, minimum fares or tolls, so some errors will always be large.
- **No real test set:** I evaluated on the training data, so real-world accuracy is probably a bit worse than my RMSE suggests.

To reduce these risks, I'd test on held-out and recent data, monitor errors after deployment, retrain when fares change, and add features like pickup/drop-off location or time of day.