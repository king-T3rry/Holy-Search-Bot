import re
import io
import os
import json
import time
import string
import random
import hashlib
import sqlite3
import tempfile
import threading
import telebot
import requests
from datetime import datetime
from telebot import types
from urllib.parse import quote

# curl_cffi используется для обхода Cloudflare-челленджей (Turnstile/Just a moment...).
# Импорт делается безопасно: если библиотека недоступна, падаем обратно на requests.
try:
    from curl_cffi import requests as _cffireq
    _HAVE_CFFI = True
except Exception:
    _cffireq = None
    _HAVE_CFFI = False

BOT_TOKEN = "8896996894:AAELCsHANp2VdBTmrJFZIjdmp0X18e1dOIc"
OWNER_ID = 5277564584
REQUIRED_CHANNEL_ID = -1004447049309
REQUIRED_CHANNEL_URL = "https://t.me/+7DX76Z1638lmNmIy"
BOT_NAME = "лысеющий осинт"
BOT_AVATAR = "https://i.ibb.co/JWgpQ6vm/e2ab44606d9cff9043c678ec6e52acdc.jpg"
WHOLOGGER_API_KEY = "B5sXwumT4wXESCPw"
WHOLOGGER_BASE = "https://ff8bfb60b541ab.lhr.life/api"
DB_PATH = os.path.expanduser("~/.router_tempmail.db")
bot = telebot.TeleBot(BOT_TOKEN)


def setup_bot_profile():
    """Меняет название и аватарку бота при запуске."""
    try:
        bot.set_my_name(BOT_NAME)
    except Exception:
        pass
    try:
        r = requests.get(BOT_AVATAR, timeout=20)
        if r.status_code == 200 and r.content:
            bio = io.BytesIO(r.content)
            bio.name = "avatar.jpg"
            bot.set_my_photo(bio)
    except Exception:
        pass


setup_bot_profile()

pending_sub_msg = {}
pending_admin_actions = {}
USER_MAILS = {}
USER_PROXIES = {}

DEP_SEARCH_TOKEN = "OsMTcjyHTRtfABnWA4V3d12SYKVIYE8z"
DEP_SEARCH_BASE_URL = "https://api.depsearch.sbs"

HTMLWEB_URL = "https://htmlweb.ru/geo/api.php"

VK_APIS = [
    {
        "name": "vk_official",
        "type": "official",
        "url": "https://api.vk.com/method/users.get",
        "token": "0af157510af157510af15751aa0a89e69600af10af157516a0bc15996e74fe2b440998c",
        "v": "5.199",
        "fields": "first_name,last_name,bdate,city,country,contacts,online",
    },
    {
        "name": "vk_official_2",
        "type": "official",
        "url": "https://api.vk.com/method/users.get",
        "token": "b5d39265b5d39265b5d39265cdb6e3de12bb5d3b5d39265ddddf56e12bc803f6127721f",
        "v": "5.199",
        "fields": "first_name,last_name,bdate,city,country,contacts,online",
    },
    {"name": "looka",  "type": "raw", "url_tpl": "https://looka.one/vk_user/id{id}"},
    {"name": "220vk",   "type": "raw", "url_tpl": "https://v1.220vk.ru/{id}"},
    {"name": "murix",   "type": "raw", "url_tpl": "http://api.murix.ru/eye?v=5&user_id={id}"},
]

LEAKCHECK_KEY = "4344cd645b6e6cc2559c1a92017d9bfa12e4e4b1"
LEAKCHECK_URL = "https://leakcheck.io/api/public"

OFDATA_KEY = "KBnpz1CHKNngFXxK"
OFDATA_URL = "https://api.ofdata.ru/v2"

SHODAN_KEY = "i7SlTEgdEoz3aNPKn6tH7aHFKwqmPrPF"
SHODAN_URL = "https://api.shodan.io/shodan/host"

QUICKFLOW_TOKEN = "4df33bf63c1d4c1741544c8c47c8940f3c4fe4711a211910e5699aa148850b7e"
QUICKFLOW_URL = "https://api.quickflow.lat/get-user"

TON_URL = "https://toncenter.com/api/v3/transactions"

GITHUB_API = "https://api.github.com"

SIMILARFACES_BASE = "https://similarfaces.me"
SIMILARFACES_DETECT = f"{SIMILARFACES_BASE}/bff/detect-faces"
SIMILARFACES_SEARCH = f"{SIMILARFACES_BASE}/bff/search-faces"

SEARCH4FACES_BASE = "https://search4faces.com/"
SEARCH4FACES_UPLOAD = SEARCH4FACES_BASE + "assets/php/upload.php"
SEARCH4FACES_DETECT = SEARCH4FACES_BASE + "assets/php/detect.php"
SEARCH4FACES_REFERER = SEARCH4FACES_BASE + "search_vkwall.html"

PHOTO_PROFILE = "https://i.ibb.co/ccdr5Mbs/file-00000000ad6c720abf68a915bdf61af1.png"
PHOTO_SUBSCRIBE = "https://i.ibb.co/JwZQmM5C/file-000000008e0871f4a0454dac43808eb0.png"
PHOTO_PAYMENT = "https://i.ibb.co/v4dVYYdg/file-00000000bbd071f48fbabb096abb5f32.png"
PHOTO_API = "https://i.ibb.co/qhd2Z15/file-00000000b2f08210b6ac854ba713da97.png"
PHOTO_TOOLS = "https://i.ibb.co/Wpjp6VZP/file-00000000fffc820a8fcef58db558f18a.png"

# ── ГЕНЕРАТОР ИЗОБРАЖЕНИЙ ────────────────────────────────────────────────
def generate_image(prompt: str) -> bytes | None:
    """Генерирует изображение через Pollinations AI."""
    encoded = prompt.strip().replace(" ", "%20")
    url = (
        f"https://image.pollinations.ai/prompt/{encoded}"
        f"?width=1024&height=1024&model=flux&nologo=true"
    )
    try:
        r = requests.get(url, timeout=90)
        return r.content if r.status_code == 200 else None
    except Exception:
        return None


# ── JITLER API (с ротацией ключей) ───────────────────────────────────────
JITLER_URL = "https://api.jitler.top"
JITLER_KEYS = [
    "HrUckOUOYwgNsyfRj4Ug6VC6",
    "OOm8kHwpAAzqOnxqCVGMnUze",
    "T7jnzagUDGTVxirZh2W0uJ21",
    "ATxNTIayXZyNcySwwIktk5rk",
    "HkWHTajnIENWXpWNlTBdmaFP",
    "JPl3E4Ng68hyIyWnojUL8XxF",
    "2dnIR65njDpE06LEEt6vp3ne",
    "dhGe2dBgXI6eoXphtfe3MmAi",
    "tZymBIx0fO0WAP0fxsMRujC9",
    "cLxzgchdrkn5c4csQjpbZxzy",
    "njobd2pa5aQXef4iT08YXj1F",
    "lTP5J7TDmMSGuuQNKdh3Uqe3",
    "x2h0HoHWdCWj4jCuU82jQFdO",
    "2wwv4ZHQDDCrFoE4E9TqnjaP",
    "vwW3ltQcryvGSKr9r7IMvBnj",
    "kUULzKkHsZCqsKZyHEGi2z2M",
    "bC5eX8klnaW2PSdhnaHlARK1",
    "pGS8AA9dGzvru9fVULLYqZCC",
    "IcLCAwCwclupbXtFhDyErjaK",
    "YHT9bpgpNCEv88unmUYKmoNl",
    "0fr2o97Pat26Wkamc0V3ghXI",
    "njobd2pa5aQXef4iT08yxJ1F",
    "2DnIR65njdpE06LEEt6Vp3ne",
    "T7jnzaguDGTVxIrZh2W0uJ21",
    "tZymBIX0fO0WAP0fXsMRujC9",
    "x2h0HohWDCWj4jCuU82JQFdO",
    "2dnIR65nJDpE06LEET6vp3ne",
    "HrUckoUOYwgNsyfRj4UG6vC6",
    "HkWHtajNIENwXpWNlTBdmaFP",
    "pGs8AA9dGzVru9fvULLYqZCC",
    "0fr2o97Pat26Wkamc0V3gHXI",
    "VwW3ltQcryvGSKr9R7IMvBnj",
    "LtP5J7TDmMSGuuQNKdh3UQe3",
    "icLcAwCwclupbxtFhDyErjaK",
    "2wWv4zHQDDCrFoE4E9Tqnjap",
    "JPl3E4NG68hyIyWnojUL8Xxf",
    "T7jnzagUDGTvxirZh2w0uJ21",
    "IcLCAwCwClupbXtfhDyERjaK",
    "YHT9bpgpnCEv88unmUYKmonL",
    "vWW3ltQcryvgsKr9r7IMvBnj",
    "kUULZKKHsZCqsKZyHEGi2z2M",
    "vww3ltQcRyvGSKr9r7IMvBnj",
    "x2H0hoHWdCwj4jCuU82jQFdO",
    "dhge2dBgXI6eoXphtFe3mmAi",
    "JPl3E4Ng68hYIyWnojUL8XxF",
    "HKWHtajnIeNWXpWNlTBdmaFP",
    "IcLCAWCwcLupbXtFhDyErjak",
    "tZymBIx0fO0Wap0fxsMRujc9",
    "hruckOUOywgNsyfRj4Ug6VC6",
    "kUuLZKkHszCqsKZyHEGi2z2M",
    "2dnIR65njDpE06LEEt6Vp3ne",
    "njobd2pA5aQXEf4iT08yXj1F",
    "ATxNTiayXZyNCySwwIKtk5rk",
    "T7jnzaguDgTVxirZh2W0uJ21",
    "0fR2o97PaT26Wkamc0V3ghXI",
    "YHT9bPgpncEv88unmUYKmoNl",
    "cLxzgcHdrkn5c4csqjpBZxzy",
    "lTp5J7TDmMSGuuQNKDh3UQe3",
    "T7jnZAgUDGTVxirzh2W0uJ21",
    "cLxzgChdRkn5c4csQJpbZxzy",
    "dhGe2dBgXI6EoXpHtfE3MmAi",
    "IcLCAwCWclupbXtFHDyERjaK",
    "HkWHTajnIEnWXpWNlTBDmafP",
    "2wwv4ZHQdDCrFoE4E9TQnjAP",
    # старые ключи (оставляем как запасные)
    "KiiUkTvloUSZFICHHqu7rtmX",
    "bUpeLcJ7nYTWop2ImTP1AUpn",
    "uPwmUzeptpP1t2px1dxCRzlL",
    "BvaEs5TOr6D2cACDEvzOvIrY",
    "EeyX4bwmRXFUUcQ3cRWFs62T",
    "uSLyowqR9ZdKqlRlVnttRlEr",
    "PCOzeYxiwWqZlYCff9sJ3MlH",
    "V9QcBC8gzAkmYpejdojBMgm0",
    "zkXH2cJmgPJXoY8aXk4K04uD",
    "sxA5sNXez0tMjON7Vkv1ZMEr",
    "2iEwlmXn1JbPGaueA6GbFUOq",
    "KELpI4p9NgtaVyqjEDkeE1QH",
    "JkX2dO5ipP4G83AFk67eo0q6",
    "Xvh6UwdreZ4oZYgbf3dPHfIn",
    "nsjI57w4VZ2V4b5vTuVQ0eMo",
    "KRQwmQx1wRxGUF0ctCaIziCz",
    "TIJcr0hNZ2qnQ1JzD0ObDH4r",
    "KMwPxIDsHJaNHHVdQcRiyTKP",
    "ZokelLupErocmYZQYgwXtjeD",
    "qGBHWUHEGG08DupGx6KlpqxE",
    "vRxBgz9RR4W0CscU4K23Xhfp",
]
JITLER_CURRENT_KEY_INDEX = 0


class MultiJitler:
    def __init__(self, keys):
        self.keys = keys

    def search(self, stype, q):
        for key in self.keys:
            try:
                r = requests.post(
                    "https://api.jitler.top/search",
                    headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                    json={"type": stype, "query": q},
                    timeout=30
                )
                if r.status_code == 200:
                    data = r.json()
                    if "response" in data:
                        return data
            except Exception:
                continue
        return {"error": "Все ключи Jitler не работают"}


_multi_jitler = MultiJitler(JITLER_KEYS)


