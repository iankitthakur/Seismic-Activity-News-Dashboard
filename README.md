# Earthquake vs Global News Sentiment Dashboard

This project presents a professional analytical dashboard built with
Streamlit to investigate possible relationships between global
earthquake activity and global news sentiment trends. It integrates real
seismic data from the USGS Earthquake Catalog with synthetic sentiment
data generated using the Google Gemini API. The dashboard provides
correlation analysis, rolling averages, volatility visualization,
heatmaps, and configurable user controls.

## Overview

The dashboard performs the following core operations:

1.  Fetches real earthquake event data for user-selected time ranges.
2.  Generates a statistically realistic sentiment time series using the
    Gemini model.
3.  Merges both datasets on a daily basis for comparative analysis.
4.  Computes correlations and rolling averages.
5.  Renders interactive visualizations for exploratory evaluation.

## Features

### Real Earthquake Data (USGS)

-   Retrieves earthquake data from the USGS Earthquake API.
-   Configurable date range (7--90 days).
-   Minimum magnitude filter (2.5 to 5.0).
-   Produces daily aggregates:
    -   Earthquake count
    -   Maximum magnitude

### Synthetic Global Sentiment (Gemini)

-   Uses Gemini 2.5 Flash to generate daily sentiment scores.
-   Sentiment range: -1.0 to +1.0.
-   Includes realistic positive and negative fluctuations.
-   Delivered strictly as JSON for predictable parsing.

### Data Processing and Analysis

-   Merges daily seismic and sentiment datasets by date.
-   Computes a 7-day rolling average of earthquake frequency.
-   Calculates Pearson correlation to identify linear relationships.
-   Handles missing or inconsistent values gracefully.

### Visualizations

-   Dual-axis time series chart displaying earthquake counts, rolling
    averages, and sentiment scores.
-   Candlestick chart illustrating daily sentiment volatility.
-   Heatmap showing weekly earthquake distribution patterns.
-   Tabular view of merged and cleaned data.

## Technology Stack

-   Python\
-   Streamlit\
-   Pandas\
-   Plotly\
-   Requests\
-   Google Gemini API

## Project Structure

    app.py          # Main Streamlit dashboard script

## Installation and Setup

### 1. Install required packages

    pip install streamlit pandas plotly requests google-genai

### 2. Configure your Gemini API key

macOS/Linux:

    export GEMINI_API_KEY="your_key_here"

Windows (PowerShell):

    setx GEMINI_API_KEY "your_key_here"

### 3. Launch the application

    streamlit run app.py

## Usage Instructions

1.  Start the Streamlit app and open the provided local URL.
2.  Adjust the sidebar controls:
    -   Date range
    -   Minimum earthquake magnitude
3.  Explore the time-series charts, sentiment volatility view, and
    earthquake heatmap.
4.  Review the correlation coefficient and raw data table.

## Author

**Ankit Thakur**\
Data sources: USGS Earthquake Catalog and Google Gemini API.
