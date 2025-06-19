import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import pyttsx3
import schedule
import time
import threading
import webbrowser
import os
import requests
import urllib.request
import pygame
import json
import sys
from datetime import datetime, timedelta

# ==== Səs sistemi ====
engine = pyttsx3.init()
engine.setProperty('rate', 180)
engine.setProperty('volume', 1.0)
for voice in engine.getProperty('voices'):
    if "tr" in voice.id or "Turkish" in voice.name:
        engine.setProperty('voice', voice.id)
        break

def speak(text):
    log(f"Jarvis: {text}")
    engine.say(text)
    engine.runAndWait()

# ==== Resurs yolu ====
def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# ==== İnsan məlumatı JSON ilə ====
def insan_bax():
    try:
        path = get_resource_path("insanlar.json")
        with open(path, "r", encoding="utf-8") as f:
            insanlar = json.load(f)
        ad = simpledialog.askstring("İnsan", "Kimin haqqında məlumat istəyirsən?")
        if not ad: return
        ad_input = ad.strip().lower()
        for key in insanlar:
            if ad_input in key.lower():
                info = insanlar[key]
                mesaj = f"{key} {info['yaş']} yaşındadır. Peşəsi: {info['peşə']}. Hobbiləri: {', '.join(info['hobbilər'])}."
                speak(mesaj)
                return
        speak("Bu insan haqqında məlumat tapılmadı.")
    except Exception as e:
        speak(f"Xəta: {e}")

# ==== Hava və saat ====
def get_weather_and_time():
    try:
        city = city_entry.get()
        if not city:
            speak("Zəhmət olmasa şəhər daxil edin.")
            return
        api_key = "811db1e392571dae28ebef308fe40412"
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=az"
        res = requests.get(url).json()
        if res["cod"] != "404":
            temp = res["main"]["temp"]
            desc = res["weather"][0]["description"]
            timezone_offset = res["timezone"]
            local_time = datetime.utcnow() + timedelta(seconds=timezone_offset)
            local_time_str = local_time.strftime("%H:%M:%S")
            mesaj = f"{city} üçün temperatur {temp}°, hava: {desc}, saat {local_time_str}"
            speak(mesaj)
            
        else:
            speak("Şəhər tapılmadı.")
    except Exception as e:
        speak(f"Hava məlumatı alınmadı: {e}")

# ==== Musiqi çal/dur ====
def play_music():
    try:
        music_path = get_resource_path("soundhelix1.mp3")
        if not os.path.exists(music_path):
            url = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"
            urllib.request.urlretrieve(url, music_path)
        pygame.mixer.init()
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.play()
        speak("Musiqi başladı.")
    except Exception as e:
        speak(f"Musiqi çalınmadı: {e}")

def stop_music():
    try:
        pygame.mixer.music.stop()
        speak("Musiqi dayandırıldı.")
    except:
        speak("Heç bir musiqi çalmır.")

# ==== Xatırlatma ====
def xatirlat(text):
    speak(f"Xatırlatma: {text}")

def add_reminder():
    text = entry_text.get()
    minute = entry_time.get()
    if not text or not minute.isdigit():
        messagebox.showerror("Xəta", "Məlumat düzgün deyil.")
        return
    schedule.every(int(minute)).minutes.do(xatirlat, text=text)
    reminders_list.insert(tk.END, f"{minute} dəq: {text}")
    speak(f"{text} üçün xatırlatma əlavə edildi.")

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

# ==== Komandaların işlənməsi ====
def process_command(cmd):
    cmd = cmd.lower()
    if cmd == "tarix":
        speak(f"Bugün {datetime.now().strftime('%Y-%m-%d')}")
    elif cmd == "hava":
        get_weather_and_time()
    elif cmd == "youtube":
        webbrowser.open("https://youtube.com")
        speak("YouTube açılır.")
    elif cmd == "google":
        webbrowser.open("https://google.com")
        speak("Google açılır.")
    elif "musiqi" in cmd and "çal" in cmd:
        play_music()
    elif "musiqi" in cmd and "dayan" in cmd:
        stop_music()
    elif "insan" in cmd:
        insan_bax()
    elif cmd == "clear logs":
        log_text.delete('1.0', tk.END)
        speak("Loglar təmizləndi.")
    elif "söndür" in cmd:
        speak("Kompüter söndürülür...")
        os.system("shutdown /s /t 0")
    elif "yenidən başlat" in cmd or "restart" in cmd:
        speak("Kompüter yenidən başladılır...")
        os.system("shutdown /r /t 0")
    elif cmd == "çıx":
        speak("Jarvis bağlanır.")
        app.quit()
    else:
        speak("Bu komandanı anlamadım.")