def jitler_search(search_type, query, page=1):
    """POST /search с автоматической ротацией ключей при 429/401/403."""
    global JITLER_CURRENT_KEY_INDEX
    max_retries = len(JITLER_KEYS)
    for _ in range(max_retries):
        key = JITLER_KEYS[JITLER_CURRENT_KEY_INDEX]
        try:
            r = requests.post(
                f"{JITLER_URL}/search",
                headers={
                    "Authorization": f"Bearer {key}",
                    "Content-Type": "application/json"
                },
                json={"type": search_type, "query": query, "page": page},
                timeout=20
            )
            if r.status_code == 200:
                return r.json()
            if r.status_code in (400, 401, 403, 429):
                JITLER_CURRENT_KEY_INDEX = (JITLER_CURRENT_KEY_INDEX + 1) % len(JITLER_KEYS)
                continue
            if r.status_code >= 500:
                JITLER_CURRENT_KEY_INDEX = (JITLER_CURRENT_KEY_INDEX + 1) % len(JITLER_KEYS)
                continue
        except Exception:
            JITLER_CURRENT_KEY_INDEX = (JITLER_CURRENT_KEY_INDEX + 1) % len(JITLER_KEYS)
            continue
    return {"result": False, "error": "Все ключи Jitler API исчерпаны или недоступны"}


def jitler_get_search_result(search_id):
    """GET /search/{id} с автоматической ротацией ключей."""
    global JITLER_CURRENT_KEY_INDEX
    max_retries = len(JITLER_KEYS)
    for _ in range(max_retries):
        key = JITLER_KEYS[JITLER_CURRENT_KEY_INDEX]
        try:
            r = requests.get(
                f"{JITLER_URL}/search/{search_id}",
                headers={"Authorization": f"Bearer {key}"},
                timeout=15
            )
            if r.status_code == 200:
                return r.json()
            if r.status_code in (400, 401, 403, 429):
                JITLER_CURRENT_KEY_INDEX = (JITLER_CURRENT_KEY_INDEX + 1) % len(JITLER_KEYS)
                continue
            if r.status_code >= 500:
                # 501 = задача ещё выполняется, не меняем ключ — ждём
                return r.json()
        except Exception:
            JITLER_CURRENT_KEY_INDEX = (JITLER_CURRENT_KEY_INDEX + 1) % len(JITLER_KEYS)
            continue
    return {"result": False, "error": "Все ключи Jitler API исчерпаны или недоступны"}


def jitler_search_with_wait(search_type, query, max_polls=12, sleep_sec=5):
    """Создаёт задачу и опрашивает результат до готовности.
    Возвращает финальный ответ Jitler API (dict).
    """
    resp = jitler_search(search_type, query)
    if not resp.get("result"):
        return resp
    # Если данные пришли сразу
    if "response" in resp:
        return resp
    # Иначе — это задача с id, опрашиваем
    search_id = resp.get("id")
    if not search_id:
        return resp
    for _ in range(max_polls):
        time.sleep(sleep_sec)
        result = jitler_get_search_result(search_id)
        if not result.get("result"):
            return result
        # Если пришёл ответ или пустой массив — задача завершена
        if "response" in result:
            return result
        # Если 501 / ошибка — продолжаем ждать
    return {"result": False, "error": "Таймаут ожидания результата Jitler API"}


USER_DATA = {}
FACE_RESULTS = {}


def safe_html(text):
    if not text:
        return ""
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def photo_preview(photo_url):
    try:
        return types.LinkPreviewOptions(
            url=photo_url,
            prefer_large_media=True,
            show_above_text=True
        )
    except Exception:
        return None


def quoted(text):
    return f"<blockquote>{text}</blockquote>"


def register_user_if_not_exists(user_id):
    if user_id not in USER_DATA:
        USER_DATA[user_id] = {
            "id": user_id,
            "subscription": "Premium",
            "requests_left": "∞",
            "reg_date": datetime.now().strftime("%d.%m.%Y")
        }


def get_profile_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_subscribe = types.InlineKeyboardButton("Оформить подписку", callback_data="menu_subscribe")
    btn_api = types.InlineKeyboardButton("API", callback_data="menu_api")
    btn_back = types.InlineKeyboardButton("‹ Вернуться", callback_data="menu_main")
    markup.add(btn_subscribe, btn_api)
    markup.add(btn_back)
    return markup


def get_subscribe_keyboard():
    markup = types.InlineKeyboardMarkup()
    btn_sub_30 = types.InlineKeyboardButton("30 Дней – 0₽ – 50 шт. в день", callback_data="sub_tar_30")
    btn_dummy = types.InlineKeyboardButton("— Дополнительные запросы —", callback_data="dummy")
    btn_pack1 = types.InlineKeyboardButton("15 – 0₽", callback_data="sub_pack_15")
    btn_pack2 = types.InlineKeyboardButton("50 – 0₽", callback_data="sub_pack_50")
    btn_pack3 = types.InlineKeyboardButton("120 – 0₽", callback_data="sub_pack_120")
    btn_pack4 = types.InlineKeyboardButton("120 – 0₽", callback_data="sub_pack_120_premium")
    btn_pack5 = types.InlineKeyboardButton("500 – 0₽", callback_data="sub_pack_500")
    btn_support = types.InlineKeyboardButton("Тех. поддержка", url="https://t.me/broadc0m")
    btn_back = types.InlineKeyboardButton("‹ Вернуться", callback_data="menu_profile")
    markup.add(btn_sub_30)
    markup.add(btn_dummy)
    markup.add(btn_pack1, btn_pack2)
    markup.add(btn_pack3, btn_pack4)
    markup.add(btn_pack5)
    markup.add(btn_support)
    markup.add(btn_back)
    return markup


def get_sub_pay_keyboard():
    markup = types.InlineKeyboardMarkup()
    btn_xrocket = types.InlineKeyboardButton("Xrocket", callback_data="buy_sub_xrocket")
    btn_cryptobot = types.InlineKeyboardButton("CryptoBot", callback_data="buy_sub_cryptobot")
    btn_sbp = types.InlineKeyboardButton("СПБ банковская карта", callback_data="buy_sub_sbp")
    btn_support = types.InlineKeyboardButton("Тех. поддержка", url="https://t.me/broadc0m")
    btn_back = types.InlineKeyboardButton("‹ Вернуться", callback_data="menu_subscribe")
    markup.row(btn_xrocket, btn_cryptobot)
    markup.add(btn_sbp)
    markup.add(btn_support)
    markup.add(btn_back)
    return markup


def get_api_keyboard():
    markup = types.InlineKeyboardMarkup()
    btn_basic = types.InlineKeyboardButton("Basic – $0 –\n150 запросов в день.", callback_data="api_tar_basic")
    btn_premium = types.InlineKeyboardButton("Premium – $0 –\n500 запросов в день.", callback_data="api_tar_premium")
    btn_back = types.InlineKeyboardButton("‹ Вернуться", callback_data="menu_profile")
    markup.add(btn_basic)
    markup.add(btn_premium)
    markup.add(btn_back)
    return markup


def get_api_pay_keyboard():
    markup = types.InlineKeyboardMarkup()
    btn_xrocket = types.InlineKeyboardButton("Xrocket", callback_data="buy_api_xrocket")
    btn_cryptobot = types.InlineKeyboardButton("CryptoBot", callback_data="buy_api_cryptobot")
    btn_sbp = types.InlineKeyboardButton("СПБ банковская карта", callback_data="buy_api_sbp")
    btn_support = types.InlineKeyboardButton("Тех. поддержка", url="https://t.me/broadc0m")
    btn_back = types.InlineKeyboardButton("‹ Вернуться", callback_data="menu_api")
    markup.row(btn_xrocket, btn_cryptobot)
    markup.add(btn_sbp)
    markup.add(btn_support)
    markup.add(btn_back)
    return markup


def get_main_keyboard():
    markup = types.InlineKeyboardMarkup()
    btn_profile = types.InlineKeyboardButton("Профиль", callback_data="menu_profile")
    btn_tools = types.InlineKeyboardButton("Инструменты", callback_data="menu_other")
    markup.add(btn_profile)
    markup.add(btn_tools)
    return markup


def get_other_menu():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Генератор фото", callback_data="menu_imagegen"))
    markup.add(types.InlineKeyboardButton("Временная почта", callback_data="menu_tempmail"))
    markup.add(types.InlineKeyboardButton("Прокси генератор", callback_data="menu_proxy"))
    markup.add(types.InlineKeyboardButton("IP Логгер", callback_data="menu_iplogger"))
    markup.add(types.InlineKeyboardButton("‹ Вернуться", callback_data="menu_main"))
    return markup


def get_tempmail_menu():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Создать почту", callback_data="tm_create"))
    markup.add(types.InlineKeyboardButton("Мои почты", callback_data="tm_list"))
    markup.add(types.InlineKeyboardButton("‹ Вернуться", callback_data="menu_other"))
    return markup


def init_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS mails (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, service TEXT, address TEXT, token TEXT, created_at TEXT)")
        conn.commit()
        conn.close()
    except Exception:
        pass


def save_mail_db(user_id, service, address, token):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO mails (user_id, service, address, token, created_at) VALUES (?,?,?,?,?)",
                       (user_id, service, address, token, datetime.now().isoformat()))
        conn.commit()
        conn.close()
    except Exception:
        pass


