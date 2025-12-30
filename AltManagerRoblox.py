import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import json
import locale
import time
import sys
import ctypes

if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
ACCOUNTS_FILE = os.path.join(BASE_DIR, "accounts.json")
PROFILES_DIR = os.path.join(BASE_DIR, "profiles")
os.makedirs(PROFILES_DIR, exist_ok=True)

ROBLOX_LOGIN = "https://www.roblox.com/login"
ROBLOX_GAME = "https://www.roblox.com/games/1818/Classic-Crossroads"

def load_json(path, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict) and "accounts" in data:
                return data["accounts"]
            return data
    except:
        return default

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        if path == ACCOUNTS_FILE:
            json.dump({"accounts": data}, f, indent=4, ensure_ascii=False)
        else:
            json.dump(data, f, indent=4, ensure_ascii=False)

LANG = {
    "en": {
        "title": "Alt Manager",
        "subtitle": "Accounts • Browsers • Languages",
        "add": "Add account",
        "login": "Login",
        "play": "Play",
        "language": "Language",
        "browser": "Browser",
        "exists": "Account already exists",
        "no_browser": "Browser not found"
    },
    "ru": {
        "title": "Alt Manager",
        "subtitle": "Аккаунты • Браузеры • Языки",
        "add": "Добавить аккаунт",
        "login": "Войти",
        "play": "Играть",
        "language": "Язык",
        "browser": "Браузер",
        "exists": "Аккаунт уже существует",
        "no_browser": "Браузер не найден"
    },
    "ua": {
        "title": "Alt Manager",
        "subtitle": "Акаунти • Браузери • Мови",
        "add": "Додати акаунт",
        "login": "Увійти",
        "play": "Грати",
        "language": "Мова",
        "browser": "Браузер",
        "exists": "Акаунт вже існує",
        "no_browser": "Браузер не знайдено"
    }
}

def detect_lang():
    if sys.platform != 'win32':
        lang = os.environ.get('LANG', '').split('_')[0].split('-')[0].lower()
        if lang.startswith('ru'):
            return 'ru'
        if lang.startswith('uk'):
            return 'ua'
        return 'en'

    try:
        lang_id = ctypes.windll.kernel32.GetUserDefaultUILanguage()
        if lang_id == 0x0419:
            return 'ru'
        if lang_id == 0x0422:
            return 'ua'
        return 'en'
    except:
        return 'en'

def find_browser(paths):
    for p in paths:
        if p and os.path.exists(p):
            return p
    return None

BROWSERS = {
    "Chrome": find_browser([
        os.path.join(os.environ.get("PROGRAMFILES", ""), "Google", "Chrome", "Application", "chrome.exe"),
        os.path.join(os.environ.get("PROGRAMFILES(X86)", ""), "Google", "Chrome", "Application", "chrome.exe"),
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Google", "Chrome", "Application", "chrome.exe")
    ]),
    "Edge": find_browser([
        os.path.join(os.environ.get("PROGRAMFILES", ""), "Microsoft", "Edge", "Application", "msedge.exe"),
        os.path.join(os.environ.get("PROGRAMFILES(X86)", ""), "Microsoft", "Edge", "Application", "msedge.exe"),
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "Edge", "Application", "msedge.exe")
    ]),
    "Yandex": find_browser([
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Yandex", "YandexBrowser", "Application", "browser.exe"),
        os.path.join(os.environ.get("PROGRAMFILES", ""), "Yandex", "YandexBrowser", "Application", "browser.exe")
    ]),
    "Firefox": find_browser([
        os.path.join(os.environ.get("PROGRAMFILES", ""), "Mozilla Firefox", "firefox.exe"),
        os.path.join(os.environ.get("PROGRAMFILES(X86)", ""), "Mozilla Firefox", "firefox.exe"),
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Mozilla Firefox", "firefox.exe")
    ])
}

AVAILABLE_BROWSERS = [b for b, p in BROWSERS.items() if p is not None]
if not AVAILABLE_BROWSERS:
    AVAILABLE_BROWSERS = ["Chrome", "Edge", "Yandex", "Firefox"]

config = load_json(CONFIG_FILE, {})
accounts_data = load_json(ACCOUNTS_FILE, [])
if isinstance(accounts_data, dict) and "accounts" in accounts_data:
    accounts = accounts_data["accounts"]
else:
    accounts = accounts_data if isinstance(accounts_data, list) else []

current_language = config.get("language", detect_lang())
current_browser = config.get("browser", AVAILABLE_BROWSERS[0] if AVAILABLE_BROWSERS else "Chrome")
T = LANG.get(current_language, LANG["en"])

BG_MAIN = "#0a0e14"
BG_CARD = "#111827"
BG_INPUT = "#020617"
BG_BTN = "#1f2937"
BG_HOVER = "#3b82f6"
FG = "#e5e7eb"
FG_DIM = "#94a3b8"

FONT_TITLE = ("Segoe UI Semibold", 24)
FONT_TEXT = ("Segoe UI", 11)
FONT_BTN = ("Segoe UI Semibold", 11)

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    pass

