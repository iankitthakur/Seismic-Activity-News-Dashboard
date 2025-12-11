# ==============================================================================
# 1. Create the Streamlit Application File (app.py)
# ==============================================================================
%%writefile app.py
import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime, timedelta
import json
from google.genai.errors import APIError
from google import genai
import os
import plotly.graph_objects as go

# Initialize the client again within the Streamlit process
try:
    # Use the key from the environment variable set in the main Colab cell
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
except Exception:
    client = None

# --- Data Fetching Functions (Unchanged) ---
@st.cache_data(ttl=60*60*4) # Cache for 4 hours
def fetch_earthquake_data(days=30, min_magnitude=3.0):
    """Fetches global earthquake data from USGS for the last 'days'."""
    st.info(f"Fetching USGS Earthquake data (M ≥ {min_magnitude}) for the last {days} days...")

    end_time = datetime.now()
    start_time = end_time - timedelta(days=days)

    USGS_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"

    params = {
        "format": "geojson",
        "starttime": start_time.isoformat(),
        "endtime": end_time.isoformat(),
        "minmagnitude": min_magnitude,
        "orderby": "time-asc"
    }

    try:
        response = requests.get(USGS_URL, params=params)
        response.raise_for_status()
        data = response.json()

        features = data.get("features", [])
        earthquakes = []
        for feature in features:
            props = feature['properties']
            dt_object = datetime.fromtimestamp(props['time'] / 1000).date()
            earthquakes.append({
                'Date': dt_object,
                'Magnitude': props['mag']
            })

        df = pd.DataFrame(earthquakes)
        if df.empty:
            return pd.DataFrame()

        # Aggregate by Day for Count
        df_quakes_daily = df.groupby('Date').agg(
            Earthquake_Count=('Magnitude', 'size'),
            Max_Magnitude=('Magnitude', 'max')
        ).reset_index()

        return df_quakes_daily

    except requests.RequestException as e:
        st.error(f"Error fetching earthquake data: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=60*60*4)
def get_daily_news_sentiment(days=30):
    """Generates synthetic sentiment scores using the Gemini API."""
    if not client:
        st.error("Gemini Client not initialized. Check your GEMINI_API_KEY.")
        return pd.DataFrame()

    st.info(f"Generating synthetic daily news sentiment for the last {days} days using Gemini...")

    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

    system_prompt = f"""
    You are an expert financial and geopolitical analyst. Your task is to generate a statistically plausible time-series of average global news sentiment (compound VADER score) for a dashboard. The sentiment should be represented as a number between -1.0 (extremely negative) and 1.0 (extremely positive), with 0.0 being neutral.

    Generate a daily sentiment score for the period from {start_date} to {end_date}. The daily scores should simulate fluctuations based on real-world events. For instance, most days should be close to 0.0 to 0.1 (slightly positive), but include some significant dips (e.g., -0.3 to -0.6) and occasional spikes (e.5 to 0.8) to simulate major news events. Ensure the time series is continuous.

    Your response MUST be a single JSON array, where each object has two keys: 'Date' (in YYYY-MM-DD format) and 'Avg_Sentiment' (a float). DO NOT include any explanatory text, markdown formatting (like ```json), or notes outside of the JSON array.
    """

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents="Generate the requested time series data now.",
            config={"system_instruction": system_prompt, "response_mime_type": "application/json"}
        )

        # The response text should be pure JSON
        sentiment_data = json.loads(response.text)
        df_sentiment = pd.DataFrame(sentiment_data)
        df_sentiment['Date'] = pd.to_datetime(df_sentiment['Date']).dt.date

        return df_sentiment

    except APIError as e:
        st.error(f"Gemini API Error: Check your API Key or rate limits. {e}")
        return pd.DataFrame()
    except json.JSONDecodeError:
        st.error("Gemini API did not return valid JSON. Retrying may help.")
        return pd.DataFrame()

# --- NEW FUNCTION FOR ROLLING AVERAGE ---
def calculate_rolling_average(df, window=7):
    """Calculates a rolling average for earthquake count."""
    df['Rolling_Avg_Count'] = df['Earthquake_Count'].rolling(window=window, min_periods=1).mean()
    return df
# ----------------------------------------


# --- NEW FUNCTION FOR CANDLESTICK PLOT ---
def plot_sentiment_volatility(df):
    """
    Creates a candlestick-style plot to visualize the sentiment score and its simulated daily volatility.
    """
    # Create synthetic daily range around the average sentiment (Fixed +/- 0.05)
    df['Sentiment_High'] = df['Avg_Sentiment'] + 0.05
    df['Sentiment_Low'] = df['Avg_Sentiment'] - 0.05
    df['Sentiment_Open'] = df['Avg_Sentiment'] + 0.02
    df['Sentiment_Close'] = df['Avg_Sentiment'] - 0.02

    st.subheader("Generated News Sentiment Volatility (Candlestick View)")
    st.markdown("This chart uses a candlestick representation to visualize the daily sentiment score and a simulated fixed volatility range.")

    fig_candle = go.Figure(
        data=[
            go.Candlestick(
                x=df['Date'],
                open=df['Sentiment_Open'],
                high=df['Sentiment_High'],
                low=df['Sentiment_Low'],
                close=df['Sentiment_Close'],
                name='Simulated Sentiment Range',
                increasing_line_color='green',
                decreasing_line_color='red'
            )
        ]
    )

    fig_candle.update_layout(
        xaxis_rangeslider_visible=False,
        yaxis_title="Sentiment Score (-1.0 to 1.0)",
        height=450
    )
    st.plotly_chart(fig_candle, use_container_width=True)
# ----------------------------------------