def get_mails_db(user_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, service, address, token FROM mails WHERE user_id=? ORDER BY id DESC", (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return [{"id": r[0], "service": r[1], "address": r[2], "token": r[3]} for r in rows]
    except Exception:
        return []


def delete_mail_db(mail_id, user_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM mails WHERE id=? AND user_id=?", (mail_id, user_id))
        conn.commit()
        conn.close()
    except Exception:
        pass


def generate_mailtm():
    try:
        r = requests.get("https://api.mail.tm/domains", timeout=8)
        if r.status_code != 200:
            return None
        domain = r.json()["hydra:member"][0]["domain"]
        username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        address = f"{username}@{domain}"
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
        requests.post("https://api.mail.tm/accounts", json={"address": address, "password": password}, timeout=8)
        tr = requests.post("https://api.mail.tm/token", json={"address": address, "password": password}, timeout=8)
        if tr.status_code == 200:
            token = tr.json().get("token")
            return {"service": "mailtm", "address": address, "token": token}
    except Exception:
        pass
    return None


def generate_guerrilla():
    try:
        r = requests.get("https://api.guerrillamail.com/ajax.php?f=get_email_address&lang=ru", timeout=8)
        if r.status_code == 200:
            data = r.json()
            address = data.get("email_addr")
            sid = data.get("sid_token")
            if address and sid:
                return {"service": "guerrilla", "address": address, "token": sid}
    except Exception:
        pass
    return None


def check_messages_mail(service, token):
    try:
        if service == "mailtm":
            headers = {"Authorization": f"Bearer {token}"}
            r = requests.get("https://api.mail.tm/messages", headers=headers, timeout=8)
            if r.status_code == 200:
                messages = r.json().get("hydra:member", [])
                return [{"id": m["id"], "from": m["from"]["address"], "subject": m.get("subject", "")} for m in messages]
        elif service == "guerrilla":
            r = requests.get(f"https://api.guerrillamail.com/ajax.php?f=get_email_list&lang=ru&offset=0&sid_token={token}", timeout=8)
            if r.status_code == 200:
                data = r.json()
                return [{"id": m["mail_id"], "from": m.get("mail_from", "—"), "subject": m.get("mail_subject", "")} for m in data.get("list", [])]
    except Exception:
        pass
    return []


def fetch_message_mail(service, token, msg_id):
    try:
        if service == "mailtm":
            headers = {"Authorization": f"Bearer {token}"}
            r = requests.get(f"https://api.mail.tm/messages/{msg_id}", headers=headers, timeout=8)
            if r.status_code == 200:
                return r.json().get("text", "Пустое письмо")
        elif service == "guerrilla":
            r = requests.get(f"https://api.guerrillamail.com/ajax.php?f=fetch_email&lang=ru&email_id={msg_id}&sid_token={token}", timeout=8)
            if r.status_code == 200:
                return r.json().get("mail_body", "Пустое письмо")
    except Exception:
        pass
    return None


def generate_proxies():
    proxies = []
    sources = [
        "https://freeproxydb.com/api/proxy/search?protocol=socks5&page_size=20",
        "https://freeproxydb.com/api/proxy/search?protocol=http&page_size=20",
        "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all"
    ]
    for url in sources:
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                if "freeproxydb" in url:
                    data = r.json()
                    for item in data.get("results", []):
                        ip = item.get("ip")
                        port = item.get("port")
                        if ip and port:
                            proxies.append(f"{ip}:{port}")
                else:
                    for line in r.text.strip().split("\n"):
                        if ":" in line:
                            proxies.append(line.strip())
        except Exception:
            continue
    proxies = list(set(proxies))
    return proxies


init_db()


WELCOME_TEXT = """«Router» - пришлите запрос в следующем формате

👤 Поиск по имени
└ Ильин Максим Сергеевич 12.04.1996

🌐 Социальные сети
├ @router – Телеграм
├ vk.com/@router – Вконтакте
├ ok.ru/profile/999 – Однокласн.
├ tiktok.com/@router – TikTok
└ instagram.com/router – Instagram

🗂 Документы
├ /vu 01234 – водительские права
├ /passport 0123 – номер паспорта
├ /snils 12345678901 – СНИЛС
├ /inn 123456789012 – ИНН 
├ /ogrn 1027700132195 – ОГРН 
├ /egrip 304500543000123 – ОГРНИП 
└ /company Сбербанк – название/ФИО

🚘 Поиск по авто
├ H777OH777 – номер автомобиля
└ XTA21150053965897 – VIN

🏠 Недвижимость
├ /adr Москва, Тверская,д1,кв1
└ 77:01:0001075:1361 – кадастровый номер

📞 +79991099999 – номер телефона
📪 tema@gmail.com – Email

💻 Доп. форматы
├ gh:nickname – GitHub аккаунт
├ id123456789 – VK ID
├ UQ... / EQ... – TON-кошелёк
└ 8.8.8.8 – IP-адрес 

📷 Отправьте фото — поиск по лицу"""


def send_menu_message(chat_id, text, photo_url, reply_markup):
    kwargs = {
        "chat_id": chat_id,
        "text": quoted(text),
        "reply_markup": reply_markup,
        "parse_mode": "HTML",
    }
    if photo_url:
        preview = photo_preview(photo_url)
        if preview is not None:
            kwargs["link_preview_options"] = preview
        else:
            kwargs["disable_web_page_preview"] = True
    else:
        kwargs["disable_web_page_preview"] = True
    bot.send_message(**kwargs)


def edit_menu_message(chat_id, message_id, text, photo_url, reply_markup):
    kwargs = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": quoted(text),
        "reply_markup": reply_markup,
        "parse_mode": "HTML",
    }
    if photo_url:
        preview = photo_preview(photo_url)
        if preview is not None:
            kwargs["link_preview_options"] = preview
        else:
            kwargs["disable_web_page_preview"] = True
    else:
        kwargs["disable_web_page_preview"] = True
    bot.edit_message_text(**kwargs)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    register_user_if_not_exists(message.from_user.id)
    # Владелец всегда видит меню без проверки подписки
    if message.from_user.id != OWNER_ID and not require_subscription(message.from_user.id, message.chat.id):
        return
    bot.send_message(
        chat_id=message.chat.id,
        text=quoted(WELCOME_TEXT),
        reply_markup=get_main_keyboard(),
        parse_mode="HTML",
        disable_web_page_preview=True
    )


@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    user_id = call.from_user.id
    register_user_if_not_exists(user_id)
    user_info = USER_DATA[user_id]

    if call.data == "menu_main":
        try:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=quoted(WELCOME_TEXT),
                reply_markup=get_main_keyboard(),
                parse_mode="HTML",
                disable_web_page_preview=True
            )
        except Exception:
            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
            except Exception:
                pass
            bot.send_message(
                chat_id=call.message.chat.id,
                text=quoted(WELCOME_TEXT),
                reply_markup=get_main_keyboard(),
                parse_mode="HTML",
                disable_web_page_preview=True
            )

    elif call.data == "menu_profile":
        profile_text = f"""<b>Профиль</b>

<b>ID:</b> <code>{user_info['id']}</code>
<b>Подписка:</b> <code>{user_info['subscription']}</code>
<b>Доступно запросов:</b> <code>{user_info['requests_left']}</code>
<b>Дата регистрации:</b> <code>{user_info['reg_date']}</code>"""
        try:
            edit_menu_message(
                call.message.chat.id,
                call.message.message_id,
                profile_text,
                "",
                get_profile_keyboard()
            )
        except Exception:
            pass

    elif call.data == "menu_api":
        api_text = "<b>Выберите интересующий тарифный план API для подключения:</b>"
        try:
            edit_menu_message(
                call.message.chat.id,
                call.message.message_id,
                api_text,
                PHOTO_API,
                get_api_keyboard()
            )
        except Exception:
            pass

    elif call.data in ["api_tar_basic", "api_tar_premium"]:
        pay_text = "Способ оплаты"
        try:
            edit_menu_message(
                call.message.chat.id,
                call.message.message_id,
                pay_text,
                PHOTO_PAYMENT,
                get_api_pay_keyboard()
            )
        except Exception:
            pass

    elif call.data == "menu_subscribe":
        sub_text = """<b>— С активной подпиской бот возвращает полные результаты поиска, включая все найденные совпадения и связанные данные.

— Дополнительные запросы не сгорают и не тратятся после дневного лимита.</b>"""
        try:
            edit_menu_message(
                call.message.chat.id,
                call.message.message_id,
                sub_text,
                PHOTO_SUBSCRIBE,
                get_subscribe_keyboard()
            )
        except Exception:
            pass

    elif call.data == "sub_tar_30" or call.data.startswith("sub_pack_"):
        pay_text = "Способ оплаты"
        try:
            edit_menu_message(
                call.message.chat.id,
                call.message.message_id,
                pay_text,
                PHOTO_PAYMENT,
                get_sub_pay_keyboard()
            )
        except Exception:
            pass

    elif call.data.startswith("face_prev_"):
        try:
            cur = int(call.data.replace("face_prev_", ""))
        except ValueError:
            cur = 0
        new_idx = max(0, cur - 1)
        cards = FACE_RESULTS.get(user_id, [])
        if not cards:
            bot.answer_callback_query(call.id, text="Сессия истекла. Повторите поиск.", show_alert=True)
            return
        edit_face_card_inplace(call.message.chat.id, call.message.message_id, user_id, index=new_idx)

    elif call.data.startswith("face_next_"):
        try:
            cur = int(call.data.replace("face_next_", ""))
        except ValueError:
            cur = 0
        cards = FACE_RESULTS.get(user_id, [])
        if not cards:
            bot.answer_callback_query(call.id, text="Сессия истекла. Повторите поиск.", show_alert=True)
            return
        new_idx = min(len(cards) - 1, cur + 1)
        edit_face_card_inplace(call.message.chat.id, call.message.message_id, user_id, index=new_idx)

    elif call.data == "menu_imagegen":
        prompt_text = (
            "<b>Генератор фото</b>\n\n"
            "Введите промпт для генерации изображения.\n\n"
            "<i>Пишите на англ. для лучшего качества.</i>"
        )
        try:
            bot.edit_message_text(
                prompt_text,
                call.message.chat.id,
                call.message.message_id,
                reply_markup=_imagegen_back_kb(),
                parse_mode="HTML",
                disable_web_page_preview=True,
            )
            sent = call.message
        except Exception:
            # если сообщение медиа — редактировать нельзя, шлём новое
            sent = bot.send_message(
                call.message.chat.id,
                prompt_text,
                reply_markup=_imagegen_back_kb(),
                parse_mode="HTML",
                disable_web_page_preview=True,
            )
        bot.register_next_step_handler(sent, _imagegen_process)

    elif call.data == "menu_other":
        other_text = "<b>Инструменты</b>\n\nВыберите раздел:"
        try:
            edit_menu_message(call.message.chat.id, call.message.message_id, other_text, PHOTO_TOOLS, get_other_menu())
        except Exception:
            # Если сообщение — фото или медиа, нельзя edit_message_text
            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
            except Exception:
                pass
            send_menu_message(call.message.chat.id, other_text, PHOTO_TOOLS, get_other_menu())

    elif call.data == "menu_tempmail":
        try:
            edit_menu_message(call.message.chat.id, call.message.message_id,
                              "<b>Временная почта</b>\n\nСоздайте одноразовый ящик и принимайте письма без раскрытия реального адреса.",
                              PHOTO_TOOLS, get_tempmail_menu())
        except Exception:
            pass

    elif call.data == "tm_create":
        bot.send_chat_action(call.message.chat.id, 'typing')
        m = generate_mailtm()
        if not m:
            m = generate_guerrilla()
        if not m:
            bot.answer_callback_query(call.id, text="❌ Не удалось создать почту. Попробуйте позже.", show_alert=True)
            return
        save_mail_db(call.from_user.id, m["service"], m["address"], m["token"])
        text = (f"<b>✅ Почта создана</b>\n\n"
                f"<b>Сервис:</b> <code>{safe_html(m['service'])}</code>\n"
                f"<b>Адрес:</b> <code>{safe_html(m['address'])}</code>")
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📥 Проверить входящие", callback_data="tm_list"))
        markup.add(types.InlineKeyboardButton("‹ Назад", callback_data="menu_tempmail"))
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception:
            pass
        send_menu_message(call.message.chat.id, text, PHOTO_TOOLS, markup)

    elif call.data == "tm_list":
        mails = get_mails_db(call.from_user.id)
        if not mails:
            bot.answer_callback_query(call.id, text="У вас пока нет созданных почт.", show_alert=True)
            return
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception:
            pass
        markup = types.InlineKeyboardMarkup()
        for m in mails[:10]:
            label = f"📬 {m['address']} ({m['service']})"
            markup.add(types.InlineKeyboardButton(label, callback_data=f"tm_check_{m['id']}"))
        markup.add(types.InlineKeyboardButton("‹ Назад", callback_data="menu_tempmail"))
        bot.send_message(call.message.chat.id, "<b>Ваши почты</b> (нажмите для проверки входящих):",
                         parse_mode="HTML", reply_markup=markup, disable_web_page_preview=True)

    elif call.data.startswith("tm_check_"):
        try:
            mail_id = int(call.data.replace("tm_check_", ""))
        except ValueError:
            return
        mails = get_mails_db(call.from_user.id)
        target = next((m for m in mails if m["id"] == mail_id), None)
        if not target:
            bot.answer_callback_query(call.id, text="Почта не найдена.", show_alert=True)
            return
        bot.send_chat_action(call.message.chat.id, 'typing')
        msgs = check_messages_mail(target["service"], target["token"])
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception:
            pass
        if not msgs:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton(" Обновить", callback_data=f"tm_check_{mail_id}"))
            markup.add(types.InlineKeyboardButton(" Удалить", callback_data=f"tm_del_{mail_id}"))
            markup.add(types.InlineKeyboardButton("‹ Назад", callback_data="tm_list"))
            bot.send_message(call.message.chat.id, f"<b>{safe_html(target['address'])}</b>\n\nВходящих нет.",
                             parse_mode="HTML", reply_markup=markup, disable_web_page_preview=True)
            return
        markup = types.InlineKeyboardMarkup()
        for i, m in enumerate(msgs[:15], 1):
            label = f"📨 {i}. {m['subject'][:40]} — {m['from'][:30]}"
            markup.add(types.InlineKeyboardButton(label, callback_data=f"tm_read_{mail_id}_{m['id']}"))
        markup.add(types.InlineKeyboardButton("Удалить почту", callback_data=f"tm_del_{mail_id}"))
        markup.add(types.InlineKeyboardButton("‹ Назад", callback_data="tm_list"))
        bot.send_message(call.message.chat.id, f"<b>{safe_html(target['address'])}</b> — {len(msgs)} писем:",
                         parse_mode="HTML", reply_markup=markup, disable_web_page_preview=True)

    elif call.data.startswith("tm_read_"):
        parts = call.data.replace("tm_read_", "").split("_", 1)
        if len(parts) != 2:
            return
        mail_id, msg_id = parts
        mails = get_mails_db(call.from_user.id)
        target = next((m for m in mails if str(m["id"]) == mail_id), None)
        if not target:
            bot.answer_callback_query(call.id, text="Почта не найдена.", show_alert=True)
            return
        bot.send_chat_action(call.message.chat.id, 'typing')
        content = fetch_message_mail(target["service"], target["token"], msg_id)
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception:
            pass
        if content:
            text = content[:3500]
            if len(content) > 3500:
                text += "\n\n... (обрезано)"
        else:
            text = "Не удалось прочитать письмо."
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("‹ Назад к списку", callback_data=f"tm_check_{mail_id}"))
        bot.send_message(call.message.chat.id, f"<b>Письмо</b>\n\n{safe_html(text)}",
                         parse_mode="HTML", reply_markup=markup, disable_web_page_preview=True)

    elif call.data.startswith("tm_del_"):
        try:
            mail_id = int(call.data.replace("tm_del_", ""))
        except ValueError:
            return
        delete_mail_db(mail_id, call.from_user.id)
        bot.answer_callback_query(call.id, text=" Почта удалена")
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception:
            pass
        mails = get_mails_db(call.from_user.id)
        if not mails:
            bot.send_message(call.message.chat.id, "У вас больше нет почт.",
                             reply_markup=get_tempmail_menu(), disable_web_page_preview=True)
        else:
            markup = types.InlineKeyboardMarkup()
            for m in mails[:10]:
                label = f"{m['address']} ({m['service']})"
                markup.add(types.InlineKeyboardButton(label, callback_data=f"tm_check_{m['id']}"))
            markup.add(types.InlineKeyboardButton("‹ Назад", callback_data="menu_tempmail"))
            bot.send_message(call.message.chat.id, "<b>Ваши почты</b>:",
                             parse_mode="HTML", reply_markup=markup, disable_web_page_preview=True)

    elif call.data == "menu_proxy":
        bot.send_chat_action(call.message.chat.id, 'typing')
        def _do():
            proxies = generate_proxies()
            if not proxies:
                send_menu_message(call.message.chat.id, "Не удалось собрать прокси. Попробуйте позже.",
                                  PHOTO_TOOLS, get_other_menu())
                return
            content = "\n".join(proxies)
            file_stream = io.BytesIO(content.encode("utf-8"))
            file_stream.name = f"proxies_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("‹ Назад", callback_data="menu_other"))
            bot.send_document(call.message.chat.id, file_stream,
                              caption=f"Найдено прокси: {len(proxies)}",
                              reply_markup=markup)
        threading.Thread(target=_do, daemon=True).start()

    elif call.data == "check_sub":
        # Проверка подписки по кнопке «Проверить»
        # handle_query перехватывает ВСЕ колбэки раньше cb_check_sub,
        # поэтому обрабатываем здесь
        if call.from_user.id == OWNER_ID or check_subscription(call.from_user.id):
            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
            except Exception:
                pass
            if call.message.chat.id in pending_sub_msg:
                del pending_sub_msg[call.message.chat.id]
            bot.send_message(
                call.message.chat.id,
                quoted(WELCOME_TEXT),
                reply_markup=get_main_keyboard(),
                parse_mode="HTML",
                disable_web_page_preview=True
            )
            bot.answer_callback_query(call.id, "✅ Подписка подтверждена")
        else:
            bot.answer_callback_query(
                call.id,
                "Вы ещё не подписались на канал",
                show_alert=True
            )

    elif call.data == "dummy":
        bot.answer_callback_query(call.id, text="")

    elif call.data == "menu_iplogger":
        uid = call.from_user.id
        stored = IPLOGGER_STORE.get(uid)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🆕 Создать новый логгер", callback_data="iplog_create"))
        if stored:
            markup.add(types.InlineKeyboardButton("📋 Получить логи", callback_data="iplog_getlogs"))
        markup.add(types.InlineKeyboardButton("‹ Назад", callback_data="menu_other"))

        text = "<b>IP Логгер (unwork)</b>\n\nСоздай ссылку — когда кто-то откроет её, ты получишь его IP, устройство и страну."
        if stored:
            text += f"\n\n<b>Активный логгер:</b>\n🔗 <code>{stored['url']}</code>"
        try:
            edit_menu_message(call.message.chat.id, call.message.message_id,
                              text, PHOTO_TOOLS, markup)
        except Exception:
            send_menu_message(call.message.chat.id, text, PHOTO_TOOLS, markup)

    elif call.data == "iplog_create":
        bot.answer_callback_query(call.id, text="Создаю логгер...")
        uid = call.from_user.id

        def _create():
            result = iplogger_create()
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("📋 Получить логи", callback_data="iplog_getlogs"))
            markup.add(types.InlineKeyboardButton("‹ Назад", callback_data="menu_iplogger"))

            if "error" in result:
                bot.send_message(call.message.chat.id,
                                 f"❌ Ошибка создания логгера:\n<code>{safe_html(result['error'])}</code>",
                                 parse_mode="HTML", reply_markup=markup,
                                 disable_web_page_preview=True)
                return

            log_hash = result["hash"]
            full_url = result["full_url"]
            IPLOGGER_STORE[uid] = {"hash": log_hash, "url": full_url}

            text = (
                f"<b>✅ Логгер создан!</b>\n\n"
                f"🔗 <b>Ссылка для жертвы:</b>\n"
                f"<code>{full_url}</code>\n\n"
                f"📎 <b>Хэш:</b> <code>{log_hash}</code>\n\n"
                f"<i>Отправь эту ссылку — и получишь IP всех кто откроет её.</i>"
            )
            bot.send_message(call.message.chat.id, text, parse_mode="HTML",
                             reply_markup=markup, disable_web_page_preview=True)

        threading.Thread(target=_create, daemon=True).start()

    elif call.data == "iplog_getlogs":
        uid = call.from_user.id
        stored = IPLOGGER_STORE.get(uid)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔄 Обновить", callback_data="iplog_getlogs"))
        markup.add(types.InlineKeyboardButton("🆕 Новый логгер", callback_data="iplog_create"))
        markup.add(types.InlineKeyboardButton("‹ Назад", callback_data="menu_iplogger"))

        if not stored:
            bot.answer_callback_query(call.id, "Сначала создай логгер", show_alert=True)
            return

        bot.answer_callback_query(call.id, text="Загружаю логи...")

        def _getlogs():
            result = iplogger_get_logs(stored["hash"])

            if "error" in result:
                bot.send_message(call.message.chat.id,
                                 f"❌ Ошибка получения логов:\n<code>{safe_html(result['error'])}</code>",
                                 parse_mode="HTML", reply_markup=markup,
                                 disable_web_page_preview=True)
                return

            logs = result.get("logs") or result.get("data") or []

            if not logs:
                text = (
                    f"<b>📋 Логи логгера</b>\n"
                    f"🔗 <code>{stored['url']}</code>\n\n"
                    f"<i>Пока никто не открыл ссылку.</i>"
                )
                bot.send_message(call.message.chat.id, text, parse_mode="HTML",
                                 reply_markup=markup, disable_web_page_preview=True)
                return

            lines = [f"<b>📋 Логи ({len(logs)} визитов)</b>\n"]
            for i, entry in enumerate(logs[:20], 1):
                ip      = entry.get("ip") or entry.get("IP") or "—"
                ua      = entry.get("user_agent") or entry.get("useragent") or entry.get("ua") or "—"
                country = entry.get("country") or entry.get("Country") or "—"
                city    = entry.get("city") or entry.get("City") or ""
                ts      = entry.get("time") or entry.get("timestamp") or entry.get("created_at") or "—"
                loc     = f"{country}" + (f", {city}" if city else "")
                lines.append(
                    f"<b>#{i}</b>\n"
                    f"  🌐 IP: <code>{ip}</code>\n"
                    f"  📍 Локация: {loc}\n"
                    f"  🕐 Время: {ts}\n"
                    f"  📱 UA: <code>{safe_html(str(ua)[:80])}</code>"
                )

            if len(logs) > 20:
                lines.append(f"\n<i>... и ещё {len(logs)-20} визитов</i>")

            text = "\n\n".join(lines)
            if len(text) > 4096:
                text = text[:4090] + "…"

            bot.send_message(call.message.chat.id, text, parse_mode="HTML",
                             reply_markup=markup, disable_web_page_preview=True)

        threading.Thread(target=_getlogs, daemon=True).start()

    elif call.data.startswith("buy_"):
        bot.answer_callback_query(call.id, text="Успешно ✅️", show_alert=True)


