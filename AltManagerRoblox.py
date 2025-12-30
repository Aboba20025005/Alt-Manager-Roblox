import sys
import os
import json
import random
import locale
import subprocess

from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QVBoxLayout, QListWidget, QLineEdit, QComboBox
)
from PySide6.QtCore import Qt, QTimer, QPoint
from PySide6.QtGui import (
    QPainter, QColor, QFont, QLinearGradient, QPalette
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "accounts.json")
SETTINGS_FILE = os.path.join(BASE_DIR, "settings.json")
PROFILES_DIR = os.path.join(BASE_DIR, "profiles")
os.makedirs(PROFILES_DIR, exist_ok=True)

ROBLOX_LOGIN = "https://www.roblox.com/login"
ROBLOX_GAME = "https://www.roblox.com/games/1818/Classic-Crossroads"

BROWSERS = {
    "chrome":  ("Google Chrome",  'start chrome --user-data-dir="{profile}" {url}'),
    "edge":    ("Microsoft Edge", 'start msedge --user-data-dir="{profile}" {url}'),
    "firefox": ("Mozilla Firefox",'start firefox -profile "{profile}" {url}'),
    "yandex":  ("Yandex Browser", 'start browser --user-data-dir="{profile}" {url}')
}

LANG = {
    "en": {
        "title": "Alt Manager v2",
        "nickname": "Account nickname",
        "add": "Add account",
        "login": "Login",
        "play": "Play",
        "remove": "Remove",
        "browser": "Browser",
        "agree": "I Agree",
        "disc_title": "⚠️ Disclaimer",
        "disc_text": (
            "Alt Manager v2 is a helper tool.\n\n"
            "The author does NOT bypass Roblox systems.\n"
            "The author is NOT responsible for bans,\n"
            "account losses or any consequences.\n\n"
            "All responsibility lies on the user."
        )
    },
    "ru": {
        "title": "Alt Manager v2",
        "nickname": "Ник аккаунта",
        "add": "Добавить аккаунт",
        "login": "Войти",
        "play": "Играть",
        "remove": "Удалить",
        "browser": "Браузер",
        "agree": "Принимаю",
        "disc_title": "⚠️ Дисклеймер",
        "disc_text": (
            "Alt Manager v2 — вспомогательный инструмент.\n\n"
            "Автор НЕ обходит системы Roblox.\n"
            "Автор НЕ несёт ответственности за блокировки,\n"
            "потери аккаунтов или последствия.\n\n"
            "Вся ответственность лежит на пользователе."
        )
    },
    "ua": {
        "title": "Alt Manager v2",
        "nickname": "Нік акаунта",
        "add": "Додати акаунт",
        "login": "Увійти",
        "play": "Грати",
        "remove": "Видалити",
        "browser": "Браузер",
        "agree": "Погоджуюсь",
        "disc_title": "⚠️ Дисклеймер",
        "disc_text": (
            "Alt Manager v2 — допоміжний інструмент.\n\n"
            "Автор НЕ обходить системи Roblox.\n"
            "Автор НЕ несе відповідальності за блокування,\n"
            "втрати акаунтів або наслідки.\n\n"
            "Уся відповідальність лежить на користувачі."
        )
    }
}

def load_json(path, default=None):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return default if default is not None else {}

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def detect_language():
    loc = locale.getdefaultlocale()[0] or ""
    if loc.startswith("ru"):
        return "ru"
    if loc.startswith("uk"):
        return "ua"
    return "en"

class Star:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.x = random.uniform(0, w)
        self.y = random.uniform(0, h)
        self.speed = random.uniform(0.5, 1.5)
        self.size = random.choice([1, 2, 3])

    def update(self):
        self.y += self.speed
        if self.y > self.h:
            self.y = 0
            self.x = random.uniform(0, self.w)

class CosmosWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.stars = [Star(1200, 800) for _ in range(250)]
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(16)

    def paintEvent(self, e):
        p = QPainter(self)
        g = QLinearGradient(0, 0, 0, self.height())
        g.setColorAt(0, QColor(30, 60, 140))
        g.setColorAt(1, QColor(120, 50, 170))
        p.fillRect(self.rect(), g)
        p.setBrush(QColor(240,240,255))
        p.setPen(Qt.NoPen)
        for s in self.stars:
            s.update()
            p.drawEllipse(int(s.x), int(s.y), s.size, s.size)

class Disclaimer(QWidget):
    def __init__(self, lang):
        super().__init__()
        t = LANG[lang]
        self.accepted = False

        self.setFixedSize(520, 360)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        card = QWidget(self)
        card.setGeometry(0,0,520,360)
        card.setStyleSheet("background:rgba(15,23,42,245);border-radius:18px;")

        lay = QVBoxLayout(card)

        title = QLabel(t["disc_title"])
        title.setFont(QFont("Segoe UI Semibold", 22))
        title.setStyleSheet("color:#FACC15;")
        title.setAlignment(Qt.AlignCenter)
        lay.addWidget(title)

        text = QLabel(t["disc_text"])
        text.setWordWrap(True)
        text.setAlignment(Qt.AlignCenter)
        text.setStyleSheet("color:#E5E7EB;font-size:13px;")
        lay.addWidget(text)

        btn = QPushButton(t["agree"])
        btn.setEnabled(False)
        btn.clicked.connect(self.accept)
        lay.addWidget(btn, alignment=Qt.AlignCenter)

        QTimer.singleShot(2500, lambda: btn.setEnabled(True))

    def accept(self):
        self.accepted = True
        self.close()

