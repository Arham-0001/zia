import speech_recognition as sr
from api import API_KEY, weather_api, news_api
import pyttsx3
from datetime import datetime
import webbrowser
import musiclibrary
import requests


engine=pyttsx3.init() 

voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id) # replace index with [0] for male voice

music=musiclibrary.music


def speak(text):
    engine.say(text)
    engine.runAndWait()
def chatbot_response(msg):
    headers = {
    "Authorization": f"Bearer {API_KEY}", #replace with your API key of chatbot
    "HTTP-Referer": "https://your-app-name.com", 
    "X-Title": "Test Chat",
    "Content-Type": "application/json"
    }
    data = {
    "model": "mistralai/mistral-7b-instruct:free",
    "messages": [
        {"role" : "system" , "content":" your are an ai assistant who answered in short term"},
        {"role": "user", "content": msg }
    ]
    }
    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
    try:
        if response.status_code == 200:
            reply = response.json()["choices"][0]["message"]["content"]
            print("Bot reply:", reply)
            speak(reply)
    except Exception as e:
            print("Error:", e)
            speak(e)
def weather(city_name):
    base_url = "http://api.openweathermap.org/data/2.5/weather"
        
    # Parameters to be sent to the API
    params = {
                'q': city_name,
                'appid': weather_api, #your openweather api key
                'units': 'metric'  # For temperature in Celsius
    }

    # Sending GET request
    response = requests.get(base_url, params=params)

    if response.status_code == 200:
            data = response.json()
            speak(f"📍 City: {data['name']}")
            speak(f"🌡️ Temperature: {data['main']['temp']}°C")
            speak(f"🌥️ Weather: {data['weather'][0]['description']}")
            speak(f"💨 Wind Speed: {data['wind']['speed']} m/s")
            speak(f"💧 Humidity: {data['main']['humidity']}%")
    else:
        print("Error:", response.status_code, "-", response.json().get("message", "Unable to fetch data"))


def processcmd(command):
    if command.lower() =="open youtube":
        webbrowser.open("https://youtube.com")
    elif command.lower() =="open spotify":
        webbrowser.open("https://open.spotify.com")
    elif command.lower() =="open chatgpt":
        webbrowser.open("https://chat.openai.com")
    elif command.lower() =="open email":
        webbrowser.open("https://mail.google.com")
    elif "today's date" in command.lower():
         today = datetime.now()
         speak(f"today's date is {today.day} {today.strftime('%B')} {today.year}")
    elif "time" in command.lower(): 
        now = datetime.now()
        speak(f"current time is {now.hour} {now.minute}")
    elif command.lower().startswith("play"):
        text =command.lower().split(" ",1)[1]
        song=music[text]
        if song:
            webbrowser.open(song)
        else:
            speak("sorry this song is not available")
    elif "news" in command:
        url = f"https://newsapi.org/v2/top-headlines?country=in&apiKey={news_api}" #your news api key
        req = requests.get(url)

        if req.status_code == 200:
            data = req.json()
            articles = data.get('articles', [])

            if not articles:
                speak("Sorry, no technology news found right now.")
                return

            speak("Here are the top 5 technology headlines:")
            for i, article in enumerate(articles[:5], start=1):
                title = article.get('title', 'No title available')
                print(f"{i}. {title}")
                speak(title)
        else:
            print("News API error:", req.status_code, req.text)
            speak("Sorry, I couldn't fetch technology news at the moment.")
    
    elif "weather" in command:
        speak("which city")
        try:
            r=sr.Recognizer()
            with sr.Microphone() as source:
                            audio = r.listen(source, timeout=4, phrase_time_limit=3)
                            city = r.recognize_google(audio)
        except Exception as e:
            print("error in weather:",e)

        weather(city)

       
    else:
        reply = chatbot_response(command)
        print("Bot:", reply)
        speak(reply)



if __name__ == "__main__":
    speak("initallizing alexaa")
    r=sr.Recognizer()
    while True:
        try:
            with sr.Microphone() as source:
                print("Listening for wake word....")
                audio = r.listen(source, timeout=3, phrase_time_limit=2) 
                word = r.recognize_google(audio) 
                print("Heard:", word)

                if word.lower() == "alexa":
                    speak("alexa activated , how may i help you ?")
                    print("alexa is activated")               

                    with sr.Microphone() as source:
                        audio = r.listen(source, timeout=4, phrase_time_limit=3)
                        command = r.recognize_google(audio)

                if word.lower()=="exit":
                    speak("good bye, Have a nice day")
                    break
                else:
                    print(command)
                    processcmd(command)


        except Exception as e:
            print("error:",e) 