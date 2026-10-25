# NetPulse: Network Performance and Packet-Loss Prediction

NetPulse is a machine-learning-powered network analytics project that predicts the number of dropped packets in a router-buffer simulation. The project combines a TensorFlow regression model, a FastAPI backend, a browser-based dashboard, and an AnyLogic discrete-event simulation model.

> **Important:** Although the repository was originally described as containing Random Forest, XGBoost, CNN, and LSTM models, the currently implemented training and serving pipeline uses a TensorFlow fully connected neural network with engineered time-series features. The current application predicts packet loss; it is not yet a conventional multi-class network-intrusion classifier.

## Table of Contents

- [Project Overview](#project-overview)
- [Objectives](#objectives)
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [How the Prediction Pipeline Works](#how-the-prediction-pipeline-works)
- [Repository Structure](#repository-structure)
- [Technology Stack](#technology-stack)
- [Requirements](#requirements)
- [Installation](#installation)
- [Running the Project](#running-the-project)
- [Training the Model](#training-the-model)
- [Using the Web Dashboard](#using-the-web-dashboard)
- [API Documentation](#api-documentation)
- [Input Features](#input-features)
- [AnyLogic Router Simulation](#anylogic-router-simulation)
- [Jupyter Notebook](#jupyter-notebook)
- [Model Details](#model-details)
- [Evaluation](#evaluation)
- [Example API Request](#example-api-request)
- [Troubleshooting](#troubleshooting)
- [Limitations and Future Improvements](#limitations-and-future-improvements)
- [Security Notes](#security-notes)
- [License](#license)

## Project Overview

Network traffic can overload router buffers, causing packets to be discarded when incoming traffic exceeds available capacity. NetPulse attempts to estimate packet loss from historical observations and temporal context before or during a simulation run.

The project contains four main components:

1. **Data and feature-processing pipeline** – Loads CSV files, cleans timestamps and target values, and generates temporal and lag-based features.
2. **Machine-learning model** – A TensorFlow neural network trained to predict dropped packets.
3. **FastAPI inference service** – Loads the trained model and scaler and exposes a `/predict` endpoint.
4. **Web and simulation interfaces** – A responsive dashboard for manual predictions and an AnyLogic router-buffer model for packet-flow simulation.

## Objectives

- Predict packet loss from recent network measurements.
- Capture time-dependent behavior using hour, weekday, lag, and rolling-average features.
- Provide a simple HTTP API for real-time inference.
- Offer a browser interface for users who do not want to call the API directly.
- Simulate router-buffer behavior using AnyLogic.
- Provide a foundation for future intrusion-detection and network-capacity experiments.

## Key Features

- TensorFlow/Keras regression model for dropped-packet prediction.
- Standardized input features using `StandardScaler`.
- Automatic model and scaler loading when the FastAPI application starts.
- REST API built with FastAPI and Pydantic validation.
- Interactive frontend built with HTML, CSS, and JavaScript.
- CORS enabled for frontend-to-backend communication.
- AnyLogic router-buffer simulation with configurable traffic rate and buffer capacity.
- Training notebook with evaluation output and actual-versus-predicted visualizations.
- Saved model artifacts in the `models/` directory.

## System Architecture

```text
+------------------+       +----------------------+       +---------------------+
| CSV / Simulation | ----> | Data preprocessing   | ----> | Feature engineering |
| measurements     |       | and cleaning         |       | and scaling         |
+------------------+       +----------------------+       +---------------------+
                                                               |
                                                               v
                                                   +---------------------+
                                                   | TensorFlow model    |
                                                   | packet_loss_model   |
                                                   +---------------------+
                                                               |
                                                               v
+------------------+       HTTP POST /predict      +---------------------+
| NetPulse web UI  | <--------------------------> | FastAPI inference   |
| index.html       |                              | service: app.py     |
+------------------+                              +---------------------+

+---------------------+
| AnyLogic simulation |
| RouterBufferModel   |
+---------------------+
```

## How the Prediction Pipeline Works

### 1. Data loading

`train_model.py` recursively searches a directory for CSV files. For each file, it attempts to identify:

- A timestamp column containing `time` or `#` in its name.
- A target column containing `bits`, `traffic`, or `dropped` in its name.
- If no matching target column is found, the second CSV column is used as a fallback.

Rows with invalid timestamps or non-numeric target values are removed. The resulting dataframes are combined, sorted by timestamp, and deduplicated.

### 2. Feature engineering

The training pipeline creates six model features:

- `hour`
- `day_of_week`
- `is_weekend`
- `lag_1`
- `lag_2`
- `rolling_3`

The first two lagged rows and any rows without a complete rolling average are removed before training.

### 3. Scaling

A scikit-learn `StandardScaler` is fitted on the training features. The scaler is saved as `models/scaler.pkl` and must be used for every prediction so that API inputs have the same scale as the training data.

### 4. Model training

The current model is a dense neural network with:

- Input layer for six features.
- Dense layer with 512 ReLU units.
- Batch normalization.
- Dropout with a rate of `0.2`.
- Dense layer with 256 ReLU units.
- Batch normalization.
- Dense layer with 128 ReLU units.
- Linear output layer for one continuous prediction.

The model uses the Adam optimizer, mean squared error loss, and mean absolute error as a training metric.

### 5. Inference

The FastAPI service:

1. Receives the six input features as JSON.
2. Builds a one-row pandas dataframe.
3. Applies the saved scaler.
4. Generates a prediction using the saved Keras model.
5. Clips negative predictions to zero.
6. Returns the predicted number of dropped packets.

## Repository Structure

```text
Network-intrusion-detection-project/
├── README.md                         # Project documentation
├── app.py                            # FastAPI backend and prediction endpoint
├── train_model.py                    # Data preparation and model training script
├── ce313_project.ipynb               # Exploratory training and evaluation notebook
├── data.csv                          # Router traffic/buffer/drop sample data
├── RouterBufferModel.alp             # AnyLogic router-buffer simulation model
├── index.html                        # NetPulse frontend page
├── script.js                         # Frontend form submission and API calls
├── style.css                         # Frontend styling and responsive layout
├── instructions.txt                  # Original quick-start instructions
├── plot_1.png                        # Saved visualization asset
├── CE313_project_review_paper.pdf    # Project review paper
└── models/
    ├── packet_loss_model.keras       # Saved TensorFlow/Keras model
    ├── packet_loss_model.pkl         # Additional serialized model artifact
    └── scaler.pkl                    # Saved StandardScaler
```

> The training script expects a `dataset/` directory containing raw CSV files. If you want to retrain the model locally, create that directory and place the source CSV files inside it, or update the path in `train_model.py`.

## Technology Stack

### Backend and machine learning

- Python
- FastAPI
- Uvicorn
- Pydantic
- pandas
- NumPy
- scikit-learn
- TensorFlow/Keras
- pickle for scaler serialization

### Frontend

- HTML5
- CSS3
- Vanilla JavaScript
- Google Fonts: Outfit and Playfair Display

### Simulation and analysis

- AnyLogic 8.9.x project format
- Jupyter Notebook
- Matplotlib

## Requirements

Recommended software:

- Python 3.10 or newer
- pip
- AnyLogic 8.9.x if you want to open or run the simulation model
- A modern web browser

Install the Python dependencies:

```bash
pip install fastapi uvicorn pandas numpy scikit-learn tensorflow pydantic matplotlib
```

For reproducible environments, it is recommended to use a virtual environment:

```bash
python -m venv .venv
```

Activate it on macOS/Linux:

```bash
source .venv/bin/activate
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Then install the dependencies inside the environment:

```bash
pip install fastapi uvicorn pandas numpy scikit-learn tensorflow pydantic matplotlib
```

## Installation

Clone the repository and enter the project directory:

```bash
git clone https://github.com/abdulwasay4585/Network-intrusion-detection-project.git
cd Network-intrusion-detection-project
```

If the trained files already exist in `models/`, you can start the API immediately. Otherwise, follow the training steps below.

## Running the Project

### Option 1: Start with the existing model

From the repository root, run:

```bash
python app.py
```

The server listens on:

```text
http://localhost:8000
```

Open the dashboard in a browser:

```text
http://localhost:8000
```

FastAPI's automatically generated API documentation is available at:

```text
http://localhost:8000/docs
```

An alternative ReDoc interface is available at:

```text
http://localhost:8000/redoc
```

### Option 2: Start with Uvicorn

You can also start the application using Uvicorn directly:

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

The `--reload` option is useful during development because the server restarts when Python source files change.

## Training the Model

The training script saves a Keras model and scaler in `models/`.

### Expected training-data layout

```text
dataset/
├── measurements_1.csv
├── measurements_2.csv
└── ...
```

Each CSV should contain a timestamp-like column and a numeric target column. The loader uses column-name heuristics, so names containing terms such as `time`, `traffic`, `bits`, or `dropped` are easiest to process.

### Run training

```bash
python train_model.py
```

The script performs the following operations:

1. Finds CSV files under `dataset/`.
2. Reads and cleans the files.
3. Creates temporal and lag features.
4. Splits the data into training and testing sets using an 80/20 split.
5. Standardizes the input features.
6. Trains the neural network for up to 200 epochs.
7. Uses early stopping and learning-rate reduction.
8. Saves the model to `models/packet_loss_model.keras`.
9. Saves the scaler to `models/scaler.pkl`.

The script prints an R² score after evaluating the test set.

## Using the Web Dashboard

The dashboard is served by FastAPI and is implemented in `index.html`, `style.css`, and `script.js`.

To make a prediction:

1. Start the backend with `python app.py`.
2. Open `http://localhost:8000`.
3. Enter values for all six features.
4. Select **Analyze Performance**.
5. The page sends a JSON request to `/predict`.
6. The predicted dropped-packet value appears on the page.

The interface includes client-side validation for the hour, day of week, and weekend indicator. It also displays a loading animation while the API request is running.

## API Documentation

### `POST /predict`

Generates a dropped-packet prediction.

#### Request body

```json
{
  "hour": 14,
  "day_of_week": 2,
  "is_weekend": 0,
  "lag_1": 150.5,
  "lag_2": 148.2,
  "rolling_3": 149.8
}
```

#### Successful response

```json
{
  "predicted_dropped_packets": 151.37
}
```

The returned value is converted to a floating-point number and constrained to be non-negative.

#### Possible errors

- `503 Service Unavailable` – The model or scaler could not be loaded.
- `500 Internal Server Error` – An unexpected preprocessing or inference error occurred.
- `422 Unprocessable Entity` – The request body does not satisfy the Pydantic schema.

### Static routes

The backend also serves the frontend assets through:

- `GET /` – Returns `index.html`.
- `GET /style.css` – Returns the stylesheet.
- `GET /script.js` – Returns the frontend JavaScript.

## Input Features

| Feature | Type | Meaning | Typical value or range |
|---|---:|---|---|
| `hour` | Integer | Hour of the day | `0`–`23` |
| `day_of_week` | Integer | Day index, where Monday is `0` and Sunday is `6` | `0`–`6` |
| `is_weekend` | Integer | Weekend indicator | `0` for weekday, `1` for weekend |
| `lag_1` | Float | Target value from the previous time step | Depends on dataset |
| `lag_2` | Float | Target value from two time steps earlier | Depends on dataset |
| `rolling_3` | Float | Average of the previous three target values | Depends on dataset |

The input order is important during preprocessing. The API constructs the dataframe in the same feature order used during training:

```text
hour, day_of_week, is_weekend, lag_1, lag_2, rolling_3
```

## AnyLogic Router Simulation

`RouterBufferModel.alp` is an AnyLogic model representing packet flow through a router buffer.

The main process contains:

```text
Source → SelectOutput → Router Buffer Queue → Delay → Success Sink
                     └────────────────────→ Dropped_Packets Sink
```

### Simulation logic

- The **Source** generates packet entities using the configured traffic rate.
- **SelectOutput** checks whether the router buffer has available capacity.
- Packets are admitted when `routerBuffer.size() < buffer_capacity`.
- Accepted packets enter the **routerBuffer** queue.
- Accepted packets pass through a 10-millisecond **delay**.
- Successfully processed packets reach the **Success** sink.
- Packets that cannot enter the full buffer are routed to **Dropped_Packets**.

### Main simulation parameters

| Parameter | Default | Description |
|---|---:|---|
| `traffic_rate` | `100` | Packet arrival rate per second |
| `buffer_capacity` | `50` | Maximum number of packets in the router buffer |

To open the simulation:

1. Install AnyLogic 8.9.x or a compatible version.
2. Open `RouterBufferModel.alp`.
3. Select the `Simulation` experiment.
4. Adjust `traffic_rate` and `buffer_capacity`.
5. Run the experiment and inspect successful and dropped packets.

The simulation model is currently stored as an AnyLogic project file. A direct Py4J integration layer is not visible in the current repository files; such an integration would need to be added or documented separately if required.

## Jupyter Notebook

`ce313_project.ipynb` documents the experimental workflow used for model development. It includes:

- Python package installation.
- Dataset extraction.
- CSV discovery and preprocessing.
- Feature engineering.
- Neural-network training.
- R² evaluation.
- Actual-versus-predicted scatter plots.
- Residual analysis.

To open it locally:

```bash
jupyter notebook ce313_project.ipynb
```

Or use JupyterLab:

```bash
jupyter lab ce313_project.ipynb
```

The notebook also contains a recorded training result of approximately **99.84% R²** for the dataset and split used in that experiment. This value should be treated as an experiment-specific result rather than a guaranteed performance level for new data.

## Model Details

### Training configuration

- Test split: `20%`
- Random state: `42`
- Optimizer: Adam
- Loss: Mean squared error (MSE)
- Metric: Mean absolute error (MAE)
- Maximum epochs: `200`
- Batch size: `64`
- Early stopping patience: `20`
- Learning-rate reduction patience: `7`
- Learning-rate reduction factor: `0.5`

### Saved artifacts

- `models/packet_loss_model.keras` – Main TensorFlow/Keras model loaded by `app.py`.
- `models/scaler.pkl` – Feature scaler required before inference.
- `models/packet_loss_model.pkl` – Additional serialized model artifact present in the repository; the current FastAPI application loads the `.keras` model instead.

## Evaluation

The training script imports support for the following regression metrics:

- Mean squared error (MSE)
- Mean absolute error (MAE)
- R² score

The current script prints the R² score after evaluating the test set. For a more complete experiment, report all metrics and evaluate on a time-ordered holdout set rather than relying only on a random split.

## Example API Request

Using `curl`:

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "hour": 14,
    "day_of_week": 2,
    "is_weekend": 0,
    "lag_1": 150.5,
    "lag_2": 148.2,
    "rolling_3": 149.8
  }'
```

Using Python:

```python
import requests

payload = {
    "hour": 14,
    "day_of_week": 2,
    "is_weekend": 0,
    "lag_1": 150.5,
    "lag_2": 148.2,
    "rolling_3": 149.8,
}

response = requests.post("http://localhost:8000/predict", json=payload)
response.raise_for_status()
print(response.json())
```

## Troubleshooting

### `Model or Scaler not found`

Confirm that the following files exist:

```text
models/packet_loss_model.keras
models/scaler.pkl
```

If they do not exist, create the expected `dataset/` directory and run:

```bash
python train_model.py
```

### `No valid data could be extracted from CSVs`

Check that:

- The `dataset/` directory exists.
- It contains `.csv` files.
- The files contain a timestamp-like column.
- The files contain a numeric target-like column.
- The CSV files are not empty or malformed.

### Frontend cannot reach the backend

Make sure the API is running at `http://localhost:8000`. The frontend currently uses this fixed URL in `script.js`:

```text
http://localhost:8000/predict
```

If the backend is hosted elsewhere, update `API_URL` in `script.js` and configure CORS appropriately.

### TensorFlow installation problems

TensorFlow installation can depend on the operating system, Python version, CPU/GPU support, and available system libraries. If installation fails, consult the TensorFlow installation instructions for your platform and use a compatible Python environment.

### Port 8000 is already in use

Start the service on another port:

```bash
uvicorn app:app --host 0.0.0.0 --port 8001
```

If you change the port, update the frontend API URL in `script.js` as well.

## Limitations and Future Improvements

The current repository is a working prototype. Potential improvements include:

1. **Use a time-aware validation strategy** – Random train/test splitting can allow temporal leakage when lag features are used. A chronological split or walk-forward validation would better reflect production performance.
2. **Add dependency pinning** – Create a `requirements.txt` or `pyproject.toml` with tested versions.
3. **Add automated tests** – Test preprocessing, feature ordering, API validation, and model loading.
4. **Improve model monitoring** – Log predictions, latency, input distributions, and drift indicators.
5. **Add a health endpoint** – Expose model readiness and version information through `/health`.
6. **Make the frontend API URL configurable** – Avoid hard-coding `http://localhost:8000`.
7. **Strengthen CORS configuration** – Replace the wildcard origin with the specific frontend origin in production.
8. **Add intrusion-detection classification** – Implement labeled attack categories and classification metrics such as precision, recall, F1 score, ROC-AUC, and a confusion matrix.
9. **Integrate AnyLogic and Python explicitly** – Add a documented Py4J or REST bridge if predictions should influence the simulation dynamically.
10. **Add reproducible experiment configuration** – Store model parameters, dataset versions, random seeds, and evaluation results.
11. **Handle missing and out-of-range inputs more strictly** – Add domain validation for lag and rolling values.
12. **Separate production assets from generated artifacts** – Document whether trained models should be committed or downloaded during deployment.

## Security Notes

This project is intended for local development and academic experimentation. Before deploying it publicly:

- Restrict `allow_origins` instead of using `[`"`*`"`]`.
- Add authentication and authorization if predictions expose sensitive data.
- Validate and constrain all user-provided inputs.
- Avoid returning raw internal exception messages from the API.
- Run behind a production ASGI server and reverse proxy.
- Review serialized model loading carefully and only load trusted `.pkl` files.
- Do not expose confidential datasets or simulation outputs.

## License

No license file is currently included in the repository. Add a `LICENSE` file before distributing or reusing the project under a specific open-source license.

## Acknowledgements

This project brings together machine learning, web development, time-series feature engineering, and discrete-event simulation to study packet loss and router-buffer behavior.