def yazili_komanda_ver():
    cmd = simpledialog.askstring("Komanda", "Komandanı yaz:")
    if cmd:
        process_command(cmd)

# ==== GUI quruluşu ====
app = tk.Tk()
app.title("🧠 Jarvis Assistant")
app.geometry("800x700")
app.configure(bg="#0d1117")
app.grid_rowconfigure(4, weight=1)
app.grid_columnconfigure(0, weight=1)

# ==== Parol ====
if simpledialog.askstring("Parol", "Parolu daxil et:") != "MehdiHuseyn2025":
    messagebox.showerror("Xəta", "Yanlış parol.")
    app.destroy()
    sys.exit()

font = ("Segoe UI", 13)

# ==== Başlıq ====
tk.Label(app, text="🧠 Jarvis Assistant", font=("Segoe UI", 24, "bold"),
         bg="#0d1117", fg="#00ffff").grid(row=0, column=0, pady=10)

# ==== Girişlər ====
frame_inputs = tk.Frame(app, bg="#0d1117")
frame_inputs.grid(row=1, column=0, sticky="ew", padx=20)

entry_text = tk.Entry(frame_inputs, font=font, width=25, bg="#161b22", fg="#00ffcc")
entry_text.insert(0, "Nəyi xatırlatsın?")
entry_text.grid(row=0, column=0, padx=5)

entry_time = tk.Entry(frame_inputs, font=font, width=10, bg="#161b22", fg="#00ffcc")
entry_time.insert(0, "5")
entry_time.grid(row=0, column=1, padx=5)

city_entry = tk.Entry(frame_inputs, font=font, width=20, bg="#161b22", fg="#00ffcc")
city_entry.insert(0, "Şəhər (hava üçün)")
city_entry.grid(row=0, column=2, padx=5)

ttk.Style().configure("TButton", font=font)
ttk.Button(frame_inputs, text="➕ Xatırlatma", command=add_reminder).grid(row=0, column=3, padx=5)

# ==== Log və Xatırlatmalar ====
frame_bottom = tk.Frame(app, bg="#0d1117")
frame_bottom.grid(row=4, column=0, sticky="nsew", padx=20, pady=10)
frame_bottom.grid_rowconfigure(0, weight=1)
frame_bottom.grid_columnconfigure(0, weight=1)
frame_bottom.grid_columnconfigure(1, weight=1)

log_text = tk.Text(frame_bottom, font=("Consolas", 11), bg="#161b22", fg="white")
log_text.grid(row=0, column=0, sticky="nsew", padx=5)

reminders_list = tk.Listbox(frame_bottom, font=("Consolas", 11), bg="#161b22", fg="#00ffcc")
reminders_list.grid(row=0, column=1, sticky="nsew", padx=5)

def log(msg):
    log_text.insert(tk.END, msg + "\n")
    log_text.see(tk.END)

# ==== Əlavə düymələr ====
ttk.Button(app, text="🎯 Komanda Yaz", command=yazili_komanda_ver).grid(row=5, column=0, pady=10)
tk.Label(app, text="Əmr: tarix | hava | youtube | google | musiqi çal/dayan | insan | clear logs | söndür | restart | çıx",
         font=("Segoe UI", 10), fg="#ccc", bg="#0d1117").grid(row=6, column=0, pady=5)

# ==== İşə başla ====
threading.Thread(target=run_scheduler, daemon=True).start()
speak("Jarvis işə başladı.")
log("✅ Jarvis aktivdir...")

app.mainloop()
