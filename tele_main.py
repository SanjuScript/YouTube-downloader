#!/usr/bin/env python3
"""
🎬 YT Downloader Telegram Bot
Funny Malayalam-style bot made by Sanju 😂

Install:
    pip install python-telegram-bot yt-dlp

Setup:
    1. Go to @BotFather on Telegram → /newbot → copy the token
    2. Replace BOT_TOKEN below with your token
    3. Replace DEVELOPER_ID with your Telegram user ID (get it from @userinfobot)
    4. python yt_telegram_bot.py
"""

import os
import asyncio
import logging
import random
import yt_dlp

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# ── Config ─────────────────────────────────────────────────────────────────────

BOT_TOKEN    = os.environ.get("BOT_TOKEN", "")
DEVELOPER_ID = int(os.environ.get("DEVELOPER_ID", "0"))
FFMPEG_PATH  = "/usr/bin/ffmpeg"
DOWNLOAD_DIR = "/tmp/downloads"

logging.basicConfig(level=logging.INFO)

# ── Malayalam-flavoured funny texts ───────────────────────────────────────────

START_TEXTS = [
    "Loooi 🖐️ Nammude bot-ilekku swagatham!\n\nYouTube link ayacholu.., njan set aakki tharaam! 🔥\nVideo aano Audio aano vendath? Paranjaal mathi, njan ready! 💪",
    "Entha mone... scene aano? 😎\n\nYouTube link ivide ittal mathi, baaki njan nokkikkollam!\nDownload-um upload-um ellam njan nissaram aayi cheythu tharaam! 🚀",
    "Ooi Bot active aanu tto! 🎬\n\nLink ayakkuu... download cheyyuuu... enjoy cheyyuu!\nFree aanu, pakshe ente server-ine kondu thallikkalle makkale! 😅",
]

WAITING_TEXTS = [
    "YouTube-um njaanum thammil oru cheriya adjustment nadakkunnu!😜",
    "Downloading... ⏳\nServer pani tharaathe irikkaan ellavarum onnu prarthikku! 🙏",
    "Adipoli! Link njaan kandupidichu... 🔍\nIppo set aakki tharaam makkale!",
    "YouTube ithu kandaal nammale oodikkum! 😂\nEnthayaalum njaan onnu try cheythu nokkatte...",
    "Ithokke download cheythu tharunnathinu enikkenthilum tharo? 😅\nOru chaya cash aayalum mathiyayirunnu! ☕",
]

DONE_VIDEO_TEXTS = [
    "Ayyy! Video ready aanu broo! 🎬🔥 Vegam download cheytho!",
    "Innaa... ningalude video! 😎 Enjoy cheyyu, pakshe naattukaare motham kaanichu scene aakkalle! 😂",
    "Done aayi! 🎉 Credit eppozhum tharanam ennu njaan parayunnilla, pakshe thannaal santhosham! 😌",
]

DONE_AUDIO_TEXTS = [
    "Paattu ready! 🎵 Ippo paadikkollu, aarum kelkkilla ennu vicharich paadikoo 😂",
    "Audio ithaaaa..! 🎶 Shower-il paadi thakarkkan use cheyyoo! 😂",
    "MP3 ready aayi! 🎵 Ithinte ellam pinnil ee pavam bot aanu... oru credit tharunnath nallathayirikum 😎",
]

ERROR_TEXTS = [
    "Ayyoo! Enthoo sambhavichu! 😭 Link adichu poyo? Onnu verify cheythittu vere link idoo.",
    "YouTube-il enthoo scene undu... block cheytha pole thonunnu! 😤 Vere link try cheyye machane.",
    "Ithu work aayilla bro! 😅 Link shari aano? Private video aano atho valid alle?",
]

INVALID_TEXTS = [
    "ithenthe thenga ayachath? 😂 Enikku YouTube link aanu vendath, allaathe ninte life story alla!",
    "Ithu YouTube link alla machane 😅 youtube.com/watch?v=... ee style-il onnu idoo.",
    "Nee link thanne aano ayachath? 🧐 Oru nalla YouTube link ittu nokku broo!",
]

