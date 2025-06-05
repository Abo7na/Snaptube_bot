import telebot
from telebot import types
import os
import yt_dlp

TOKEN = "7699983015:AAGBiFfOyi0GJa491tuTnioU9css5Nd-50U"
CHANNELS = ["snaptubei", "snaptubeo"]

bot = telebot.TeleBot(TOKEN)

# إنشاء مجلدات إذا غير موجودة
if not os.path.exists('snaptube videos'):
    os.mkdir('snaptube videos')
if not os.path.exists('snaptube musics'):
    os.mkdir('snaptube musics')

LANGUAGES = {
    "ar": {
        "welcome": "مرحباً بك في بوت Snaptube!\n\nيمكنك تحميل الفيديوهات أو المقاطع الصوتية بكل سهولة. اختر لغتك من الأزرار أدناه، وسنرشدك للخطوات التالية.\n\nيرجى العلم أن الاشتراك في قنواتنا ضروري لاستخدام البوت.\n\nاختر لغتك:",
        "subscribe": "يرجى الاشتراك في القنوات التالية لتتمكن من استخدام البوت:\n\n- @snaptubei\n- @snaptubeo\n\nبعد الاشتراك، اضغط على زر \"تحقق من الاشتراك\" لتأكيد الاشتراك.",
        "check_subscription": "تحقق من الاشتراك",
        "not_subscribed": "يبدو أنك لم تشترك في جميع القنوات بعد. الرجاء الاشتراك ثم المحاولة مرة أخرى.",
        "send_link": "تم التحقق من اشتراكك! الآن أرسل الرابط الذي تريد تحميله.",
        "choose_format": "كيف تريد تنزيل الملف؟",
        "video": "تحميل فيديو",
        "audio_fingerprint": "تحميل بصمة صوتية",
        "audio": "تحميل مقطع صوتي",
        "processing": "جاري التحميل والمعالجة، الرجاء الانتظار...",
        "done": "تم إرسال الملف بنجاح!\n\nإذا أعجبك البوت، لا تتردد في مشاركته مع أصدقائك.\n\nلتحميل فيديو آخر، اضغط /start",
        "error": "حدث خطأ، يرجى إعادة المحاولة."
    },
    "en": {
        "welcome": "Welcome to Snaptube Bot!\n\nYou can easily download videos or audio clips. Please select your language below, and we will guide you through the steps.\n\nSubscription to our channels is required to use the bot.\n\nChoose your language:",
        "subscribe": "Please subscribe to the following channels to use the bot:\n\n- @snaptubei\n- @snaptubeo\n\nAfter subscribing, press the \"Check Subscription\" button to confirm.",
        "check_subscription": "Check Subscription",
        "not_subscribed": "It seems you haven't subscribed to all channels yet. Please subscribe and try again.",
        "send_link": "Subscription verified! Now send the video or audio link you want to download.",
        "choose_format": "How do you want to download the file?",
        "video": "Download Video",
        "audio_fingerprint": "Download Audio Fingerprint",
        "audio": "Download Audio Clip",
        "processing": "Downloading and processing, please wait...",
        "done": "File sent successfully!\n\nIf you like the bot, please share it with your friends.\n\nTo download another video, press /start",
        "error": "An error occurred, please try again."
    },
    "fr": {
        "welcome": "Bienvenue sur le Bot Snaptube!\n\nVous pouvez facilement télécharger des vidéos ou des clips audio. Veuillez sélectionner votre langue ci-dessous, et nous vous guiderons à travers les étapes.\n\nL'abonnement à nos chaînes est requis pour utiliser le bot.\n\nChoisissez votre langue:",
        "subscribe": "Veuillez vous abonner aux chaînes suivantes pour utiliser le bot:\n\n- @snaptubei\n- @snaptubeo\n\nAprès l'abonnement, appuyez sur le bouton \"Vérifier l'abonnement\" pour confirmer.",
        "check_subscription": "Vérifier l'abonnement",
        "not_subscribed": "Il semble que vous ne soyez pas abonné à toutes les chaînes. Veuillez vous abonner et réessayer.",
        "send_link": "Abonnement vérifié! Envoyez maintenant le lien de la vidéo ou de l'audio que vous souhaitez télécharger.",
        "choose_format": "Comment voulez-vous télécharger le fichier?",
        "video": "Télécharger la vidéo",
        "audio_fingerprint": "Télécharger l'empreinte audio",
        "audio": "Télécharger le clip audio",
        "processing": "Téléchargement et traitement en cours, veuillez patienter...",
        "done": "Fichier envoyé avec succès!\n\nSi vous aimez le bot, partagez-le avec vos amis.\n\nPour télécharger une autre vidéo, appuyez sur /start",
        "error": "Une erreur est survenue, veuillez réessayer."
    }
}

user_lang = {}
user_state = {}
user_link = {}
user_format = {}

def check_user_subscription(user_id):
    for channel in CHANNELS:
        try:
            member = bot.get_chat_member(f"@{channel}", user_id)
            if member.status not in ['member', 'creator', 'administrator']:
                return False
        except Exception:
            return False
    return True

