import time
import os
import sys

# Speed (printing delay)
typing_speed = 0.08  # smaller = faster

# ✏️ Your Lyrics Here (each line separately)
lyrics = [
    "I think they call this love,",
    "Feels like something from above,",
    "Heartbeats getting louder...",
    "And I don't want this to stop..."
]

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def typewriter(text):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(typing_speed)
    print()  # new line

clear_screen()
print("\n🎵  Lyrics Display  🎵\n")

for line in lyrics:
    typewriter(line)
    time.sleep(0.8)  # delay between lines