def _imagegen_back_kb():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("‹ Назад", callback_data="menu_other"))
    return markup


# ── IP ЛОГГЕР (whologger API) ─────────────────────────────────────────────
IPLOGGER_STORE = {}   # user_id -> {"hash": ..., "url": ...}

def iplogger_create() -> dict:
    """Создать новый логгер."""
    try:
        r = requests.get(
            f"{WHOLOGGER_BASE}/{WHOLOGGER_API_KEY}/create_logg",
            timeout=15,
            headers={"Accept": "application/json"}
        )
        raw = r.text.strip()
        if not raw:
            return {"error": f"Пустой ответ от сервера (HTTP {r.status_code})"}
        try:
            data = r.json()
        except Exception:
            return {"error": f"Не JSON: {raw[:200]}"}
        if "hash" in data and "full_url" in data:
            return data
        return {"error": data.get("error", f"Неожиданный ответ: {raw[:200]}")}
    except requests.exceptions.ConnectionError:
        return {"error": "Сервер логгера недоступен (Connection refused)"}
    except Exception as e:
        return {"error": str(e)}


def iplogger_get_logs(log_hash: str) -> dict:
    """Получить логи по хэшу."""
    try:
        r = requests.get(
            f"{WHOLOGGER_BASE}/{WHOLOGGER_API_KEY}/get_logs/{log_hash}",
            timeout=15,
            headers={"Accept": "application/json"}
        )
        raw = r.text.strip()
        if not raw:
            return {"error": f"Пустой ответ (HTTP {r.status_code})"}
        try:
            return r.json()
        except Exception:
            return {"error": f"Не JSON: {raw[:200]}"}
    except requests.exceptions.ConnectionError:
        return {"error": "Сервер логгера недоступен"}
    except Exception as e:
        return {"error": str(e)}


def _imagegen_process(message):
    """Обрабатывает промпт пользователя и генерирует изображение."""
    chat_id = message.chat.id

    if not message.text or message.text.startswith("/"):
        return

    prompt = message.text.strip()
    if not prompt:
        bot.send_message(chat_id, "Промпт не может быть пустым.")
        return

    wait_msg = bot.send_message(chat_id, "🎨 Генерация фото... (до 90 секунд)")

    def _do():
        img_data = generate_image(prompt)
        try:
            bot.delete_message(chat_id, wait_msg.message_id)
        except Exception:
            pass

        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔄 Сгенерировать ещё", callback_data="menu_imagegen"))
        markup.add(types.InlineKeyboardButton("‹ Назад", callback_data="menu_other"))

        if img_data:
            bio = io.BytesIO(img_data)
            bio.name = "image.jpg"
            caption = (
                f"<b>🎨 Готово!</b>\n\n"
                f"<b>Промпт:</b> <code>{safe_html(prompt)}</code>"
            )
            bot.send_photo(
                chat_id, bio,
                caption=caption,
                parse_mode="HTML",
                reply_markup=markup
            )
        else:
            text = "❌ Не удалось сгенерировать фото. Попробуйте другой промпт."
            send_menu_message(chat_id, text, PHOTO_TOOLS, markup)

    threading.Thread(target=_do, daemon=True).start()


def status_animation(chat_id):
    msg = bot.send_message(chat_id, "Проверяем базы", disable_web_page_preview=True)
    time.sleep(1.2)
    try:
        bot.edit_message_text(chat_id=chat_id, message_id=msg.message_id, text="Сверяем данные", disable_web_page_preview=True)
    except Exception:
        pass
    return msg


def finish_status_animation(chat_id, msg_id):
    try:
        bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text="Готово", disable_web_page_preview=True)
        time.sleep(0.5)
        bot.delete_message(chat_id, msg_id)
    except Exception:
        pass


def _safe_json(resp):
    """Парсит ответ как JSON. Возвращает ровно то, что прислал сервер
    (включая JSON-тела ошибок Cloudflare и т.п.). Если JSON-парсинг не удался —
    отдаёт сырой текст под ключом "raw"."""
    try:
        return resp.json()
    except Exception:
        return {"raw": (resp.text or "")[:1000]}


def _cffi_get(url, headers=None, timeout=30):
    """GET-запрос через curl_cffi с имперсонацией Safari iOS — обходит
    Cloudflare-челленджи (Just a moment... / Turnstile), которые блокируют
    обычный requests. Если curl_cffi недоступен — откатывается на requests."""
    if _HAVE_CFFI:
        try:
            return _cffireq.get(url, impersonate="safari17_2_ios",
                                headers=headers or {}, timeout=timeout)
        except Exception:
            pass
    return requests.get(url, headers=headers or {}, timeout=timeout)


def call_depsearch(query):
    """DepSearch через Cloudflare. Всегда возвращает сырой JSON-ответ
    сервера как есть (без обёртки в {"error": ...})."""
    try:
        encoded_q = quote(str(query), safe="")
        url = f"{DEP_SEARCH_BASE_URL}/quest={encoded_q}&token={DEP_SEARCH_TOKEN}&lang=ru"
        r = _cffi_get(url, timeout=30,
                      headers={
                          "Accept": "application/json, text/javascript, */*; q=0.01",
                          "Accept-Language": "ru-RU,ru;q=0.9",
                          "X-Requested-With": "XMLHttpRequest",
                      })
        return _safe_json(r)
    except Exception as e:
        return {"error": str(e)}



def call_htmlweb_geo(phone):
    try:
        url = f"{HTMLWEB_URL}?json&telcod={phone}"
        r = requests.get(url, timeout=10)
        return _safe_json(r)
    except Exception as e:
        return {"error": str(e)}