def language_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    buttons = [
        types.InlineKeyboardButton(text="🇸🇦 العربية", callback_data="lang_ar"),
        types.InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en"),
        types.InlineKeyboardButton(text="🇫🇷 Français", callback_data="lang_fr"),
    ]
    keyboard.add(*buttons)
    return keyboard

def subscription_keyboard(lang_code):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text=LANGUAGES[lang_code]["check_subscription"], callback_data="check_sub"))
    return keyboard

def format_keyboard(lang_code):
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    keyboard.add(
        types.InlineKeyboardButton(text=LANGUAGES[lang_code]["video"], callback_data="format_video"),
        types.InlineKeyboardButton(text=LANGUAGES[lang_code]["audio_fingerprint"], callback_data="format_audio_fingerprint"),
        types.InlineKeyboardButton(text=LANGUAGES[lang_code]["audio"], callback_data="format_audio"),
    )
    return keyboard

def download_media(link, download_type, user_id):
    output_path = ""
    ydl_opts = {}

    if download_type == 'video':
        output_path = 'snaptube videos/%(title)s.%(ext)s'
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': output_path,
            'merge_output_format': 'mp4',
            'quiet': True,
            'no_warnings': True,
        }
    elif download_type == 'audio':
        output_path = 'snaptube musics/%(title)s.%(ext)s'
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_path,
            'quiet': True,
            'no_warnings': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
    elif download_type == 'audio_fingerprint':
        output_path = 'snaptube musics/%(title)s_fingerprint.%(ext)s'
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_path,
            'quiet': True,
            'no_warnings': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'ogg',
                'preferredquality': '192',
            }],
        }
    else:
        raise ValueError("Invalid download type")

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(link, download=True)
        filename = ydl.prepare_filename(info)

        if download_type == 'audio':
            if not filename.endswith('.mp3'):
                filename = filename.rsplit('.', 1)[0] + '.mp3'
        elif download_type == 'audio_fingerprint':
            if not filename.endswith('.ogg'):
                filename = filename.rsplit('.', 1)[0] + '.ogg'

        return filename

def share_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="🔗 شارك البوت مع أصدقائك", url="https://t.me/Snaptubecc_bot"))
    return keyboard

@bot.message_handler(commands=['start'])
def start_handler(message):
    user_id = message.from_user.id
    user_lang[user_id] = "ar"  # اللغة الافتراضية عربية
    user_state[user_id] = "awaiting_language"
    bot.send_message(message.chat.id, LANGUAGES["ar"]["welcome"], reply_markup=language_keyboard())

@bot.callback_query_handler(func=lambda call: call.data.startswith("lang_"))
def lang_select(call):
    user_id = call.from_user.id
    lang_code = call.data.split("_")[1]
    user_lang[user_id] = lang_code
    user_state[user_id] = "awaiting_subscription"
    bot.answer_callback_query(call.id)
    bot.edit_message_text(LANGUAGES[lang_code]["subscribe"], call.message.chat.id, call.message.message_id,
                          reply_markup=subscription_keyboard(lang_code))

@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def check_subscription_handler(call):
    user_id = call.from_user.id
    lang_code = user_lang.get(user_id, "ar")
    if check_user_subscription(user_id):
        user_state[user_id] = "awaiting_link"
        bot.edit_message_text(LANGUAGES[lang_code]["send_link"], call.message.chat.id, call.message.message_id)
    else:
        bot.edit_message_text(LANGUAGES[lang_code]["not_subscribed"], call.message.chat.id, call.message.message_id,
                              reply_markup=subscription_keyboard(lang_code))

@bot.message_handler(func=lambda message: user_state.get(message.from_user.id) == "awaiting_link")
def link_handler(message):
    user_id = message.from_user.id
    user_link[user_id] = message.text
    lang_code = user_lang.get(user_id, "ar")
    bot.send_message(user_id, LANGUAGES[lang_code]["choose_format"], reply_markup=format_keyboard(lang_code))

@bot.callback_query_handler(func=lambda call: call.data.startswith("format_"))
def format_select(call):
    user_id = call.from_user.id
    download_type = call.data.split("_")[1]
    lang_code = user_lang.get(user_id, "ar")
    link = user_link.get(user_id, "")
    user_format[user_id] = download_type

    if link:
        bot.edit_message_text(LANGUAGES[lang_code]["processing"], call.message.chat.id, call.message.message_id)
        try:
            file_path = download_media(link, download_type, user_id)
            with open(file_path, 'rb') as file:
                bot.send_document(user_id, file)
            os.remove(file_path)  # حذف الملف بعد الإرسال
            bot.send_message(user_id, LANGUAGES[lang_code]["done"], reply_markup=share_keyboard())  # إضافة الزر هنا
        except Exception as e:
            bot.send_message(user_id, LANGUAGES[lang_code]["error"])
            print(f"Error downloading media: {e}")
    else:
        bot.send_message(user_id, LANGUAGES[lang_code]["error"])

bot.polling(none_stop=True)