class AltManager(QWidget):
    def __init__(self, lang):
        super().__init__()
        self.lang = lang
        self.browser = load_json(SETTINGS_FILE).get("browser","chrome")
        self.t = LANG[self.lang]
        self.accounts = load_json(DATA_FILE, [])

        self.setFixedSize(1000,700)
        self.setWindowTitle(self.t["title"])

        self.bg = CosmosWidget(self)
        self.bg.resize(self.size())

        self.init_ui()

    def init_ui(self):
        self.title = QLabel(self.t["title"], self)
        self.title.setFont(QFont("Segoe UI Semibold", 30))
        self.title.setStyleSheet("color:white;")
        self.title.move(350,40)

        self.card = QWidget(self)
        self.card.setGeometry(250,120,500,520)
        self.card.setStyleSheet("background:rgba(255,255,255,0.15);border-radius:18px;")
        lay = QVBoxLayout(self.card)

        self.lang_box = QComboBox()
        self.lang_box.addItems(["English","Русский","Українська"])
        self.lang_box.setCurrentIndex(["en","ru","ua"].index(self.lang))
        self.lang_box.currentIndexChanged.connect(self.change_language)
        lay.addWidget(self.lang_box)

        self.browser_label = QLabel(f"🌐 {self.t['browser']}")
        self.browser_label.setStyleSheet("color:white;font-weight:600;")
        lay.addWidget(self.browser_label)

        self.browser_box = QComboBox()
        self.browser_box.addItems([v[0] for v in BROWSERS.values()])
        self.browser_box.setCurrentIndex(list(BROWSERS.keys()).index(self.browser))
        self.browser_box.currentIndexChanged.connect(self.change_browser)
        lay.addWidget(self.browser_box)

        self.input = QLineEdit()
        lay.addWidget(self.input)

        self.btn_add = QPushButton()
        self.btn_add.clicked.connect(self.add_account)
        lay.addWidget(self.btn_add)

        self.list = QListWidget()
        self.list.addItems(self.accounts)
        lay.addWidget(self.list)

        self.btn_login = QPushButton()
        self.btn_login.clicked.connect(self.login)
        lay.addWidget(self.btn_login)

        self.btn_play = QPushButton()
        self.btn_play.clicked.connect(self.play)
        lay.addWidget(self.btn_play)

        self.btn_remove = QPushButton()
        self.btn_remove.clicked.connect(self.remove)
        lay.addWidget(self.btn_remove)

        self.refresh_ui()

    def refresh_ui(self):
        self.t = LANG[self.lang]
        self.setWindowTitle(self.t["title"])
        self.title.setText(self.t["title"])
        self.input.setPlaceholderText(self.t["nickname"])
        self.btn_add.setText(self.t["add"])
        self.btn_login.setText(self.t["login"])
        self.btn_play.setText(self.t["play"])
        self.btn_remove.setText(self.t["remove"])
        self.browser_label.setText(f"🌐 {self.t['browser']}")

    def change_language(self, i):
        self.lang = ["en","ru","ua"][i]
        save_json(SETTINGS_FILE, {"language":self.lang,"browser":self.browser})
        self.refresh_ui()

    def change_browser(self, i):
        self.browser = list(BROWSERS.keys())[i]
        save_json(SETTINGS_FILE, {"language":self.lang,"browser":self.browser})

    def open_url(self, url):
        item = self.list.currentItem()
        if not item: return
        profile = os.path.join(PROFILES_DIR, item.text())
        os.makedirs(profile, exist_ok=True)
        command = BROWSERS[self.browser][1].format(profile=profile, url=url)
        subprocess.Popen(command, shell=True)

    def login(self): self.open_url(ROBLOX_LOGIN)
    def play(self): self.open_url(ROBLOX_GAME)

    def add_account(self):
        name = self.input.text().strip()
        if name and name not in self.accounts:
            self.accounts.append(name)
            save_json(DATA_FILE, self.accounts)
            self.list.addItem(name)
            self.input.clear()

    def remove(self):
        item = self.list.currentItem()
        if item:
            self.accounts.remove(item.text())
            save_json(DATA_FILE, self.accounts)
            self.list.takeItem(self.list.row(item))

if __name__ == "__main__":
    settings = load_json(SETTINGS_FILE)
    lang = settings.get("language", detect_language())

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(15,23,42))
    palette.setColor(QPalette.Base, QColor(30,41,59))
    palette.setColor(QPalette.Text, QColor(248,250,252))
    palette.setColor(QPalette.ButtonText, QColor(248,250,252))
    app.setPalette(palette)

    disc = Disclaimer(lang)
    disc.show()
    app.exec()

    if not disc.accepted:
        sys.exit(0)

    window = AltManager(lang)
    window.show()
    sys.exit(app.exec())