def call_leakcheck(query):
    try:
        url = f"{LEAKCHECK_URL}?check={query}"
        headers = {"X-API-Key": LEAKCHECK_KEY}
        r = requests.get(url, headers=headers, timeout=10)
        return _safe_json(r)
    except Exception as e:
        return {"error": str(e)}


def call_ofdata(query):
    try:
        inn = re.sub(r'\D', '', str(query))
        if not inn or len(inn) not in (10, 12):
            return {"error": "ofdata требует корректный ИНН (10 или 12 цифр)", "raw_query": str(query)}
        endpoint = "company" if len(inn) == 10 else "entrepreneur"
        url = f"{OFDATA_URL}/{endpoint}?key={OFDATA_KEY}&inn={inn}"
        r = requests.get(url, timeout=10)
        return _safe_json(r)
    except Exception as e:
        return {"error": str(e)}


def call_ofdata_company_by_inn(inn):
    try:
        inn = re.sub(r'\D', '', str(inn))
        if len(inn) != 10:
            return {"error": "ИНН юр.лица должен содержать 10 цифр", "raw_query": str(inn)}
        url = f"{OFDATA_URL}/company?key={OFDATA_KEY}&inn={inn}"
        r = requests.get(url, timeout=10)
        return _safe_json(r)
    except Exception as e:
        return {"error": str(e)}


def call_ofdata_company_by_ogrn(ogrn):
    try:
        ogrn = re.sub(r'\D', '', str(ogrn))
        if len(ogrn) != 13:
            return {"error": "ОГРН должен содержать 13 цифр", "raw_query": str(ogrn)}
        url = f"{OFDATA_URL}/company?key={OFDATA_KEY}&ogrn={ogrn}"
        r = requests.get(url, timeout=10)
        return _safe_json(r)
    except Exception as e:
        return {"error": str(e)}


def call_ofdata_entrepreneur_by_inn(inn):
    try:
        inn = re.sub(r'\D', '', str(inn))
        if len(inn) != 12:
            return {"error": "ИНН ИП должен содержать 12 цифр", "raw_query": str(inn)}
        url = f"{OFDATA_URL}/entrepreneur?key={OFDATA_KEY}&inn={inn}"
        r = requests.get(url, timeout=10)
        return _safe_json(r)
    except Exception as e:
        return {"error": str(e)}


def call_ofdata_entrepreneur_by_ogrn(ogrnip):
    try:
        ogrnip = re.sub(r'\D', '', str(ogrnip))
        if len(ogrnip) != 15:
            return {"error": "ОГРНИП должен содержать 15 цифр", "raw_query": str(ogrnip)}
        url = f"{OFDATA_URL}/entrepreneur?key={OFDATA_KEY}&ogrn={ogrnip}"
        r = requests.get(url, timeout=10)
        return _safe_json(r)
    except Exception as e:
        return {"error": str(e)}


def call_ofdata_search(name, obj="org"):
    try:
        name = str(name).strip()
        if len(name) < 4:
            return {"error": "Минимум 4 символа для поиска по наименованию", "raw_query": name}
        url = (f"{OFDATA_URL}/search?key={OFDATA_KEY}"
               f"&by=name&obj={obj}&query={quote(name)}&limit=20")
        r = requests.get(url, timeout=10)
        return _safe_json(r)
    except Exception as e:
        return {"error": str(e)}


def call_shodan(ip):
    try:
        url = f"{SHODAN_URL}/{ip}?key={SHODAN_KEY}"
        r = requests.get(url, timeout=15)
        return _safe_json(r)
    except Exception as e:
        return {"error": str(e)}


def call_quickflow(tg_id):
    try:
        url = f"{QUICKFLOW_URL}?id={tg_id}&token={QUICKFLOW_TOKEN}"
        r = requests.get(url, timeout=10)
        return _safe_json(r)
    except Exception as e:
        return {"error": str(e)}


def call_ton(address):
    try:
        url = f"{TON_URL}?account={address}&limit=50"
        r = requests.get(url, timeout=15)
        return _safe_json(r)
    except Exception as e:
        return {"error": str(e)}


def call_vk_api(api_def, vk_id):
    try:
        if api_def.get("type") == "official":
            url = api_def["url"]
            params = {
                "user_ids": vk_id,
                "access_token": api_def["token"],
                "v": api_def["v"],
                "fields": api_def["fields"],
            }
            r = requests.get(url, params=params, timeout=10)
            return _safe_json(r)
        else:
            url = api_def["url_tpl"].format(id=vk_id)
            r = requests.get(url, timeout=10)
            return _safe_json(r)
    except Exception as e:
        return {"error": str(e)}


def call_github_user(nickname):
    try:
        url = f"{GITHUB_API}/users/{nickname}"
        r = requests.get(url, timeout=10, headers={"Accept": "application/vnd.github+json"})
        return _safe_json(r)
    except Exception as e:
        return {"error": str(e)}


def call_github_repos(nickname):
    try:
        url = f"{GITHUB_API}/users/{nickname}/repos?per_page=100&sort=updated"
        r = requests.get(url, timeout=10, headers={"Accept": "application/vnd.github+json"})
        return _safe_json(r)
    except Exception as e:
        return {"error": str(e)}


def call_github_gists(nickname):
    try:
        url = f"{GITHUB_API}/users/{nickname}/gists?per_page=100"
        r = requests.get(url, timeout=10, headers={"Accept": "application/vnd.github+json"})
        return _safe_json(r)
    except Exception as e:
        return {"error": str(e)}


def call_github_events(nickname):
    try:
        url = f"{GITHUB_API}/users/{nickname}/events/public?per_page=100"
        r = requests.get(url, timeout=10, headers={"Accept": "application/vnd.github+json"})
        return _safe_json(r)
    except Exception as e:
        return {"error": str(e)}


def call_github_orgs(nickname):
    try:
        url = f"{GITHUB_API}/users/{nickname}/orgs"
        r = requests.get(url, timeout=10, headers={"Accept": "application/vnd.github+json"})
        return _safe_json(r)
    except Exception as e:
        return {"error": str(e)}


def call_github_starred(nickname):
    try:
        url = f"{GITHUB_API}/users/{nickname}/starred?per_page=100"
        r = requests.get(url, timeout=10, headers={"Accept": "application/vnd.github+json"})
        return _safe_json(r)
    except Exception as e:
        return {"error": str(e)}


def call_github_followers(nickname):
    try:
        url = f"{GITHUB_API}/users/{nickname}/followers?per_page=100"
        r = requests.get(url, timeout=10, headers={"Accept": "application/vnd.github+json"})
        return _safe_json(r)
    except Exception as e:
        return {"error": str(e)}


def call_github_following(nickname):
    try:
        url = f"{GITHUB_API}/users/{nickname}/following?per_page=100"
        r = requests.get(url, timeout=10, headers={"Accept": "application/vnd.github+json"})
        return _safe_json(r)
    except Exception as e:
        return {"error": str(e)}