root = tk.Tk()
root.geometry("840x580")
root.configure(bg=BG_MAIN)
root.resizable(False, False)
root.attributes("-alpha", 0.0)

def fade_in():
    for i in range(0, 101, 2):
        root.attributes("-alpha", i / 100)
        root.update()
        time.sleep(0.006)

root.after(100, fade_in)

card = tk.Frame(root, bg=BG_CARD)
card.place(relx=0.5, rely=0.5, anchor="center", width=780, height=520)

title = tk.Label(card, font=FONT_TITLE, fg=FG, bg=BG_CARD)
subtitle = tk.Label(card, fg=FG_DIM, bg=BG_CARD, font=("Segoe UI", 10))

title.pack(pady=(28, 6))
subtitle.pack()

settings = tk.Frame(card, bg=BG_CARD)
settings.pack(pady=16)

lang_var = tk.StringVar(value=current_language)
browser_var = tk.StringVar(value=current_browser)

def change_language(*_):
    global current_language, T
    current_language = lang_var.get()
    T = LANG.get(current_language, LANG["en"])
    config["language"] = current_language
    save_json(CONFIG_FILE, config)
    refresh_ui()

def change_browser(*_):
    global current_browser
    current_browser = browser_var.get()
    config["browser"] = current_browser
    save_json(CONFIG_FILE, config)

def dropdown(parent, label, var, values, command):
    f = tk.Frame(parent, bg=BG_CARD)
    tk.Label(f, text=label, fg=FG_DIM, bg=BG_CARD).pack(side="left", padx=6)
    m = tk.OptionMenu(f, var, *values, command=lambda _: command())
    m.config(bg=BG_BTN, fg=FG, relief="flat", highlightthickness=0)
    m["menu"].config(bg=BG_BTN, fg=FG)
    f.pack(side="left", padx=12)

dropdown(settings, T["language"], lang_var, list(LANG.keys()), change_language)
dropdown(settings, T["browser"], browser_var, AVAILABLE_BROWSERS, change_browser)

entry = tk.Entry(card, font=FONT_TEXT, bg=BG_INPUT, fg=FG,
                 insertbackground=FG, relief="flat")
entry.pack(fill="x", padx=180, pady=14, ipady=9)

def animated_button(parent, text, command):
    btn = tk.Label(parent, text=text, bg=BG_BTN, fg=FG,
                   font=FONT_BTN, padx=30, pady=13, cursor="hand2")

    def hover_on(e): btn.config(bg=BG_HOVER)
    def hover_off(e): btn.config(bg=BG_BTN)
    def click(e):
        btn.config(bg="#1e40af")
        parent.after(90, lambda: btn.config(bg=BG_HOVER))
        command()

    btn.bind("<Enter>", hover_on)
    btn.bind("<Leave>", hover_off)
    btn.bind("<Button-1>", click)
    return btn

btns = tk.Frame(card, bg=BG_CARD)
btns.pack(pady=20)

btn_add = animated_button(btns, T["add"], lambda: add_account())
btn_login = animated_button(btns, T["login"], lambda: open_url(ROBLOX_LOGIN))
btn_play = animated_button(btns, T["play"], lambda: open_url(ROBLOX_GAME))

btn_add.pack(side="left", padx=14)
btn_login.pack(side="left", padx=14)
btn_play.pack(side="left", padx=14)

listbox = tk.Listbox(
    card, font=FONT_TEXT, bg=BG_INPUT, fg=FG,
    selectbackground=BG_HOVER, relief="flat", height=9
)
listbox.pack(fill="x", padx=200, pady=18)

def refresh_list(animated=True):
    listbox.delete(0, "end")
    if not animated:
        for a in accounts:
            listbox.insert("end", a)
        return

    def insert_step(i=0):
        if i < len(accounts):
            listbox.insert("end", accounts[i])
            root.after(60, lambda: insert_step(i + 1))
    insert_step()

def add_account():
    name = entry.get().strip()
    if not name:
        return
    if name in accounts:
        messagebox.showerror(T["title"], T["exists"])
        return
    accounts.append(name)
    save_json(ACCOUNTS_FILE, accounts)
    entry.delete(0, "end")
    refresh_list()

def open_url(url):
    sel = listbox.curselection()
    if not sel:
        return
    browser_path = BROWSERS.get(current_browser)
    if not browser_path or not os.path.exists(browser_path):
        messagebox.showerror(T["title"], T["no_browser"])
        return
    profile = os.path.join(PROFILES_DIR, listbox.get(sel[0]))
    os.makedirs(profile, exist_ok=True)
    try:
        if current_browser == "Firefox":
            subprocess.Popen([browser_path, "-profile", profile, "-new-window", url])
        else:
            subprocess.Popen([browser_path, f"--user-data-dir={profile}", "--new-window", url])
    except Exception as e:
        messagebox.showerror(T["title"], f"Error launching browser: {str(e)}")

def refresh_ui():
    root.title(T["title"])
    title.config(text=T["title"])
    subtitle.config(text=T["subtitle"])
    btn_add.config(text=T["add"])
    btn_login.config(text=T["login"])
    btn_play.config(text=T["play"])

refresh_ui()
refresh_list(animated=True)
root.mainloop()
