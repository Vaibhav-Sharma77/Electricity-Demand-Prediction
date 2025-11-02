📘 Overview

This project presents an **AI-driven hybrid forecasting system** that predicts **real-time electricity demand and peak load requirements** for the **Delhi Power System**, using both **historical load data** and **weather parameters**.

It leverages **LSTM (Long Short-Term Memory)** for temporal load pattern modeling, **XGBoost** for weather-based demand prediction, and a **Multi-Layer Perceptron (MLP)** ensemble model for combining outputs — achieving high accuracy and adaptability for real-world grid applications.


🌍 Problem Statement

Delhi experiences extreme weather variations and rapid demand fluctuations due to:

* Seasonal temperature and humidity changes
* Industrial and residential load variability
* Renewable energy integration challenges

Accurate **short-term and long-term load forecasting** is essential for:

* Grid stability
* Optimized energy distribution
* Power purchase scheduling
* Renewable balancing and cost efficiency

Traditional models fail to capture complex non-linear dependencies.
Hence, an **AI-based hybrid system** is proposed.

🎯 Objectives

* Build an **AI-powered model** for forecasting electricity demand and identifying peak load intervals.
* Integrate **load and weather data** for robust, real-time predictions.
* Deploy an accessible **Flask web interface** for interactive forecasting.
* Support **data-driven decisions** for utilities and power planners.
* Enable future scalability for **renewable and flexibility forecasting**.


📊 Datasets Used

1️⃣ Electricity Load Dataset

| Column                      | Description                |
| --------------------------- | -------------------------- |
| Date                        | Date of record             |
| TimeSlot                    | 15-min or hourly intervals |
| DELHI                       | Total system load (MW)     |
| BRPL, BYPL, NDPL, NDMC, MES | Regional loads             |

2️⃣ Weather Dataset

| Column               | Description              |
| -------------------- | ------------------------ |
| date                 | Timestamp                |
| temperature_2m       | Ambient temperature (°C) |
| relative_humidity_2m | Humidity (%)             |
| wind_speed_10m       | Wind speed (m/s)         |

Data merged on **date and time** to correlate climatic variations with load patterns.

🧩 Methodology

1. **Data Preprocessing**

   * Handle missing values, outliers, and scaling
   * Merge datasets using timestamp keys
   * Extract temporal features (hour, day, season)

2. **Exploratory Data Analysis**

   * Correlation between weather and demand
   * Time-series trends (daily, weekly, seasonal)
   * Peak load behavior analysis

3. **Modeling**

   * **LSTM:** Captures historical time-series dependencies.
   * **XGBoost:** Learns weather-driven non-linear impacts.
   * **MLP Fusion:** Combines outputs for final optimized forecast.

4. **Evaluation Metrics**

   * Mean Absolute Error (MAE)
   * Root Mean Squared Error (RMSE)
   * Mean Absolute Percentage Error (MAPE)
   * R² Score

---

## ⚙️ Technologies Used

| Category                 | Tools / Frameworks             |
| ------------------------ | ------------------------------ |
| **Programming Language** | Python                         |
| **Machine Learning**     | Scikit-learn, XGBoost          |
| **Deep Learning**        | TensorFlow / Keras (LSTM, MLP) |
| **Data Processing**      | Pandas, NumPy                  |
| **Visualization**        | Matplotlib, Seaborn, Plotly    |
| **Web Framework**        | Flask                          |
| **Deployment**           | Flask Server / Localhost       |
| **Version Control**      | Git, GitHub                    |

🧮 Model Architecture Details

🔹 LSTM Model

* Input: Past 48–72 hours of load data
* Layers: LSTM(64), Dropout(0.2), Dense(32)
* Optimizer: Adam
* Output: Predicted load (MW)

🔹 XGBoost Model

* Input: Weather + Temporal features
* Parameters: n_estimators=500, max_depth=7, learning_rate=0.05
* Output: Weather-based demand prediction

🔹 MLP Ensemble

* Inputs: LSTM and XGBoost outputs
* Hidden Layers: [64, 32]
* Activation: ReLU
* Output: Final load prediction

 📈 Model Performance (Indicative)

| Model                             | MAE      | RMSE     | MAPE     | R²       |
| --------------------------------- | -------- | -------- | -------- | -------- |
| LSTM                              | 58.2     | 74.5     | 2.8%     | 0.95     |
| XGBoost                           | 65.3     | 82.1     | 3.4%     | 0.93     |
| **Hybrid (LSTM + XGBoost + MLP)** | **51.7** | **67.8** | **2.3%** | **0.97** |

---

 🖥️ Flask Web App Features

* Real-time electricity demand prediction
* Weather-based forecasting interface
* Interactive visual dashboards using Plotly
* Upload custom CSV datasets for testing
* REST API endpoint for model inference

 🚀 How to Run the Project
 🧩 Installation

Clone the repository and install dependencies:

```bash
pip install -r requirements.txt
```

 ▶️ Run Locally

```bash
python app.py
```

Then open:

```
http://127.0.0.1:5000/
```

### 🧾 Example API Request

```bash
POST /predict
{
  "temperature_2m": 34.5,
  "relative_humidity_2m": 62,
  "wind_speed_10m": 2.5,
  "time": "18:00",
  "date": "2025-06-11"
}
```

Response:

```json
{
  "predicted_demand_MW": 5237.45
}
```

---

## 🌤️ Future Scope

* Integration with **real-time IoT sensor data**
* **Reinforcement Learning** for adaptive prediction
* **Explainable AI (XAI)** dashboards for transparency
* Cloud deployment on **AWS / Azure / GCP**
* Integration with **renewable energy planning systems**
* Expansion to **railway and metro load forecasting**


