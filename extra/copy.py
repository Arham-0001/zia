import speech_recognition as sr
from api import API_KEY, weather_api, news_api
import pyttsx3
from datetime import datetime
import webbrowser
import musiclibrary
from time import time
import webapp
import requests


engine=pyttsx3.init() 

voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id) # replace index with [0] for male voice

music=musiclibrary.music
app=webapp.app


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
        
def fetch_news(api_key, country='in', page_size=5, language=None, q=None):
    """Fetch top headlines from NewsAPI.org.

    Returns a dict: {'articles': [...], 'totalResults': N} on success,
    or {'error': 'message'} on network/HTTP/JSON failure.
    Accepts optional `country`, `language`, and `q` (query) parameters.
    """
    url = "https://newsapi.org/v2/top-headlines"
    params = {'apiKey': api_key, 'pageSize': page_size}
    # Only include optional params when provided
    if country:
        params['country'] = country
    if language:
        params['language'] = language
    if q:
        params['q'] = q
    try:
        resp = requests.get(url, params=params, timeout=10)
    except requests.RequestException as e:
        return {'error': f'Request error: {e}'}

    # Non-200 responses -> return error with body where possible
    if resp.status_code != 200:
        try:
            body = resp.json()
        except Exception:
            body = resp.text
        return {'error': f'Status {resp.status_code}: {body}'}

    try:
        data = resp.json()
    except Exception as e:
        return {'error': f'Invalid JSON response: {e}'}

    articles = data.get('articles', [])
    total = data.get('totalResults', 0)
    # Return success even if articles is empty so caller can attempt fallback
    return {'articles': articles, 'totalResults': total}



def processcmd(command):
    if "open" in command or "run" in command:
        command = command.replace("open","").replace("run","").strip()
        url=app.get(command)
        if url:
            webbrowser.open(url)
        else:
            speak("sorry i coudn't find the app url")
        
    
    elif "today's date" in command.lower():
         today = datetime.now()
         speak(f"today's date is {today.day} {today.strftime('%B')} {today.year}")
    
    
    elif "time" in command.lower(): 
        now = datetime.now()
        speak(f"current time is {now.hour} {now.minute}")

    
    elif command.lower().startswith("play"):
        text =command.replace("play","").strip().lower()
        song=music.get(text)
        if song:
            webbrowser.open(song)
        else:
            speak("sorry this song is not available")

    elif "news" in command.lower():
        # Use helper to fetch news so we can handle errors and debug easily
        result = fetch_news(news_api, country='in', page_size=5)
        if 'error' in result:
            print("News fetch error:", result['error'])
            speak("Sorry, I couldn't fetch the news right now.")
            return

        articles = result.get('articles', [])
        # If there are no articles for the chosen country, try a fallback without country
        if not articles:
            print('No articles returned for country=in; attempting fallback (no country, language=en)')
            fallback = fetch_news(news_api, country=None, language='en', page_size=5)
            if 'error' in fallback:
                print('News fallback error:', fallback['error'])
                speak("Sorry, I couldn't fetch the news right now.")
                return
            articles = fallback.get('articles', [])

        if not articles:
            speak("Sorry, I couldn't find any news at the moment.")
            return

        speak("Here are the top headlines:")
        for i, article in enumerate(articles[:5], start=1):
            title = article.get('title', 'No title available')
            print(f"{i}. {title}")
            speak(title)
    
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

    elif "note" in command or "notes" in command or "to do" in command or "remember" in command or "add" in command:
        if "notes that" in command or "remember" in command or "add" in command:
            note_text=command.replace("note that","").replace("remember","").replace("add","").replace("note","").strip()
            if note_text:
                with open("note.txt","a",encoding="utf-8") as f:
                    f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M')} - {note_text}\n")
                speak("Okay, I have noted that down.")
            else:
                speak("What should I note down?") 
        
        elif "show" in command or "read" in command or "my notes" in command:
            try:
                with open("note.txt", "r", encoding="utf-8") as f:
                    notes = f.read().strip()
                    if notes:
                        speak("Here are your notes.")
                        print(notes)
                        speak(notes)
                    else:
                        speak("You don't have any notes yet.")
            except FileNotFoundError:
                speak("You don't have any notes yet.")
            
        elif "clear" in command or "delete" in command:
            open("note.txt", "w").close()
            speak("All notes have been cleared.")
        else:
            speak("Would you like to add, read, or clear notes?")

       
    else:
        reply = chatbot_response(command)


if __name__ == "__main__":
    speak("initializing alexa")
    r = sr.Recognizer()
    r.dynamic_energy_threshold = True
    r.pause_threshold = 0.7       # allow short pauses in long speech
    r.non_speaking_duration = 0.5
    mic = sr.Microphone()

    # calibrate once
    with mic as source:
        print("Calibrating microphone for ambient noise...")
        r.adjust_for_ambient_noise(source, duration=0.8)
        print("Calibration done. Energy threshold:", r.energy_threshold)

    while True:
        try:
            with mic as source:
                print("Listening for wake word...")
                # Allow longer time to start speaking and longer phrase so user can say more
                try:
                    audio = r.listen(source, timeout=8, phrase_time_limit=10)  # <- increased
                    word = r.recognize_google(audio, language="en-IN")           # or "en-US"
                except sr.WaitTimeoutError:
                    print("No speech detected in timeout window — continuing.")
                    continue
                except sr.UnknownValueError:
                    print("Could not understand audio for wake word.")
                    continue
                except Exception as e:
                    print("Wake recognition error:", e)
                    continue

            word = word.lower().strip()
            print("Heard (wake):", word)

            # exact wake word
            if word == "alexa":
                speak("Yes? How can I help you?")
                print("Wakeword detected, listening for full command...")
                with mic as source:
                    # small re-calibration helps after wake
                    r.adjust_for_ambient_noise(source, duration=0.3)
                    # listen for a longer phrase (user can speak long sentence)
                    try:
                        audio = r.listen(source, timeout=8, phrase_time_limit=20)  # allow long commands
                        command = r.recognize_google(audio, language="en-IN")
                        print("Recognized command:", command)
                    except sr.WaitTimeoutError:
                        speak("I didn't hear anything. Please try again.")
                        continue
                    except sr.UnknownValueError:
                        # save audio for debugging
                        wav_data = audio.get_wav_data()
                        fname = f"debug_unknown_{int(time.time())}.wav"
                        with open(fname, "wb") as f:
                            f.write(wav_data)
                        print(f"Could not understand command. Saved to {fname}")
                        speak("Sorry, I didn't catch that. Can you repeat?")
                        continue
                    except Exception as e:
                        print("Command recognition error:", e)
                        speak("Sorry, something went wrong while listening.")
                        continue

                # process the recognized command
                cmd = command.strip()
                if cmd.lower() == "exit":
                    speak("Goodbye, have a nice day.")
                    break
                processcmd(cmd)

            # wake+command in same utterance: "alexa play song..."
            elif "alexa" in word:
                command = word.replace("alexa", "").strip()
                print("Command (same utterance):", command)
                if not command:
                    speak("Yes?")
                    continue
                if "exit" in command.lower():
                    speak("Goodbye, have a nice day.")
                    break
                processcmd(command)

            elif "exit" in word:
                speak("Goodbye, have a nice day.")
                break

            else:
                # nothing relevant heard
                continue

        except KeyboardInterrupt:
            speak("Shutting down.")
            break
        except Exception as e:
            print("Main loop error:", e)
            continue