FUNNY_ROASTS = [
    "Sathyamm parayamallo... new oru bhayankara genius thanne! 😂",
    "Ippozhum waiting aano? ⏳ Coffee kudikkaan poyathaano atho avide urangi poyo? ☕",
    "Nee ithrem download cheythittum ee paavam bot-inu oru chaya kudikkaan polum paisa kittillallo! 😭",
]
# ── Helpers ────────────────────────────────────────────────────────────────────

def is_youtube_url(text: str) -> bool:
    return any(d in text for d in ["youtube.com/watch", "youtu.be/", "youtube.com/shorts"])


def funny(lst: list) -> str:
    return random.choice(lst)


def format_duration(seconds: int) -> str:
    m, s = divmod(seconds or 0, 60)
    h, m = divmod(m, 60)
    return f"{h}h {m}m {s}s" if h else f"{m}m {s}s"


def fetch_info(url: str) -> dict | None:
    try:
        with yt_dlp.YoutubeDL({"quiet": True, "noplaylist": True}) as ydl:
            return ydl.extract_info(url, download=False)
    except Exception:
        return None


def build_quality_keyboard(url: str) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton("🎬 Video 480p",  callback_data=f"v|480|{url}")],
        [InlineKeyboardButton("🎬 Video 720p",  callback_data=f"v|720|{url}")],
        [InlineKeyboardButton("🎬 Video 1080p", callback_data=f"v|1080|{url}")],
        [InlineKeyboardButton("🎬 Best Video",  callback_data=f"v|best|{url}")],
        [InlineKeyboardButton("🎵 Audio MP3",   callback_data=f"a|mp3|{url}")],
        [InlineKeyboardButton("🎵 Audio M4A",   callback_data=f"a|m4a|{url}")],
    ]
    return InlineKeyboardMarkup(buttons)


def get_video_opts(quality: str, out_path: str) -> dict:
    fmt_map = {
        "480":  "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=480]+bestaudio/best",
        "720":  "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=720]+bestaudio/best",
        "1080": "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=1080]+bestaudio/best",
        "best": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best",
    }
    return {
        "format": fmt_map.get(quality, fmt_map["best"]),
        "merge_output_format": "mp4",
        "outtmpl": out_path,
        "ffmpeg_location": FFMPEG_PATH,
        "postprocessors": [{"key": "FFmpegVideoConvertor", "preferedformat": "mp4"}],
        "noplaylist": True,
        "quiet": True,
    }


def get_audio_opts(fmt: str, out_path: str) -> dict:
    return {
        "format": "bestaudio/best",
        "outtmpl": out_path,
        "ffmpeg_location": FFMPEG_PATH,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": fmt,
                "preferredquality": "0",
            }
        ],
        "noplaylist": True,
        "quiet": True,
    }


# ── Handlers ───────────────────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    name = user.first_name or "machane"
    await update.message.reply_text(
        f"👋 *{name}!* {funny(START_TEXTS)}\n\n"
        f"Just paste a YouTube link and I'll handle the rest! 🚀\n\n"
        f"_Ithu undaakkiyathu nammude swantham **Sanju** aanu! 🙏 Avanu oru thanks parayoo!_\n\n"
        f"_Type /help to see all commands_",
        parse_mode="Markdown",
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 *YT Downloader Bot — Help*\n\n"
        "Just paste any YouTube link and I'll show download options!\n\n"
        "*Commands:*\n"
        "🎬 /start — Start the bot\n"
        "❓ /help — Show this help\n"
        "👨‍💻 /dev — About the developer\n"
        "😂 /joke — Get a Malayalam joke\n"
        "📊 /stats — Bot stats\n\n"
        "_Supported: youtube.com, youtu.be, YouTube Shorts_ ✅",
        parse_mode="Markdown",
    )


async def dev_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👨‍💻 *Developer Info*\n\n"
        "Ithu undaakkiyathu: *Sanju* 😎\n"
        "Complaints: /dev-il thanne parayu makkale! 😂\n"
        "Praise: Njan ready aayi irikkuvan! 🙌\n\n"
        "_Bug-undo? Enkil report cheytho, njan fix cheyyaam... thonniyaal matthram!_ 😅",
        parse_mode="Markdown",
    )


