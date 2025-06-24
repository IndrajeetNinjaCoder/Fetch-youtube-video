import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
import requests
from datetime import datetime

# Load environment variables
load_dotenv()

app = Flask(__name__)

WEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# === 1. Get Weather ===
def get_weather(api_key, city="Delhi"):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    data = response.json()
    if response.status_code != 200 or 'weather' not in data:
        return "Unknown", 0
    return data['weather'][0]['main'], data['main']['temp']

# === 2. Get Time of Day ===
def get_time_of_day():
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return "Morning"
    elif 12 <= hour < 17:
        return "Afternoon"
    elif 17 <= hour < 21:
        return "Evening"
    else:
        return "Night"

# === 3. Build Prompt ===
def build_prompt(weather, time_of_day, mood, activity):
    return f"""
    You are a fun, modern music assistant for Indian Gen Z users.

    🎯 Your **top priority** is the user's **mood** — always suggest songs that best match or elevate the mood. 
    🎯 Second priority is the **activity** — tailor the playlist to fit what the user is doing.
    🎯 Third comes the **weather** — it can influence the vibe, so consider it if it fits.
    🎯 Least important is **time of day** — use it only when mood and activity are neutral or unclear.

    Suggest 5 **trending Indian songs** (Bollywood, Tollywood, Punjabi, Hindi Pop, etc.) that are currently viral or have high YouTube views.
    Include Hollywood/English songs only if they’re extremely popular and trending in India.

    Make it sound like a real Gen Z playlist — short, catchy, no fluff.

    🔍 Context:
    - Mood: {mood}
    - Activity: {activity}
    - Weather: {weather}
    - Time of Day: {time_of_day}

    🎵 Output Format (strict):
    - Song Name – Artist (Language)

    No intros. No explanations. Just the 5 bold, catchy playlist suggestions.
    """

# === 4. Call Groq LLaMA 3 ===
def call_llama3_groq(prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama3-70b-8192",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.8
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        data = response.json()
        if "choices" in data:
            return data["choices"][0]["message"]["content"]
        else:
            return "❌ Failed to get song suggestions."
    except Exception as e:
        return f"❌ Error calling Groq API: {str(e)}"

# === 5. API Route ===
@app.route("/get-songs", methods=["GET"])
def get_songs():
    mood = request.args.get("mood", default="neutral")
    activity = request.args.get("activity", default="studying")
    user_weather = request.args.get("weather")
    user_time = request.args.get("time")

    weather = user_weather if user_weather else get_weather(WEATHER_API_KEY)[0]
    time_of_day = user_time if user_time else get_time_of_day()

    prompt = build_prompt(weather, time_of_day, mood, activity)
    raw_response = call_llama3_groq(prompt)

    lines = raw_response.split("\n")
    songs = []
    for line in lines:
        clean_line = line.strip().lstrip("•*-1234567890. 🎵").strip()
        if "–" in clean_line:
            songs.append(clean_line)

    if not songs:
        songs = [
            "Kesariya - Arijit Singh (Hindi)",
            "Butta Bomma - Armaan Malik (Telugu)",
            "Excuses - AP Dhillon (Punjabi)",
            "Naatu Naatu - Rahul Sipligunj, Kaala Bhairava (Telugu)",
            "Tere Vaaste - Varun Jain (Hindi)"
        ]

    return jsonify({
        "weather": weather,
        "time_of_day": time_of_day,
        "mood": mood,
        "activity": activity,
        "recommended_songs": songs
    })

# === 6. Start Server ===
if __name__ == "__main__":
    app.run(debug=True, port=5000)



