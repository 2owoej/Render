import asyncio
import logging
import os

from pyrogram import Client, filters, idle
from pyrogram.types import Message

from py_tgcalls import PyTgCalls
from py_tgcalls.types.input_stream import AudioPiped
from py_tgcalls.types.input_stream.quality import HighQualityAudio

import yt_dlp
from youtube_search import YoutubeSearch

# ===== ENV VARIABLES (Render) =====
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

SESSION = "render_vc_bot"

logging.basicConfig(level=logging.INFO)

# ===== CLIENTS =====
app = Client(
    SESSION,
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

pytgcalls = PyTgCalls(app)

queue = []
current_chat = None
playing = False

# ===== YOUTUBE =====
def yt_search(query):
    r = YoutubeSearch(query, max_results=1).to_dict()
    if not r:
        return None
    return {
        "title": r[0]["title"],
        "url": f"https://youtube.com/watch?v={r[0]['id']}"
    }

def get_audio(url):
    ydl_opts = {"format": "bestaudio", "quiet": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return info["url"]

# ===== PLAYER =====
async def play_next():
    global playing
    if not queue:
        playing = False
        return

    song = queue.pop(0)
    audio = get_audio(song["url"])

    await pytgcalls.join_group_call(
        current_chat,
        AudioPiped(audio, HighQualityAudio())
    )

    await app.send_message(
        current_chat,
        f"🎵 **Now Playing**\n\n{song['title']}"
    )

    playing = True

# ===== COMMANDS =====
@app.on_message(filters.command("start"))
async def start(_, m: Message):
    await m.reply(
        "🎧 **Render VC Music Bot**\n\n"
        "/play song_name\n"
        "/skip\n"
        "/stop\n\n"
        "⚠️ Free Render (sleep possible)"
    )

@app.on_message(filters.command("play"))
async def play(_, m: Message):
    global current_chat

    if len(m.command) < 2:
        return await m.reply("Song name do")

    song = yt_search(" ".join(m.command[1:]))
    if not song:
        return await m.reply("Song nahi mila")

    queue.append(song)
    await m.reply(f"✅ Added: **{song['title']}**")

    if not playing:
        current_chat = m.chat.id
        await play_next()

@app.on_message(filters.command("skip"))
async def skip(_, m: Message):
    try:
        await pytgcalls.leave_group_call(current_chat)
    except:
        pass
    await play_next()
    await m.reply("⏭ Skipped")

@app.on_message(filters.command("stop"))
async def stop(_, m: Message):
    queue.clear()
    try:
        await pytgcalls.leave_group_call(current_chat)
    except:
        pass
    await m.reply("⏹ Stopped")

# ===== MAIN =====
async def main():
    await app.start()
    await pytgcalls.start()
    print("🔥 RENDER VC MUSIC BOT RUNNING")
    await idle()

if __name__ == "__main__":
    asyncio.run(main())