def detect_query_type(text):
    text = text.strip()

    clean_phone = re.sub(r'[^\d+]', '', text)
    is_phone = False
    if clean_phone.startswith('+') and clean_phone[1:].isdigit() and len(clean_phone) >= 11:
        is_phone = True
    elif (clean_phone.startswith('7') or clean_phone.startswith('8')) and len(clean_phone) == 11:
        is_phone = True

    ip_pattern = r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$'
    m_ip = re.match(ip_pattern, text)
    is_ip = False
    if m_ip and all(0 <= int(p) <= 255 for p in m_ip.groups()):
        is_ip = True

    is_tg_username = text.startswith('@') and len(text) > 1 and not any(c.isspace() for c in text)

    is_tg_id = text.isdigit() and 5 <= len(text) <= 15

    is_email = bool(re.match(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$', text))

    is_vk_id = False
    vk_id_value = None
    if text.lower().startswith('id') and text[2:].isdigit():
        is_vk_id = True
        vk_id_value = text[2:]
    elif text.isdigit() and 5 <= len(text) <= 12:
        is_vk_id = True
        vk_id_value = text

    is_ton = text.startswith(('UQ', 'EQ', '0:')) or (len(text) == 48 and text[:2] in ('UQ', 'EQ'))

    is_ogrn = text.isdigit() and len(text) == 13

    is_egrip = text.isdigit() and len(text) == 15

    is_github = False
    github_nick = None
    if text.lower().startswith('gh:'):
        is_github = True
        github_nick = text[3:].strip()
    elif text.lower().startswith('github:'):
        is_github = True
        github_nick = text[7:].strip()

    tg_combined = re.match(r'^@(\w+),\s*(\d+)$', text)

    return {
        "phone": is_phone,
        "phone_clean": clean_phone if is_phone else None,
        "ip": is_ip,
        "tg_username": is_tg_username,
        "tg_id": is_tg_id,
        "tg_combined": bool(tg_combined),
        "tg_combined_user": tg_combined.group(1) if tg_combined else None,
        "tg_combined_id": tg_combined.group(2) if tg_combined else None,
        "email": is_email,
        "vk_id": is_vk_id,
        "vk_id_value": vk_id_value,
        "ton": is_ton,
        "ogrn": is_ogrn,
        "egrip": is_egrip,
        "github": is_github,
        "github_nick": github_nick,
    }


def run_search(text):
    info = detect_query_type(text)
    result = {
        "query": text,
        "timestamp": datetime.now().isoformat(),
        "query_type": None,
        "results": {}
    }

    if info["tg_combined"]:
        result["query_type"] = "telegram_combined"
        user = info["tg_combined_user"]
        tid = info["tg_combined_id"]
        result["results"]["depsearch"] = call_depsearch(text)
        result["results"]["quickflow_by_username"] = call_quickflow(user)
        result["results"]["quickflow_by_id"] = call_quickflow(tid)
        result["results"]["leakcheck"] = call_leakcheck(text)
    elif info["phone"]:
        result["query_type"] = "phone"
        phone = info["phone_clean"]
        result["results"]["База"] = call_depsearch(phone)
        result["results"]["htmlweb_geo"] = call_htmlweb_geo(phone)
        result["results"]["jitler"] = jitler_search_with_wait("number", phone, max_polls=12, sleep_sec=5)
    elif info["ip"]:
        result["query_type"] = "ip"
        result["results"]["shodan"] = call_shodan(text)
    elif info["tg_username"]:
        result["query_type"] = "telegram_username"
        username = text.lstrip('@')
        result["results"]["База"] = call_depsearch(f"nick:{username}")
        result["results"]["quickflow"] = call_quickflow(username)
        result["results"]["leakcheck"] = call_leakcheck(text)
    elif info["tg_id"]:
        result["query_type"] = "telegram_id"
        result["results"]["База"] = call_depsearch(text)
        result["results"]["quickflow"] = call_quickflow(text)
        result["results"]["leakcheck"] = call_leakcheck(text)
    elif info["vk_id"]:
        result["query_type"] = "vk_id"
        vk_id = info["vk_id_value"]
        for vk_api in VK_APIS:
            result["results"][vk_api["name"]] = call_vk_api(vk_api, vk_id)
        result["results"]["leakcheck"] = call_leakcheck(text)
    elif info["ogrn"]:
        result["query_type"] = "ogrn"
        result["results"]["ofdata_company"] = call_ofdata_company_by_ogrn(text)
        result["results"]["База"] = call_depsearch(text)
    elif info["egrip"]:
        result["query_type"] = "egrip"
        result["results"]["ofdata_entrepreneur"] = call_ofdata_entrepreneur_by_ogrn(text)
        result["results"]["База"] = call_depsearch(text)
    elif info["ton"]:
        result["query_type"] = "ton_wallet"
        result["results"]["ton_transactions"] = call_ton(text)
    elif info["github"]:
        result["query_type"] = "github"
        nick = info["github_nick"]
        result["results"]["github_user"] = call_github_user(nick)
        result["results"]["github_repos"] = call_github_repos(nick)
        result["results"]["github_gists"] = call_github_gists(nick)
        result["results"]["github_events"] = call_github_events(nick)
        result["results"]["github_orgs"] = call_github_orgs(nick)
        result["results"]["github_starred"] = call_github_starred(nick)
        result["results"]["github_followers"] = call_github_followers(nick)
        result["results"]["github_following"] = call_github_following(nick)
    elif info["email"]:
        result["query_type"] = "email"
        result["results"]["База"] = call_depsearch(text)
        result["results"]["leakcheck"] = call_leakcheck(text)
    else:
        result["query_type"] = "default"
        # DepSearch: кириллика + пробелы + дата/год → ФИО (API сам распознаёт),
        # иначе → nick: (логины, латиница и т.д.)
        if re.match(r'^[А-ЯЁа-яё\s.\-\d,]+$', text.strip()):
            dep_q = text
        else:
            dep_q = f"nick:{text}"
        result["results"]["База"] = call_depsearch(dep_q)

    return result


def similarfaces_search(image_bytes, filename="face.jpg", mime="image/jpeg"):
    base = SIMILARFACES_BASE
    detect_url = SIMILARFACES_DETECT
    search_url = SIMILARFACES_SEARCH

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:151.0) Gecko/20100101 Firefox/151.0",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "Origin": base,
        "Referer": f"{base}/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }

    minute = int(time.time() // 60)

    try:
        frontend_id = hashlib.sha256(f"{minute}:detect-faces".encode()).hexdigest()
        files = {"image": (filename, image_bytes, mime)}
        r = requests.post(
            detect_url,
            files=files,
            headers={**headers, "X-Frontend-ID": frontend_id},
            timeout=90
        )
        detect_data = r.json() if r.status_code == 200 else {"error": f"HTTP {r.status_code}", "text": (r.text or "")[:500]}
    except Exception as e:
        detect_data = {"error": str(e)}

    search_results = []
    search_raw = None
    try:
        # IMPORTANT: according to the similarfaces.me frontend JS, the search-faces
        # endpoint uses the SAME X-Frontend-ID as detect-faces, i.e. hashed with
        # the literal string "detect-faces" (NOT "search-faces").  See homepage JS
        # line where `gDt("detect-faces")` is reused for the /bff/search-faces call.
        frontend_id2 = hashlib.sha256(f"{minute}:detect-faces".encode()).hexdigest()
        files = {"image": (filename, image_bytes, mime)}
        r = requests.post(
            search_url,
            files=files,
            headers={**headers, "X-Frontend-ID": frontend_id2},
            timeout=90
        )
        if r.status_code == 200:
            data = r.json()
            search_raw = data
            if isinstance(data, list):
                search_results = data
            elif isinstance(data, dict):
                search_results = data.get("results") or data.get("data") or []
        else:
            search_raw = {"error": f"HTTP {r.status_code}", "text": (r.text or "")[:500]}
    except Exception as e:
        search_raw = {"error": str(e)}

    return {
        "detected_faces": detect_data,
        "search_results": search_results,
        "raw_search_response": search_raw,
    }


def search4faces_search(image_bytes, filename="face.jpg"):
    try:
        try:
            import cloudscraper
            scraper = cloudscraper.create_scraper()
        except ImportError:
            scraper = requests.Session()

        scraper.headers.update({
            "User-Agent": "Mozilla/5.0 (Linux; Android 14; RMX3474) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Mobile Safari/537.36",
            "Referer": SEARCH4FACES_REFERER,
            "Origin": "https://search4faces.com",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "X-Requested-With": "XMLHttpRequest",
        })

        try:
            r = scraper.post(
                SEARCH4FACES_UPLOAD,
                data=image_bytes,
                headers={"Content-Type": "image/jpeg"},
                timeout=60
            )
            if r.status_code != 200 or not r.text.strip():
                return {"error": "upload_failed", "status": r.status_code, "text": (r.text or "")[:500]}
            upload_data = r.json()
        except Exception as e:
            return {"error": f"upload_exception: {e}"}

        server_filename = upload_data.get("url")
        faces = upload_data.get("boundings") or []
        scale = float(upload_data.get("scale", 1.0))

        if not faces or not server_filename:
            return {"upload": upload_data, "error": "no_faces_detected"}

        selected = faces[0]
        boundings = [selected[0] * scale, selected[1] * scale, selected[2] * scale, selected[3] * scale] + list(selected[4:])

        payload = {
            "query": "vk01",
            "lang": "ru",
            "filename": server_filename,
            "boundings": boundings,
        }

        for ctype in ("application/json", "application/x-www-form-urlencoded; charset=UTF-8"):
            try:
                r = scraper.post(
                    SEARCH4FACES_DETECT,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=90
                )
                if r.status_code == 200 and r.text.strip():
                    detect_data = r.json()
                    return {
                        "upload": upload_data,
                        "detect": detect_data,
                        "faces": detect_data.get("faces", []),
                    }
            except Exception:
                continue

        return {"upload": upload_data, "error": "detect_failed_no_response"}
    except Exception as e:
        return {"error": f"exception: {e}"}


def run_face_search(image_bytes):
    return {
        "query": "face_search",
        "timestamp": datetime.now().isoformat(),
        "query_type": "face_photo",
        "results": {
            "similarfaces_me": similarfaces_search(image_bytes),
            "search4faces_com": search4faces_search(image_bytes),
        }
    }



def format_htmlweb(data: dict) -> str:
    """Красивый вывод ответа htmlweb geo."""
    if not data or "error" in data:
        return ""
    lines = ["<b>🗺 Гео-данные</b>"]
    country = data.get("country", {})
    region  = data.get("region", {})
    city    = data.get("0", {})

    if country.get("name"):
        lines.append(f"  🌍 Страна: <code>{country['name']}</code>")
    if region.get("name"):
        lines.append(f"  🏛 Регион: <code>{region['name']}</code>")
    if region.get("okrug") or data.get("okrug"):
        lines.append(f"  🗺 Округ: <code>{region.get('okrug') or data.get('okrug','')}</code>")
    if city.get("name"):
        lines.append(f"  🏙 Город: <code>{city['name']}</code>")
    if city.get("oper_brand") or city.get("oper"):
        op = city.get("oper_brand") or city.get("oper","")
        lines.append(f"  📶 Оператор: <code>{op}</code>")
    tz = data.get("time_zone") or city.get("time_zone")
    if tz is not None:
        lines.append(f"  🕐 Часовой пояс: <code>UTC+{tz}</code>")
    lat = city.get("latitude")
    lon = city.get("longitude")
    if lat and lon:
        lines.append(f"  📌 Координаты: <code>{lat}, {lon}</code>")
    if city.get("def"):
        lines.append(f"  🔢 Диапазон: <code>{city['def']}</code>")
    return "\n".join(lines)


def format_jitler_phone(data: dict) -> str:
    """Красивый вывод ответа Jitler для номера телефона."""
    if not data:
        return ""
    # Если пришла ошибка
    if not data.get("result") or "error" in data:
        err = data.get("error", "нет данных")
        return ""

    resp = data.get("response", {})
    if not resp:
        return ""

    lines = ["<b>🔍 Данные по номеру</b>"]

    # Базовая инфо
    if resp.get("phone"):
        lines.append(f"  📱 Номер: <code>{resp['phone']}</code>")
    if resp.get("operator"):
        lines.append(f"  📶 Оператор: <code>{resp['operator']}</code>")
    if resp.get("region"):
        lines.append(f"  📍 Регион: <code>{resp['region']}</code>")
    if resp.get("country"):
        lines.append(f"  🌍 Страна: <code>{resp['country']}</code>")

    # Телефонные книги
    books = resp.get("phonebooks", [])
    if books:
        lines.append(f"\n  📒 Телефонные книги ({len(books)}):")
        for name in books[:10]:
            lines.append(f"    • {name}")

    # Telegram
    tg_list = resp.get("telegram", [])
    if tg_list:
        lines.append(f"\n  💬 Telegram ({len(tg_list)}):")
        for tg in tg_list:
            username = tg.get("username", "")
            uid      = tg.get("id", "")
            parts_tg = []
            if username: parts_tg.append(username)
            if uid:      parts_tg.append(f"ID: <code>{uid}</code>")
            lines.append(f"    • {' | '.join(parts_tg)}")

    # Профили соцсетей
    profiles = resp.get("profiles", {})
    for net, label in [("vk","VK"), ("ok","Одноклассники"), ("instagram","Instagram"),
                       ("facebook","Facebook"), ("tiktok","TikTok")]:
        entries = profiles.get(net, [])
        if entries:
            lines.append(f"\n  {'🔵' if net=='vk' else '🟠' if net=='ok' else '📸'} {label} ({len(entries)}):")
            for e in entries[:5]:
                name = e.get("name","")
                url  = e.get("url","")
                lines.append(f"    • <a href=\"{url}\">{name}</a>" if url else f"    • {name}")

    # Автомобили
    cars = resp.get("cars", [])
    if cars:
        lines.append(f"\n  🚗 Автомобили ({len(cars)}):")
        for c in cars[:5]:
            lines.append(f"    • {c}")

    # Упоминания
    mentions = resp.get("mentions", [])
    if mentions:
        lines.append(f"\n  🔗 Упоминания ({len(mentions)}):")
        for m in mentions[:5]:
            lines.append(f"    • {m}")

    return "\n".join(lines)


def format_depsearch(data: dict) -> str:
    """Красивый вывод ответа DepSearch."""
    if not data or "error" in data:
        return ""

    lines = ["<b>🗄 База данных</b>"]

    # Инфо о телефоне
    phone_info = data.get("phone_info", {})
    if phone_info:
        for label, key in [("📱 Номер", "phone"), ("🌍 Страна", "country"),
                           ("📶 Оператор", "operator"), ("📍 Регион", "region"),
                           ("🕐 Часовой пояс", "timezone")]:
            val = phone_info.get(key)
            if val:
                lines.append(f"  {label}: <code>{val}</code>")

    # Результаты поиска (записи из БД)
    results = data.get("results", [])
    if isinstance(results, list) and results:
        lines.append(f"\n  📋 Найдено записей: {len(results)}")
        for i, entry in enumerate(results[:15], 1):
            parts = []
            for k, emoji in [("name","👤"), ("fio","👤"), ("surname","👤"),
                             ("phone","📱"), ("email","📧"), ("address","📍"),
                             ("city","🏙"), ("region","🗺"), ("bdate","🎂"),
                             ("inn","🔢"), ("snils","🔢"), ("passport","🪪"),
                             ("vk","🔵"), ("telegram","💬"), ("job","💼"),
                             ("car","🚗"), ("carnum","🚗")]:
                val = entry.get(k)
                if val and str(val).strip() and str(val) not in ("-", "None", "null"):
                    parts.append(f"{emoji} {val}")
            if parts:
                lines.append(f"\n  <b>#{i}</b>")
                for p in parts:
                    lines.append(f"    {p}")

    # Если results это dict (другой формат)
    elif isinstance(results, dict):
        for section, items in results.items():
            if isinstance(items, list) and items:
                lines.append(f"\n  <b>{section}</b> ({len(items)}):")
                for item in items[:5]:
                    if isinstance(item, str):
                        lines.append(f"    • {item}")
                    elif isinstance(item, dict):
                        row = " | ".join(
                            f"{v}" for k, v in item.items()
                            if v and str(v).strip() not in ("-", "None")
                        )
                        if row:
                            lines.append(f"    • {row[:120]}")

    # Если совсем пусто
    if len(lines) == 1:
        return ""

    return "\n".join(lines)


def _phone_result_to_txt(data: dict) -> str:
    """Формирует текстовый отчёт (.txt) — jitler первым, без названий API."""
    results = data.get("results", {})
    lines   = []
    query   = data.get("query", "")
    ts      = data.get("timestamp", "")
    lines.append(f"РЕЗУЛЬТАТЫ ПОИСКА: {query}")
    lines.append(f"Дата: {ts}")
    lines.append("=" * 60)

    # ── Jitler ПЕРВЫМ ────────────────────────────────────────────────────────
    jit  = results.get("jitler", {})
    resp = jit.get("response", {})
    if resp:
        lines.append("\n[ ДАННЫЕ ПО НОМЕРУ ]")
        for label, key in [("Номер","phone"),("Оператор","operator"),
                           ("Регион","region"),("Страна","country")]:
            if resp.get(key): lines.append(f"  {label}: {resp[key]}")
        books = resp.get("phonebooks", [])
        if books:
            lines.append(f"\n  Телефонные книги ({len(books)}):")
            for b in books: lines.append(f"    - {b}")
        tg_list = resp.get("telegram", [])
        if tg_list:
            lines.append(f"\n  Telegram ({len(tg_list)}):")
            for tg in tg_list:
                u = tg.get("username",""); uid = tg.get("id","")
                lines.append(f"    - {u}  ID:{uid}")
        profiles = resp.get("profiles", {})
        for net, label in [("vk","VK"),("ok","Одноклассники"),
                           ("instagram","Instagram"),("facebook","Facebook"),
                           ("tiktok","TikTok")]:
            entries = profiles.get(net, [])
            if entries:
                lines.append(f"\n  {label} ({len(entries)}):")
                for e in entries:
                    lines.append(f"    - {e.get('name','')} {e.get('url','')}")
        cars = resp.get("cars", [])
        if cars:
            lines.append(f"\n  Автомобили ({len(cars)}):")
            for c in cars: lines.append(f"    - {c}")
        mentions = resp.get("mentions", [])
        if mentions:
            lines.append(f"\n  Упоминания ({len(mentions)}):")
            for m in mentions[:10]: lines.append(f"    - {m}")

    # ── Гео-данные ──────────────────────────────────────────────────────────
    hw = results.get("htmlweb_geo", {})
    if hw and "error" not in hw:
        lines.append("\n[ ГЕО-ДАННЫЕ ]")
        country = hw.get("country", {})
        region  = hw.get("region", {})
        city    = hw.get("0", {})
        if country.get("name"):  lines.append(f"  Страна:        {country['name']}")
        if region.get("name"):   lines.append(f"  Регион:        {region['name']}")
        if region.get("okrug") or hw.get("okrug"):
            lines.append(f"  Округ:         {region.get('okrug') or hw.get('okrug','')}")
        if city.get("name"):     lines.append(f"  Город:         {city['name']}")
        op = city.get("oper_brand") or city.get("oper","")
        if op:                   lines.append(f"  Оператор:      {op}")
        tz = hw.get("time_zone") or city.get("time_zone")
        if tz is not None:       lines.append(f"  Часовой пояс:  UTC+{tz}")
        lat = city.get("latitude"); lon = city.get("longitude")
        if lat and lon:          lines.append(f"  Координаты:    {lat}, {lon}")
        if city.get("def"):      lines.append(f"  Диапазон:      {city['def']}")

    # ── Остальные источники — сырой JSON ────────────────────────────────────
    for src_key, src_data in results.items():
        if src_key in ("jitler", "htmlweb_geo"):
            continue  # уже выведены красиво выше
        if not src_data:
            continue
        lines.append(f"\n[ {src_key.upper()} ]")
        lines.append(json.dumps(src_data, ensure_ascii=False, indent=2))

    return "\n".join(lines)


def format_phone_result(data: dict) -> str:
    """HTML-сообщение: jitler первым, без названий API."""
    results = data.get("results", {})
    blocks  = []

    # Jitler — ПЕРВЫМ
    jitler_block = format_jitler_phone(results.get("jitler", {}))
    if jitler_block:
        blocks.append(jitler_block)

    htmlweb_block = format_htmlweb(results.get("htmlweb_geo", {}))
    if htmlweb_block:
        blocks.append(htmlweb_block)

    depsearch_block = format_depsearch(results.get("База", {}))
    if depsearch_block:
        blocks.append(depsearch_block)

    if not blocks:
        return "❌ Данные не найдены."

    header = f"<b>🔎 Пробив номера: <code>{data.get('query','')}</code></b>\n"
    return header + "\n\n".join(blocks)


def _generic_result_to_txt(data: dict) -> str:
    """Универсальный txt-форматтер для не-phone результатов."""
    query   = data.get("query", "")
    ts      = data.get("timestamp", "")
    qtype   = data.get("query_type", "")
    results = data.get("results", {})
    lines   = [f"РЕЗУЛЬТАТЫ ПОИСКА: {query}", f"Дата: {ts}", "=" * 60]

    for src_key, src_data in results.items():
        if not src_data:
            continue
        lines.append(f"\n[ {src_key.upper()} ]")
        lines.append(json.dumps(src_data, ensure_ascii=False, indent=2))

    return "\n".join(lines)


def send_result_file(chat_id, query, data, caption="📄 Результаты поиска"):
    """Отправляет ТОЛЬКО .txt файл — никаких HTML-сообщений в чат."""
    query_type = data.get("query_type", "")

    if query_type == "phone":
        txt_content = _phone_result_to_txt(data)
    else:
        txt_content = _generic_result_to_txt(data)

    safe_name   = re.sub(r'[^\w\d]', '_', str(query))[:30] or "query"
    timestamp   = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_stream = io.BytesIO(txt_content.encode("utf-8"))
    file_stream.name = f"report_{safe_name}_{timestamp}.txt"
    try:
        bot.send_document(chat_id=chat_id, document=file_stream, caption=caption)
    except Exception:
        file_stream.seek(0)
        bot.send_document(chat_id=chat_id, document=file_stream)


def check_subscription(user_id):
    try:
        member = bot.get_chat_member(REQUIRED_CHANNEL_ID, user_id)
        return getattr(member, "status", None) in ("member", "administrator", "creator")
    except Exception:
        return False


def check_and_remove_subscription(chat_id, user_id):
    if chat_id in pending_sub_msg and check_subscription(user_id):
        try:
            bot.delete_message(chat_id, pending_sub_msg[chat_id])
        except Exception:
            pass
        del pending_sub_msg[chat_id]
        return True
    return False


def require_subscription(user_id, chat_id):
    if check_and_remove_subscription(chat_id, user_id):
        return True
    if not check_subscription(user_id):
        if chat_id in pending_sub_msg:
            return False
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.row(
            types.InlineKeyboardButton("Подписаться", url=REQUIRED_CHANNEL_URL),
            types.InlineKeyboardButton("Проверить", callback_data="check_sub")
        )
        msg = bot.send_message(
            chat_id,
            "⚠️ НЕ ПОТЕРЯЙТЕ БОТА\n\n"
            "Подпишитесь на канал, чтобы всегда быть в курсе обновлений и не потерять доступ!",
            parse_mode="HTML",
            reply_markup=markup,
            disable_web_page_preview=True
        )
        pending_sub_msg[chat_id] = msg.message_id
        return False
    return True


@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def cb_check_sub(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    if check_subscription(user_id):
        try:
            bot.delete_message(chat_id, call.message.message_id)
        except Exception:
            pass
        if chat_id in pending_sub_msg:
            del pending_sub_msg[chat_id]
        bot.send_message(
            chat_id,
            WELCOME_TEXT,
            reply_markup=get_main_keyboard(),
            disable_web_page_preview=True
        )
        bot.answer_callback_query(call.id, "Подписка подтверждена")
    else:
        bot.answer_callback_query(call.id, "Вы ещё не подписались на канал", show_alert=True)


@bot.message_handler(commands=["tarry"])
def admin_panel(message):
    if message.from_user.id != OWNER_ID:
        return
    register_user_if_not_exists(message.from_user.id)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Статистика", callback_data="admin_stats"))
    markup.add(types.InlineKeyboardButton("Пользователи", callback_data="admin_users"))
    markup.add(types.InlineKeyboardButton("Рассылка", callback_data="admin_broadcast"))
    markup.add(types.InlineKeyboardButton("Выдать Premium", callback_data="admin_grant"))
    bot.send_message(
        message.chat.id,
        "<b>Админ-панель</b>",
        reply_markup=markup,
        parse_mode="HTML",
        disable_web_page_preview=True
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("admin_"))
def admin_handler(call):
    if call.from_user.id != OWNER_ID:
        bot.answer_callback_query(call.id, text="Нет доступа", show_alert=True)
        return

    action = call.data.replace("admin_", "")

    if action == "stats":
        total_users = len(USER_DATA)
        text = f"<b>Статистика</b>\n\nПользователей: <code>{total_users}</code>\nВсего результатов по фото: <code>{sum(len(v) for v in FACE_RESULTS.values())}</code>"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Назад", callback_data="admin_back"))
        try:
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id,
                                  parse_mode="HTML", reply_markup=markup, disable_web_page_preview=True)
        except Exception:
            pass

    elif action == "users":
        if not USER_DATA:
            text = "<b>Пользователи</b>\n\nСписок пуст."
        else:
            lines = ["<b>Пользователи</b>\n"]
            for uid, info in list(USER_DATA.items())[:30]:
                lines.append(f"• <code>{uid}</code> — {info.get('subscription', '?')} — рег. {info.get('reg_date', '?')}")
            if len(USER_DATA) > 30:
                lines.append(f"\n...и ещё {len(USER_DATA) - 30}")
            text = "\n".join(lines)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Назад", callback_data="admin_back"))
        try:
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id,
                                  parse_mode="HTML", reply_markup=markup, disable_web_page_preview=True)
        except Exception:
            pass

    elif action == "broadcast":
        bot.answer_callback_query(call.id, text="Пришлите текст рассылки", show_alert=False)
        bot.send_message(call.message.chat.id,
                         "Пришлите текст для рассылки всем пользователям. Для отмены — /cancel",
                         disable_web_page_preview=True)
        bot.register_next_step_handler(call.message, do_broadcast)

    elif action == "grant":
        bot.answer_callback_query(call.id, text="Пришлите ID пользователя", show_alert=False)
        bot.send_message(call.message.chat.id,
                         "Пришлите Telegram ID пользователя, которому выдать Premium. Для отмены — /cancel",
                         disable_web_page_preview=True)
        bot.register_next_step_handler(call.message, do_grant_premium)

    elif action == "back":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Статистика", callback_data="admin_stats"))
        markup.add(types.InlineKeyboardButton("Пользователи", callback_data="admin_users"))
        markup.add(types.InlineKeyboardButton("Рассылка", callback_data="admin_broadcast"))
        markup.add(types.InlineKeyboardButton("Выдать Premium", callback_data="admin_grant"))
        try:
            bot.edit_message_text("<b>Админ-панель</b>", call.message.chat.id, call.message.message_id,
                                  parse_mode="HTML", reply_markup=markup, disable_web_page_preview=True)
        except Exception:
            pass


@bot.message_handler(commands=["cancel"])
def cancel_action(message):
    if message.from_user.id != OWNER_ID:
        return
    bot.send_message(message.chat.id, "Отменено", disable_web_page_preview=True)


def do_broadcast(message):
    if message.from_user.id != OWNER_ID:
        return
    chat_id = message.chat.id
    text = message.text.strip()
    if not text:
        bot.send_message(chat_id, "Текст не может быть пустым.", disable_web_page_preview=True)
        return
    user_ids = list(USER_DATA.keys())
    if not user_ids:
        bot.send_message(chat_id, "Нет пользователей для рассылки.", disable_web_page_preview=True)
        return
    confirm_msg = bot.send_message(
        chat_id,
        f"Начинаю рассылку для {len(user_ids)} пользователей.\n"
        f"Текст:\n{text[:200]}{'...' if len(text) > 200 else ''}\n\n"
        f"Это может занять время...",
        disable_web_page_preview=True
    )

    def _do_mailing():
        success = 0
        fail = 0
        for uid in user_ids:
            try:
                bot.send_message(uid, text, parse_mode="HTML", disable_web_page_preview=True)
                success += 1
                time.sleep(0.05)
            except Exception:
                fail += 1
        try:
            bot.edit_message_text(
                f"Рассылка завершена\nОтправлено: {success}\nНе доставлено: {fail}\nВсего: {len(user_ids)}",
                chat_id,
                confirm_msg.message_id,
                disable_web_page_preview=True
            )
        except Exception:
            pass

    threading.Thread(target=_do_mailing, daemon=True).start()


def do_grant_premium(message):
    if message.from_user.id != OWNER_ID:
        return
    try:
        target_id = int(message.text.strip())
    except ValueError:
        bot.send_message(message.chat.id, "Неверный ID", disable_web_page_preview=True)
        return
    if target_id not in USER_DATA:
        USER_DATA[target_id] = {
            "id": target_id,
            "subscription": "Premium",
            "requests_left": "∞",
            "reg_date": datetime.now().strftime("%d.%m.%Y")
        }
    else:
        USER_DATA[target_id]["subscription"] = "Premium"
        USER_DATA[target_id]["requests_left"] = "∞"
    bot.send_message(message.chat.id, f"Пользователю {target_id} выдан Premium",
                     disable_web_page_preview=True)


@bot.message_handler(commands=['snils', 'inn', 'ogrn', 'egrip', 'company', 'adr', 'vu', 'passport'])
def handle_commands(message):
    register_user_if_not_exists(message.from_user.id)
    if message.from_user.id != OWNER_ID and not require_subscription(message.from_user.id, message.chat.id):
        return
    command = message.text.split(maxsplit=1)
    if len(command) < 2:
        bot.reply_to(message, "Пожалуйста, укажите значение после команды.", disable_web_page_preview=True)
        return

    cmd = command[0].lower()
    value = command[1].strip()

    if cmd == '/snils':
        clean_value = re.sub(r'\D', '', value)
        query = f"snils{clean_value}"
    elif cmd == '/inn':
        clean_value = re.sub(r'\D', '', value)
        if len(clean_value) not in (10, 12):
            bot.reply_to(message, "ИНН должен содержать 10 (юр.лицо) или 12 (ИП) цифр.",
                         disable_web_page_preview=True)
            return
        status_msg = status_animation(message.chat.id)
        bot.send_chat_action(message.chat.id, 'typing')
        try:
            if len(clean_value) == 10:
                ofdata_result = call_ofdata_company_by_inn(clean_value)
                qt = "inn_company"
            else:
                ofdata_result = call_ofdata_entrepreneur_by_inn(clean_value)
                qt = "inn_entrepreneur"
            result = {
                "query": f"inn{clean_value}",
                "timestamp": datetime.now().isoformat(),
                "query_type": qt,
                "results": {
                    "ofdata": ofdata_result,
                    "База": call_depsearch(f"inn{clean_value}"),
                }
            }
            finish_status_animation(message.chat.id, status_msg.message_id)
            send_result_file(message.chat.id, f"inn{clean_value}", result)
        except Exception as e:
            finish_status_animation(message.chat.id, status_msg.message_id)
            bot.reply_to(message, f"Ошибка обработки запроса: {safe_html(str(e))}",
                         disable_web_page_preview=True)
        return
    elif cmd == '/ogrn':
        clean_value = re.sub(r'\D', '', value)
        if len(clean_value) != 13:
            bot.reply_to(message, "ОГРН должен содержать 13 цифр.",
                         disable_web_page_preview=True)
            return
        status_msg = status_animation(message.chat.id)
        bot.send_chat_action(message.chat.id, 'typing')
        try:
            result = {
                "query": f"ogrn{clean_value}",
                "timestamp": datetime.now().isoformat(),
                "query_type": "ogrn",
                "results": {
                    "ofdata_company": call_ofdata_company_by_ogrn(clean_value),
                    "База": call_depsearch(f"ogrn{clean_value}"),
                }
            }
            finish_status_animation(message.chat.id, status_msg.message_id)
            send_result_file(message.chat.id, f"ogrn{clean_value}", result)
        except Exception as e:
            finish_status_animation(message.chat.id, status_msg.message_id)
            bot.reply_to(message, f"Ошибка обработки запроса: {safe_html(str(e))}",
                         disable_web_page_preview=True)
        return
    elif cmd == '/egrip':
        clean_value = re.sub(r'\D', '', value)
        if len(clean_value) != 15:
            bot.reply_to(message, "ОГРНИП должен содержать 15 цифр.",
                         disable_web_page_preview=True)
            return
        status_msg = status_animation(message.chat.id)
        bot.send_chat_action(message.chat.id, 'typing')
        try:
            result = {
                "query": f"egrip{clean_value}",
                "timestamp": datetime.now().isoformat(),
                "query_type": "egrip",
                "results": {
                    "ofdata_entrepreneur": call_ofdata_entrepreneur_by_ogrn(clean_value),
                    "База": call_depsearch(f"egrip{clean_value}"),
                }
            }
            finish_status_animation(message.chat.id, status_msg.message_id)
            send_result_file(message.chat.id, f"egrip{clean_value}", result)
        except Exception as e:
            finish_status_animation(message.chat.id, status_msg.message_id)
            bot.reply_to(message, f"Ошибка обработки запроса: {safe_html(str(e))}",
                         disable_web_page_preview=True)
        return
    elif cmd == '/company':
        name = value.strip()
        if len(name) < 4:
            bot.reply_to(message, "Минимум 4 символа для поиска по наименованию.",
                         disable_web_page_preview=True)
            return
        status_msg = status_animation(message.chat.id)
        bot.send_chat_action(message.chat.id, 'typing')
        try:
            result = {
                "query": f"company:{name}",
                "timestamp": datetime.now().isoformat(),
                "query_type": "company_search",
                "results": {
                    "ofdata_search_org": call_ofdata_search(name, obj="org"),
                    "ofdata_search_ent": call_ofdata_search(name, obj="ent"),
                }
            }
            finish_status_animation(message.chat.id, status_msg.message_id)
            send_result_file(message.chat.id, f"company_{name[:30]}", result)
        except Exception as e:
            finish_status_animation(message.chat.id, status_msg.message_id)
            bot.reply_to(message, f"Ошибка обработки запроса: {safe_html(str(e))}",
                         disable_web_page_preview=True)
        return
    elif cmd == '/adr':
        query = f"addr:{value}"
    else:
        query = value

    status_msg = status_animation(message.chat.id)
    bot.send_chat_action(message.chat.id, 'typing')
    try:
        result = run_search(query)
        finish_status_animation(message.chat.id, status_msg.message_id)
        send_result_file(message.chat.id, query, result)
    except Exception as e:
        finish_status_animation(message.chat.id, status_msg.message_id)
        bot.reply_to(message, f"Ошибка обработки запроса: {safe_html(str(e))}", disable_web_page_preview=True)


def normalize_face_results(raw_result):
    cards = []

    sf = (raw_result.get("results") or {}).get("similarfaces_me") or {}
    sf_items = sf.get("search_results") or []
    if isinstance(sf_items, dict):
        sf_items = sf_items.get("results") or sf_items.get("data") or []
    for r in sf_items:
        if not isinstance(r, dict):
            continue
        photo = ""
        for k in ("photo", "image_url", "image", "img", "src", "url", "avatar"):
            v = r.get(k)
            if v:
                photo = v
                break
        name = ""
        for k in ("name", "full_name", "fullname"):
            v = r.get(k)
            if v:
                name = v
                break
        rate = ""
        for k in ("similarity_rate", "similarity", "rate", "score"):
            v = r.get(k)
            if v not in (None, ""):
                try:
                    rate = float(v)
                except Exception:
                    rate = v
                break
        vk_id = ""
        for k in ("vk_id", "vkid", "id", "user_id"):
            v = r.get(k)
            if v not in (None, ""):
                vk_id = v
                break
        city = ""
        for k in ("city", "town"):
            v = r.get(k)
            if v:
                city = v
                break
        social = r.get("social") or r.get("link") or (f"https://vk.com/id{vk_id}" if vk_id else "")
        cards.append({
            "source": "similarfaces.me",
            "photo": photo,
            "name": name or "—",
            "rate": rate,
            "vk_id": str(vk_id) if vk_id else "",
            "city": city,
            "social": social,
            "raw": r,
        })

    s4f = (raw_result.get("results") or {}).get("search4faces_com") or {}
    s4f_faces = s4f.get("faces") or []
    if isinstance(s4f_faces, list):
        for r in s4f_faces:
            if not isinstance(r, list) or len(r) < 4:
                continue
            def g(i, r=r):
                return r[i] if i < len(r) else ""
            try:
                pct = float(g(10)) if g(10) not in ("", None) else 0.0
            except (TypeError, ValueError):
                pct = 0.0
            name = f"{g(13)} {g(14)}".strip()
            city = ", ".join(v for v in (g(16), g(17)) if v)
            cards.append({
                "source": "search4faces.com",
                "photo": g(2),
                "photo_link": g(3),
                "name": name or "—",
                "rate": pct,
                "vk_id": "",
                "city": city,
                "social": g(1),
                "age": g(12) if g(12) not in ("", -1, "-1") else "",
                "birth": g(18),
                "raw": r,
            })

    cards.sort(key=lambda c: c["rate"] if isinstance(c.get("rate"), (int, float)) else 0, reverse=True)
    return cards


def get_face_card_caption(card, index, total):
    rate = card.get("rate", "")
    if isinstance(rate, (int, float)):
        rate_str = f"{rate:.2f}%"
    else:
        rate_str = str(rate) if rate else "—"

    lines = [
        f"<b>Поиск по лицу</b>  ·  {index + 1}/{total}",
        "",
        f"<b>Источник:</b> <code>{safe_html(card.get('source', '—'))}</code>",
        f"<b>Имя:</b> {safe_html(card.get('name', '—'))}",
        f"<b>Схожесть:</b> <code>{rate_str}</code>",
    ]
    if card.get("vk_id"):
        lines.append(f"<b>VK ID:</b> <code>{safe_html(card['vk_id'])}</code>")
    if card.get("city"):
        lines.append(f"<b>Город:</b> {safe_html(card['city'])}")
    if card.get("age"):
        lines.append(f"<b>Возраст:</b> {safe_html(card['age'])}")
    if card.get("birth"):
        lines.append(f"<b>День рождения:</b> {safe_html(card['birth'])}")
    if card.get("social"):
        lines.append(f"<b>Профиль:</b> {safe_html(card['social'])}")
    return "\n".join(lines)


def get_face_keyboard(index, total):
    markup = types.InlineKeyboardMarkup(row_width=3)

    prev_btn = types.InlineKeyboardButton(
        "Назад" if index > 0 else " ",
        callback_data=f"face_prev_{index}" if index > 0 else "dummy"
    )
    counter_btn = types.InlineKeyboardButton(f"{index + 1} / {total}", callback_data="dummy")
    next_btn = types.InlineKeyboardButton(
        "Вперёд" if index < total - 1 else " ",
        callback_data=f"face_next_{index}" if index < total - 1 else "dummy"
    )
    markup.row(prev_btn, counter_btn, next_btn)

    markup.add(types.InlineKeyboardButton("Вернуться в меню", callback_data="menu_main"))
    return markup


def edit_face_card_inplace(chat_id, message_id, user_id, index=0):
    cards = FACE_RESULTS.get(user_id, [])
    if not cards:
        return
    index = max(0, min(index, len(cards) - 1))
    card = cards[index]
    caption = get_face_card_caption(card, index, len(cards))
    markup = get_face_keyboard(index, len(cards))
    photo_url = card.get("photo_link") or card.get("photo") or ""
    if photo_url:
        try:
            bot.edit_message_media(
                chat_id=chat_id,
                message_id=message_id,
                media=types.InputMediaPhoto(photo_url, caption=caption, parse_mode="HTML"),
                reply_markup=markup
            )
            return
        except Exception:
            pass
    try:
        text = caption + (f"\n\nФото: {safe_html(photo_url)}" if photo_url else "\n\nФото недоступно")
        bot.edit_message_text(text, chat_id, message_id,
                              parse_mode="HTML", reply_markup=markup, disable_web_page_preview=False)
    except Exception:
        pass


def show_face_card(chat_id, user_id, index=0):
    cards = FACE_RESULTS.get(user_id, [])
    if not cards:
        bot.send_message(chat_id, "Результаты не найдены.", disable_web_page_preview=True)
        return

    index = max(0, min(index, len(cards) - 1))
    card = cards[index]
    caption = get_face_card_caption(card, index, len(cards))
    markup = get_face_keyboard(index, len(cards))

    photo_url = card.get("photo_link") or card.get("photo") or ""
    if photo_url:
        try:
            bot.send_photo(
                chat_id=chat_id,
                photo=photo_url,
                caption=caption,
                parse_mode="HTML",
                reply_markup=markup
            )
            return
        except Exception:
            pass

    text = caption + (f"\n\nФото: {safe_html(photo_url)}" if photo_url else "\n\nФото недоступно")
    bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode="HTML",
        reply_markup=markup,
        disable_web_page_preview=False
    )


