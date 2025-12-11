# Earthquake vs Global News Sentiment Dashboard

This Streamlit application visualizes the relationship between **global
earthquake activity** and **global news sentiment** by combining
real-time USGS earthquake data with synthetic sentiment generated using
the **Google Gemini API**.

------------------------------------------------------------------------

## 🚀 Features

### **1. Real Earthquake Data (USGS API)**

-   Fetches quake data for the last 7--90 days.
-   Configurable minimum magnitude (2.5 to 5.0).
-   Aggregated daily:
    -   Earthquake Count
    -   Maximum Magnitude

### **2. AI‑Generated Global News Sentiment (Gemini)**

-   Uses Gemini 2.5 Flash to generate realistic sentiment values between
    -1 and +1.
-   Includes spikes and dips representing important events.
-   Returned strictly as JSON for clean parsing.

### **3. Data Processing**

-   Datasets merge on **Date**.
-   Computes **7‑day rolling average** of earthquake counts.
-   Calculates **Pearson correlation** between quakes and sentiment.

### **4. Visualizations**

-   📈 **Dual‑axis Line Chart** (quakes + sentiment)
-   🕯 **Candlestick Sentiment Volatility Chart**
-   🔥 **Earthquake Heatmap** (calendar-style weekly distribution)
-   🧮 **Raw data preview table**

------------------------------------------------------------------------

## 🧩 How It Works

1.  **USGS fetch** → pulls earthquake events.
2.  **Gemini generation** → produces synthetic sentiment series.
3.  **Merge data** → aligns both datasets by date.
4.  **Visualize** → interactive charts powered by Plotly.
5.  **Customize** → users adjust time range + magnitude in sidebar.

------------------------------------------------------------------------

## 📦 Technologies Used

-   **Python**
-   **Streamlit**
-   **Pandas**
-   **Plotly**
-   **Google Gemini API**
-   **USGS Earthquake Catalog API**

------------------------------------------------------------------------

## 📁 Project Structure

    app.py          # Main Streamlit dashboard

------------------------------------------------------------------------

## ▶ Running the App

### 1. Install Dependencies

    pip install streamlit pandas plotly google-genai requests

### 2. Set Your Gemini API Key

    export GEMINI_API_KEY="your_key_here"

### 3. Run Streamlit App

    streamlit run app.py

------------------------------------------------------------------------

## 👨‍💻 Creator

**Ankit Thakur**\
Data sources: **USGS** & **Google Gemini API**

------------------------------------------------------------------------

## 📜 License

This project is for educational and research purposes.