# --- NEW FUNCTION FOR EARTHQUAKE HEATMAP ---
def plot_earthquake_heatmap(df):
    """
    Creates a calendar-style heatmap showing earthquake counts by day of week across weeks.
    """
    st.subheader("Seismic Activity Heatmap (Weekly Count)")
    st.markdown("Visualizing the distribution of daily earthquake count across the entire selected time period.")

    # 1. Ensure 'Date' is datetime object
    df['Date'] = pd.to_datetime(df['Date'])
    
    # 2. Extract Weekday and Week Number
    df['DayOfWeek'] = df['Date'].dt.day_name()
    df['WeekOfYear'] = df['Date'].dt.isocalendar().week.astype(int)
    
    # Define the order of the days for proper visualization
    day_order = ['Sunday', 'Saturday', 'Friday', 'Thursday', 'Wednesday', 'Tuesday', 'Monday']

    # 3. Create the pivot table for the heatmap
    heatmap_data = df.pivot_table(
        values='Earthquake_Count',
        index='DayOfWeek',
        columns='WeekOfYear',
        fill_value=0  # Fill days with no quakes as 0
    )
    
    # Reindex the rows to ensure days are in order (Sunday at top)
    heatmap_data = heatmap_data.reindex(day_order, axis=0)

    # 4. Create the Plotly Heatmap
    fig_heatmap = px.imshow(
        heatmap_data,
        color_continuous_scale="Plasma", 
        x=heatmap_data.columns,
        y=heatmap_data.index,
        labels=dict(x="Week Number", y="Day of Week", color="Quake Count"),
        aspect="auto"
    )

    fig_heatmap.update_xaxes(side="top")
    fig_heatmap.update_layout(height=400)
    
    st.plotly_chart(fig_heatmap, use_container_width=True)
# ---------------------------------------------


# --- NEW FUNCTION TO ADD CREATOR INFO ---
def add_creator_info(name):
    """Adds a small credit footer to the sidebar."""
    st.sidebar.markdown("---")
    st.sidebar.caption(f"**Project Creator:** {name}")
    st.sidebar.caption("Data: USGS & Gemini API")
# ----------------------------------------


# --- Main Dashboard Layout ---

def main_dashboard():
    st.set_page_config(layout="wide", page_title="Earthquake vs. News Sentiment Mashup")

    st.title("🌎 Earthquake Frequency vs. Global News Sentiment")
    st.markdown("---")

    st.sidebar.header("Configuration")
    days = st.sidebar.slider("Data Range (Days)", min_value=7, max_value=90, value=30)
    min_mag = st.sidebar.slider("Min Earthquake Magnitude", min_value=2.5, max_value=5.0, value=3.0, step=0.5)

    # CALL NEW CREATOR INFO FUNCTION
    add_creator_info("Ankit Thakur") 

    # Fetch data
    df_quakes_daily = fetch_earthquake_data(days=days, min_magnitude=min_mag)
    df_sentiment_daily = get_daily_news_sentiment(days=days)

    if df_quakes_daily.empty or df_sentiment_daily.empty:
        st.error("One or both data sources returned no data or an error occurred. Please check configuration/API keys and try again.")
        return

    # Merge DataFrames on Date
    df_merged = pd.merge(df_quakes_daily, df_sentiment_daily, on='Date', how='inner')
    df_merged = df_merged.sort_values('Date')

    # CALL NEW ROLLING AVERAGE FUNCTION
    df_merged = calculate_rolling_average(df_merged)

    st.header("Correlation Analysis")
    st.subheader(f"Data Mapped: {df_merged['Date'].min().strftime('%b %d')} to {df_merged['Date'].max().strftime('%b %d')} (Total Days: {len(df_merged)})")

    # Calculate Correlation
    corr = df_merged['Earthquake_Count'].corr(df_merged['Avg_Sentiment'])
    st.markdown(f"**Pearson Correlation (Quakes vs. Sentiment):** **`{corr:.4f}`** (A number close to 0 means no linear relationship.)")

    # --- Chart 1: Combined Time Series (Now includes Rolling Average) ---
    st.subheader("Time Series: Quake Count, Rolling Average, and Sentiment")

    fig = px.line(
        df_merged,
        x='Date',
        y='Earthquake_Count',
        labels={'Earthquake_Count': f'Daily Earthquake Count (M ≥ {min_mag})'},
        title=f'Daily Earthquake Count vs. Generated Global News Sentiment',
        height=500
    )

    # Add Rolling Average Trace
    fig.add_scatter(
        x=df_merged['Date'],
        y=df_merged['Rolling_Avg_Count'],
        mode='lines',
        name='7-Day Rolling Avg Quake Count',
        line=dict(color='orange', dash='dot'),
        yaxis='y1'
    )

    # Add Average Sentiment as a secondary y-axis
    fig.add_scatter(
        x=df_merged['Date'],
        y=df_merged['Avg_Sentiment'],
        mode='lines',
        name='Gemini Generated Avg Sentiment',
        yaxis='y2'
    )

    fig.update_layout(
        yaxis=dict(title=f'Earthquake Count (M ≥ {min_mag})', showgrid=False),
        yaxis2=dict(
            title='Avg Global News Sentiment (-1.0 to 1.0)',
            overlaying='y',
            side='right',
            range=[-1, 1],
            showgrid=True
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True)

    # CALL SENTIMENT PLOT FUNCTION
    plot_sentiment_volatility(df_merged)
    
    # CALL HEATMAP FUNCTION
    plot_earthquake_heatmap(df_merged)


    st.markdown("---")
    st.subheader("Raw Data Preview")
    st.dataframe(df_merged[['Date', 'Earthquake_Count', 'Rolling_Avg_Count', 'Max_Magnitude', 'Avg_Sentiment']].tail(10))

if __name__ == "__main__":
    main_dashboard()