@bot.message_handler(content_types=['photo'])
def handle_photo_message(message):
    user_id = message.from_user.id
    register_user_if_not_exists(user_id)
    if user_id != OWNER_ID and not require_subscription(user_id, message.chat.id):
        return

    status_msg = status_animation(message.chat.id)
    bot.send_chat_action(message.chat.id, 'typing')

    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded = bot.download_file(file_info.file_path)
        image_bytes = downloaded if isinstance(downloaded, bytes) else downloaded.read()

        raw_result = run_face_search(image_bytes)
        cards = normalize_face_results(raw_result)

        finish_status_animation(message.chat.id, status_msg.message_id)

        if not cards:
            send_result_file(message.chat.id, "face_search", raw_result,
                             caption="Лица не найдены. Сырой ответ API:")
            return

        FACE_RESULTS[user_id] = cards
        show_face_card(message.chat.id, user_id, index=0)
    except Exception as e:
        finish_status_animation(message.chat.id, status_msg.message_id)
        bot.reply_to(message, f"Ошибка при поиске по лицу: {safe_html(str(e))}", disable_web_page_preview=True)


@bot.message_handler(content_types=['text'])
def handle_text_message(message):
    user_id = message.from_user.id
    register_user_if_not_exists(user_id)
    if user_id != OWNER_ID and not require_subscription(user_id, message.chat.id):
        return
    text = message.text.strip()

    status_msg = status_animation(message.chat.id)
    bot.send_chat_action(message.chat.id, 'typing')

    try:
        result = run_search(text)
        finish_status_animation(message.chat.id, status_msg.message_id)
        send_result_file(message.chat.id, text, result)
    except Exception as e:
        finish_status_animation(message.chat.id, status_msg.message_id)
        bot.reply_to(message, f"Ошибка обработки запроса: {safe_html(str(e))}", disable_web_page_preview=True)


if __name__ == "__main__":
    print("Бот Router запущен...")
    bot.infinity_polling()