async def joke_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    jokes = [
    "Oru ammayi joliku poyi. Interviewer: 'Ninte pradhana hobby entha?' Ammayi: 'Njan nalla pole abhinayikkum.' Interviewer: 'Cinema-yil aano?' Ammayi: 'Alla, veettil joli cheyyunna pole!' 😂",
    "Kalyanam kazhinja puthiya jodi hotel-il poyi. Bharthavu: 'Nee enthaa kazhikkan edukkunne?' Bharya: 'Ente ishtam ninte ishtam aanu.' Bharthavu: 'Enkil namukku oru Beef Roast edukkaam.' Bharya: 'Ayyoo, athu venda!' 😂",
    "Appanum makanum koode nadakkunnu. Makan: 'Appa, njan valuthakumbol ammaye kalyanam kazhikkum!' Appan: 'Patti! Ente bharyaye nee engane kalyanam kazhikkum?' Makan: 'Pinnne appan alle ente ammaye kalyanam kazhichathu!' 🤣",
    "Oru kalla kaavyan (Poet) koottukaaranodu: 'Njaan ezhuthiya kavitha vayichu nante bharya karanju poyi.' Koottukaaran: 'Athra nalla kavithayayirunno?' Kaavyan: 'Alla, njaan athu ezhuthiyathu avalude puthiya pattu-sari-yil aayirunnu!' 😭",
    "Pappu: 'Aliya, njan innale rathri 2 manikku ente bharyaye vilichunarthi.' Aliya: 'Enthinayirunnu?' Pappu: 'Aval kure neramayi urakathil entho parayunnu... athu kettu thalavedana eduthittaanu!' 😂",
    ]
    await update.message.reply_text(f"😂 *Joke of the moment:*\n\n{random.choice(jokes)}", parse_mode="Markdown")


