import pandas as pd

ground_truth = pd.read_csv("data/ground_truth.csv")

indices = ground_truth["index"].tolist()
time_periods = ["_".join(x.split("_")[:2]) for x in indices ]
ground_truth["time_period"] = time_periods
print(ground_truth.head())
ground_truth.to_csv("data/ground_truth_corrected.csv")
print("Correction done")
