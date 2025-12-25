import os
from pyrogram import Client, filters
from py_tgcalls import PyTgCalls
from py_tgcalls.types.input_stream import AudioPiped
from py_tgcalls.types.input_stream.quality import HighQualityAudio
import yt_dlp

API_ID = int(os.getenv("8291719430"))
API_HASH = os.getenv("8291719430:AAEwzm5T5wzux2fss2_o5Gy2FX1Xm35DuHo")
BOT_TOKEN = os.getenv("8291719430:AAEwzm5T5wzux2fss2_o5Gy2FX1Xm35DuHo")

app = Client(
    "vc_music_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

pytgcalls = PyTgCalls(app)

def yt_audio(query):
    ydl_opts = {
        "format": "bestaudio",
        "quiet": True,
        "noplaylist": True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=False)
        return info["entries"][0]["url"]

@app.on_message(filters.command("play") & filters.group)
async def play(_, message):
    if len(message.command) < 2:
        return await message.reply("❌ Song name do")

    query = " ".join(message.command[1:])
    audio = yt_audio(query)

    chat_id = message.chat.id
    await pytgcalls.join_group_call(
        chat_id,
        AudioPiped(audio, HighQualityAudio())
    )

    await message.reply(f"🎶 Playing: **{query}**")

@app.on_message(filters.command("stop") & filters.group)
async def stop(_, message):
    await pytgcalls.leave_group_call(message.chat.id)
    await message.reply("🛑 Music stopped")

app.start()
pytgcalls.start()
print("🔥 VC MUSIC BOT RUNNING")
app.idle()
