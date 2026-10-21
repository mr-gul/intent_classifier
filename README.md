# Intent Classifier

Classifies customer-support messages into 9 intents (TF-IDF + Logistic Regression). This branch (`kserve`) adds a [KServe](https://kserve.github.io/website/) `InferenceService` manifest so the model can be served on Kubernetes.

The same model is also available as a standalone FastAPI app (`app/`), which is useful for local development and testing.

## Intents

`account_update` · `billing_issue` · `cancel_account` · `login_problem` · `order_tracking` · `password_reset` · `refund_request` · `subscription_information` · `support_request`

## Project structure

```text
app/                  FastAPI app: routes, request schema, prediction logic
model/                Trained artifacts: intent_classifier.joblib, tfidf_vectorizer.joblib
tests/                API tests (pytest)
train.py              Trains the model and writes the artifacts to model/
inference-svc.yaml    KServe InferenceService (sklearn runtime)
requirements.txt      Python dependencies (pinned)
```

## Run locally (FastAPI)

Requires Python 3.12.

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Interactive docs: http://127.0.0.1:8000/docs

| Method | Path       | Description                         |
|--------|------------|-------------------------------------|
| GET    | `/`        | Service info message                |
| GET    | `/health`  | Health check                        |
| POST   | `/predict` | Returns `intent` and `confidence`   |

```bash
curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "I forgot my password"}'
```

```json
{
  "text": "I forgot my password",
  "intent": "password_reset",
  "confidence": 0.9876
}
```

Run the tests with `python -m pytest`.

## Deploy with KServe

**Prerequisites:** a Kubernetes cluster with KServe installed, and `kubectl` pointing at it.

`inference-svc.yaml` defines an `InferenceService` named `intent-classifier`:

- **Runtime:** KServe `sklearn` model format
- **Model source:** `storageUri` points to the `model.pkl` asset on the [`v1.0.0` release](https://github.com/mr-gul/intent_classifier/releases/tag/v1.0.0)
- **Resources:** requests 100m CPU / 512Mi memory; limits 1 CPU / 1Gi memory

```bash
kubectl apply -f inference-svc.yaml
kubectl get inferenceservice intent-classifier      # wait until READY is True
```

Reach it locally with a port-forward (service name may vary by KServe version; check `kubectl get svc`):

```bash
kubectl port-forward svc/intent-classifier-predictor 8080:80
curl -X POST http://127.0.0.1:8080/v1/models/intent-classifier:predict \
  -H "Content-Type: application/json" \
  -d '{"instances": [...]}'
```

### Input format

The KServe `sklearn` runtime serves one pickled estimator and passes the request `instances` straight to `predict`. The classifier in this repo is a plain `LogisticRegression` and the `TfidfVectorizer` is a separate artifact, so raw text is **not** vectorized for you. Either:

- publish a single scikit-learn `Pipeline` (vectorizer + classifier) as `model.pkl`, so text goes in directly; or
- send pre-computed TF-IDF feature vectors as `instances`.

Check which one your `v1.0.0` `model.pkl` contains before relying on text input.

### Updating the model

1. Retrain and save artifacts (see below).
2. Publish the new `model.pkl` as a release asset.
3. Update `storageUri` in `inference-svc.yaml` and run `kubectl apply -f inference-svc.yaml`.

## Training

`train.py` reads `data/intent.csv` (columns `text`, `intent`), splits 70/30 with stratification, fits TF-IDF + Logistic Regression, prints accuracy and a classification report, and saves both artifacts to `model/`.

`train.py` currently uses hardcoded absolute paths (`/home/gulraiz/intent-classifier/...`). Change them to paths on your machine before running it, and make sure `data/intent.csv` exists (it is not on this branch).

## Related branches

| Branch            | Deployment                                              |
|-------------------|---------------------------------------------------------|
| `master`          | Docker image, Kubernetes manifests, GitHub Actions CI/CD |
| `virtual_machine` | EC2 Auto Scaling Group behind an Application Load Balancer |
| `kserve`          | KServe InferenceService                                 |