async def stats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📊 *Bot Stats*\n\n"
        "Status: 🟢 Running (miraculously)\n"
        "Developer sleep status: 😴 Unknown\n"
        "Bugs fixed today: Probably 0 😂\n"
        "Coffee consumed: ☕☕☕ (3 cups minimum)\n\n"
        "_Server running on pure willpower_ 💪",
        parse_mode="Markdown",
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    user = update.effective_user
    name = user.first_name or "machane"
    
    await context.bot.send_message(
        chat_id=DEVELOPER_ID,
        text=(
            f"👤 *New User Activity!*\n\n"
            f"Name: {user.first_name} {user.last_name or ''}\n"
            f"Username: @{user.username or 'no username'}\n"
            f"User ID: `{user.id}`\n"
            f"Message: `{text[:100]}`"
        ),
        parse_mode="Markdown",
    )

    if not is_youtube_url(text):
        await update.message.reply_text(
            f"*{name}*, {funny(INVALID_TEXTS)}"
        )
        return

    wait_msg = await update.message.reply_text(
        f"🔍 *{name}*, {funny(WAITING_TEXTS)}"
    )

    info = await asyncio.get_event_loop().run_in_executor(None, fetch_info, text)

    if not info:
        await wait_msg.edit_text(f"❌ *{name}*, {funny(ERROR_TEXTS)}")
        return

    title    = info.get("title", "Unknown")
    channel  = info.get("uploader", "Unknown")
    duration = format_duration(info.get("duration", 0))
    views    = f"{info.get('view_count', 0):,}"

    caption = (
        f"🎬 *{title}*\n\n"
        f"📺 Channel: {channel}\n"
        f"⏱ Duration: {duration}\n"
        f"👁 Views: {views}\n\n"
        f"*{name}*, enthu format venam? 👇\n"
        f"_Powered by YouTube Gandharvan 🎶 | Made by Sanju 😎_"
    )

    await wait_msg.delete()
    await update.message.reply_text(
        caption,
        parse_mode="Markdown",
        reply_markup=build_quality_keyboard(text),
    )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    name = user.first_name or "machane"
    await query.answer(random.choice(FUNNY_ROASTS))

    data = query.data.split("|", 2)
    mode, quality, url = data[0], data[1], data[2]
    
    await context.bot.send_message(
        chat_id=DEVELOPER_ID,
        text=(
            f"⬇️ *New Download!*\n\n"
            f"Name: {user.first_name} {user.last_name or ''}\n"
            f"Username: @{user.username or 'no username'}\n"
            f"User ID: `{user.id}`\n"
            f"Type: {'🎬 Video' if mode == 'v' else '🎵 Audio'} {quality}\n"
            f"URL: {url}"
        ),
        parse_mode="Markdown",
    )

    chat_id = query.message.chat_id
    status_msg = await context.bot.send_message(
        chat_id, f"⏳ *{name}*, {funny(WAITING_TEXTS)}",
        parse_mode="Markdown"
    )

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    out_template = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")

    try:
        if mode == "v":
            opts = get_video_opts(quality, out_template)
            done_text = f"*{name}*, {funny(DONE_VIDEO_TEXTS)}\n\n_YouTube Gandharvan 🎶 | Made with ❤️ by Sanju_"
        else:
            opts = get_audio_opts(quality, out_template)
            done_text = f"*{name}*, {funny(DONE_AUDIO_TEXTS)}\n\n_YouTube Gandharvan 🎶 | Made with ❤️ by Sanju_"

        def do_download():
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                return ydl.prepare_filename(info)

        filename = await asyncio.get_event_loop().run_in_executor(None, do_download)

        if mode == "a":
            base = os.path.splitext(filename)[0]
            filename = f"{base}.{quality}"

        await status_msg.edit_text(f"📤 *{name}*, upload cheyyunnu... oru minute wait aake! 🚀", parse_mode="Markdown")

        file_size = os.path.getsize(filename) if os.path.exists(filename) else 0

        if file_size > 50 * 1024 * 1024:
            await status_msg.edit_text(
                f"😅 *{name}*, file valare valuthaanu!\n\n"
                "50MB-l adhikam aanu, Telegram-il direct ayakaanilla 😭\n"
                f"File saved locally: `{filename}`",
                parse_mode="Markdown",
            )
            return

        await status_msg.edit_text(f"📤 *{name}*, almost done! 🎉", parse_mode="Markdown")

        with open(filename, "rb") as f:
            if mode == "v":
                await context.bot.send_video(
                    chat_id=chat_id,
                    video=f,
                    caption=done_text,
                    supports_streaming=True,
                    read_timeout=120,
                    write_timeout=120,
                    parse_mode="Markdown",
                )
            else:
                await context.bot.send_audio(
                    chat_id=chat_id,
                    audio=f,
                    caption=done_text,
                    read_timeout=120,
                    write_timeout=120,
                    parse_mode="Markdown",
                )

        await status_msg.delete()
        os.remove(filename)

    except Exception as e:
        await status_msg.edit_text(
            f"❌ *{name}*, {funny(ERROR_TEXTS)}\n\n`{str(e)[:200]}`",
            parse_mode="Markdown",
        )

async def notify_developer(app):
    """Sends a message to the developer when bot starts."""
    try:
        await app.bot.send_message(
            chat_id=DEVELOPER_ID,
            text=(
                "🚀 *Bot started* 🚀\n\n"
                "Ooi! Nammude bot ippo live aanu! 🎉\n"
                "Server set aanu, download-um smooth aayi nadakkunnu.\n"
            ),
            parse_mode="Markdown",
        )
    except Exception:
        pass  # Developer ID might not have started bot

# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    app = (
    ApplicationBuilder()
    .token(BOT_TOKEN)
    .post_init(notify_developer)
    .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help",  help_cmd))
    app.add_handler(CommandHandler("dev",   dev_cmd))
    app.add_handler(CommandHandler("joke",  joke_cmd))
    app.add_handler(CommandHandler("stats", stats_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(handle_callback))

    print("=" * 50)
    print("  🎬 Youtube Gandharvan starting...! 🔥")
    print("=" * 50)

    app.run_polling(
        allowed_updates=["message", "callback_query"],
        drop_pending_updates=True,  # This clears old messages so the bot doesn't crash on restart
        close_loop=False
    )


if __name__ == "__main__":
    main()