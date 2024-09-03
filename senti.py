import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Set custom theme and configuration
st.set_page_config(page_title="SentimentSense", page_icon="🧠", layout="wide")

# Add custom styling
st.markdown(
    """
    <style>
    .main {
        background-color: #f4f4f9;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border: None;
        border-radius: 12px;
        height: 40px;
        width: 100%;
        margin: 0.5rem 0;
    }
    .stDownloadButton>button {
        background-color: #1E88E5;
        color: white;
        border: None;
        border-radius: 12px;
        height: 40px;
        width: 100%;
        margin: 0.5rem 0;
    }
    </style>
    """, unsafe_allow_html=True
)

# Title and description with an emoji
st.title("🧠 SentimentSense: Your Text Analysis Companion")
st.markdown(
    """
    **SentimentSense** provides in-depth sentiment analysis to understand the emotions conveyed in your text.
    Simply input your text below and let the magic happen!
    """
)

# Initialize or load session state to keep track of the results
if 'results' not in st.session_state:
    st.session_state['results'] = []

# Sidebar for text input and actions
st.sidebar.header("📝 Input Text for Sentiment Analysis")
text_input = st.sidebar.text_area("Enter text for sentiment analysis:", height=150)
clear_button = st.sidebar.button("Clear Input")
reset_button = st.sidebar.button("Reset Analysis History")

if clear_button:
    text_input = ""
if reset_button:
    st.session_state['results'] = []


# Function to analyze sentiment
def analyze_sentiment(text):
    analyzer = SentimentIntensityAnalyzer()
    sentiment = analyzer.polarity_scores(text)
    return sentiment


# Function to get primary sentiment with an emoji
def get_primary_sentiment(sentiment):
    if sentiment['compound'] >= 0.05:
        return "Positive 😊"
    elif sentiment['compound'] <= -0.05:
        return "Negative 😠"
    else:
        return "Neutral 😐"


# Analyze button
if st.sidebar.button("Analyze Sentiment"):
    if text_input:
        sentiment = analyze_sentiment(text_input)
        primary_sentiment = get_primary_sentiment(sentiment)

        # Display results in the main area
        st.subheader("Analysis Results")
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="Primary Sentiment", value=primary_sentiment)
            st.metric(label="Compound Score", value=round(sentiment['compound'], 2))
        with col2:
            st.metric(label="Positive Score", value=round(sentiment['pos'], 2))
            st.metric(label="Neutral Score", value=round(sentiment['neu'], 2))
            st.metric(label="Negative Score", value=round(sentiment['neg'], 2))

        # Interactive Visualization - Pie Chart for Sentiment Breakdown
        st.subheader("Sentiment Score Distribution")
        pie_chart = px.pie(
            names=['Positive', 'Neutral', 'Negative'],
            values=[sentiment['pos'], sentiment['neu'], sentiment['neg']],
            color=['Positive', 'Neutral', 'Negative'],
            color_discrete_map={'Positive': '#00C853', 'Neutral': '#039BE5', 'Negative': '#D32F2F'},
            title='Sentiment Breakdown'
        )
        st.plotly_chart(pie_chart, use_container_width=True)

        # Interactive Visualization - Gauge Chart for Compound Score
        gauge_chart = go.Figure(go.Indicator(
            mode="gauge+number",
            value=sentiment['compound'],
            title={'text': "Compound Sentiment Score"},
            gauge={'axis': {'range': [-1, 1]},
                   'bar': {'color': "#1E88E5"},
                   'steps': [
                       {'range': [-1, -0.05], 'color': '#D32F2F'},
                       {'range': [-0.05, 0.05], 'color': '#039BE5'},
                       {'range': [0.05, 1], 'color': '#00C853'}],
                   }))
        st.plotly_chart(gauge_chart, use_container_width=True)

        # Store results in session state
        st.session_state['results'].append({
            "Text": text_input,
            "Primary Sentiment": primary_sentiment,
            "Positive": sentiment['pos'],
            "Neutral": sentiment['neu'],
            "Negative": sentiment['neg'],
            "Compound": sentiment['compound']
        })
    else:
        st.warning("Please enter text for analysis.")

# Show past analysis results with a unique style
if st.session_state['results']:
    st.subheader("📊 Sentiment Analysis History")
    result_df = pd.DataFrame(st.session_state['results'])

    # Interactive Timeline of Results using Plotly
    timeline_chart = px.scatter(
        result_df,
        x='Compound',
        y='Primary Sentiment',
        color='Primary Sentiment',
        hover_data=['Text'],
        title='Sentiment Analysis History Timeline',
        color_discrete_map={"Positive 😊": "#00C853", "Neutral 😐": "#039BE5", "Negative 😠": "#D32F2F"}
    )
    st.plotly_chart(timeline_chart, use_container_width=True)

    # Download button for results
    csv = result_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Results as CSV",
        data=csv,
        file_name='sentiment_analysis_results.csv',
        mime='text/csv',
    )
