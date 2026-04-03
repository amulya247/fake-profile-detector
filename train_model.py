import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib

# Load data
data = pd.read_csv("data.csv")

X = data[["followers", "following", "posts", "bio_length"]]
y = data["fake"]

# Train model
model = RandomForestClassifier()
model.fit(X, y)

# Save model
joblib.dump(model, "model.pkl")

print("Model trained and saved!")