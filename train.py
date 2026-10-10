import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report

import joblib


# 1. Load dataset
df = pd.read_csv("//home//gulraiz//intent-classifier//data//intent.csv")

print("Dataset:")
print(df.head())
print(f"\nNumber of examples: {len(df)}")
print(f"Number of intents: {df['intent'].nunique()}")


# 2. Split features and labels
X = df["text"]
y = df["intent"]


# 3. Split into training and testing data
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.3,
    random_state=42,
    stratify=y
)


# 4. Convert text into numerical features
vectorizer = TfidfVectorizer()

X_train_vectorized = vectorizer.fit_transform(X_train)
X_test_vectorized = vectorizer.transform(X_test)


# 5. Train classifier
model = LogisticRegression(
    max_iter=1000
)

model.fit(X_train_vectorized, y_train)


# 6. Make predictions
predictions = model.predict(X_test_vectorized)


# 7. Evaluate model
accuracy = accuracy_score(y_test, predictions)

print(f"\nAccuracy: {accuracy:.2f}")

print("\nClassification Report:")
print(classification_report(y_test, predictions))


# 8. Save model and vectorizer
joblib.dump(model, "//home//gulraiz/intent-classifier//model//intent_classifier.joblib")
joblib.dump(vectorizer, "//home//gulraiz/intent-classifier//model//tfidf_vectorizer.joblib")

print("\nModel saved successfully.")