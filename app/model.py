import joblib


MODEL_PATH = "model/intent_classifier.joblib"
VECTORIZER_PATH = "model/tfidf_vectorizer.joblib"


model = joblib.load(MODEL_PATH)
vectorizer = joblib.load(VECTORIZER_PATH)


def predict_intent(text: str):

    features = vectorizer.transform([text])

    prediction = model.predict(features)[0]

    probabilities = model.predict_proba(features)[0]

    confidence = max(probabilities)

    return prediction, confidence