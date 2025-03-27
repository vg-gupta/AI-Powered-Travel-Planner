import streamlit as st
import openai
import requests
import os

# Set OpenRouter API Key (Replace with your actual OpenRouter API key)
OPENROUTER_API_KEY = "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"  # Replace with your OpenRouter API Key

# Initialize OpenRouter Client
client = openai.OpenAI(api_key=OPENROUTER_API_KEY, base_url="https://openrouter.ai/api/v1")


# Function to fetch travel recommendations using SerpAPI
def fetch_travel_recommendations(query):
    SERPAPI_KEY = "378227f20d34d105646ea1b4e8295e7e3f4f72cda2c47b3aa9352eefbea7f6d5"  # Replace with your SerpAPI key
    url = f"https://serpapi.com/search.json?q={query}&hl=en&gl=us&api_key={SERPAPI_KEY}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        results = response.json().get("organic_results", [])
        return [result["title"] for result in results[:5]]
    except requests.exceptions.RequestException as e:
        return [f"Error fetching results: {e}"]


# Function to generate a structured travel itinerary using OpenRouter API
def generate_itinerary(user_data):
    """Generate a structured travel itinerary using OpenRouter API."""
    prompt = f"""
    Create a {user_data['duration']}-day travel itinerary for {user_data['destination']}.
    - Budget: {user_data['budget']}
    - Interests: {', '.join(user_data['interests'])}
    - Accommodation preference: {user_data['accommodation']}
    - Walking tolerance: {user_data['walking_tolerance']}
    
    Provide a detailed, step-by-step itinerary with:
    - Activities for each day
    - Best places to eat (local recommendations)
    - Travel tips
    - Cultural experiences
    - Budget-friendly or luxury options as per preference
    """

    try:
        response = client.chat.completions.create(
            model="deepseek/deepseek-chat-v3-0324:free",  # Try "anthropic/claude-3-opus" for better results
            messages=[
                {"role": "system", "content": "You are a professional AI travel planner."},
                {"role": "user", "content": prompt},
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error generating itinerary: {e}"


# Streamlit UI Setup
st.set_page_config(page_title="🌍 AI Travel Planner", layout="wide")
st.title("🌍 AI-Powered Travel Planner")
st.write("Plan your perfect trip with AI-powered suggestions and a personalized itinerary!")

# User Input Fields
destination = st.text_input("✈️ Destination", placeholder="E.g., Paris, Tokyo, New York")
duration = st.slider("📅 Trip Duration (in days)", 1, 14, 5)
budget = st.selectbox("💰 Budget", ["Low", "Medium", "Luxury"])
interests = st.multiselect("🎭 Interests", ["Nature", "Food", "Culture", "Adventure", "Relaxation"])
accommodation = st.selectbox("🏨 Preferred Accommodation", ["Budget", "Mid-range", "Luxury"])
walking_tolerance = st.selectbox("🚶 Walking Tolerance", ["High", "Moderate", "Low"])

# Generate Itinerary Button
if st.button("🚀 Generate Itinerary"):
    if not destination:
        st.error("❌ Please enter a destination!")
    else:
        st.session_state.user_data = {
            "destination": destination,
            "duration": duration,
            "budget": budget,
            "interests": interests,
            "accommodation": accommodation,
            "walking_tolerance": walking_tolerance,
        }

        with st.spinner("🔎 Fetching recommendations..."):
            attractions = fetch_travel_recommendations(f"Top attractions in {destination}")

        st.subheader("📍 Recommended Attractions")
        if attractions:
            for idx, attraction in enumerate(attractions, 1):
                st.write(f"**{idx}.** {attraction}")
        else:
            st.write("⚠️ No attractions found. Please try again.")

        with st.spinner("📝 Generating your personalized itinerary..."):
            itinerary = generate_itinerary(st.session_state.user_data)

        st.subheader("📜 Your Personalized Itinerary")
        st.markdown(itinerary)
