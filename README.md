# Intent Classifier API

A FastAPI service that classifies user text into intents using a pre-trained scikit-learn model.

## Features

- REST API for intent prediction (`POST /predict`)
- Health and root endpoints (`/health`, `/`)
- Pre-trained model + TF-IDF vectorizer loaded from `model/`
- Containerized runtime via Docker
- Kubernetes manifests for deployment (`k8s/`)
- CI/CD workflow for tests, image publish, and optional Kubernetes deploy

## Project Structure

```text
app/                # FastAPI app, schema, and prediction logic
model/              # Serialized model artifacts (.joblib)
tests/              # API tests (pytest)
k8s/                # Kubernetes Deployment and Service manifests
Dockerfile          # Container build/runtime definition
requirements.txt    # Python dependencies
.github/workflows/ci-cd.yml
```

## Prerequisites

- Python 3.12
- pip
- (Optional) Docker
- (Optional) kubectl + Kubernetes cluster

## Run Locally

From the repository root:

```bash
python -m venv .venv && source .venv/bin/activate && python -m pip install --upgrade pip && python -m pip install -r requirements.txt && uvicorn app.main:app --host 0.0.0.0 --port 8000
```

API will be available at `http://127.0.0.1:8000`.

## Run Tests

```bash
python -m pytest
```

## API Endpoints

| Method | Path       | Description |
|---|---|---|
| GET | `/` | Service info message |
| GET | `/health` | Health check |
| POST | `/predict` | Predict intent from input text |

### Example Request

```bash
curl -X POST "http://127.0.0.1:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"text":"I forgot my password"}'
```

Example response shape:

```json
{
  "text": "I forgot my password",
  "intent": "password_reset",
  "confidence": 0.9876
}
```

## Configuration / Environment Variables

The application code currently does not require runtime environment variables for startup.

CI/CD workflow variables (from `.github/workflows/ci-cd.yml`):

- `PYTHON_VERSION`
- `IMAGE_NAME`
- `IMAGE_TAG` (smoke test step)
- `IMAGE` (deploy step)
- `ENABLE_DEPLOY` repository variable gates the deploy job

## Docker

Build and run:

```bash
docker build -t intent-classifier:local .
docker run --rm -p 8000:8000 intent-classifier:local
```

## Kubernetes

Manifests are provided in `k8s/` for:

- `Deployment` (`k8s/deployment.yaml`)
- `Service` (`k8s/service.yaml`)

Apply them:

```bash
kubectl apply -f k8s/
```

To update the deployment image (pattern used in CI):

```bash
kubectl -n default set image deployment/intent-classifier intent-classifier=<your-image>
kubectl -n default rollout status deployment/intent-classifier --timeout=180s
```

## GitHub Actions Workflow

`.github/workflows/ci-cd.yml` defines:

1. **test**: installs dependencies and runs `python -m pytest`
2. **image**: builds and pushes image to GHCR, then smoke-tests `/health`
3. **deploy**: deploys to Kubernetes when deploy conditions are met
