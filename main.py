import os
import shutil
import zipfile
import subprocess
from fastapi import FastAPI, UploadFile, File
from telegram import Bot

BOT_TOKEN = "8547405964:AAF3xsaRQlUAeFmdRjIRntCw7hDyFClduus"
CHAT_ID   = "8214639314"

bot = Bot(token=BOT_TOKEN)

app = FastAPI()

@app.post("/upload-zip")
async def upload_zip(file: UploadFile = File(...)):

    if os.path.exists("photos"):
        shutil.rmtree("photos")
    os.makedirs("photos", exist_ok=True)

    zip_path = "batch.zip"
    with open(zip_path, "wb") as z:
        z.write(await file.read())

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall("photos")

    images = sorted([f for f in os.listdir("photos") if f.endswith(".jpg")])
    if not images:
        return {"error": "ZIP vacío o sin imágenes JPG"}

    output = "video.mp4"

    subprocess.run([
        "ffmpeg",
        "-y",
        "-framerate", "5",
        "-pattern_type", "glob",
        "-i", "photos/*.jpg",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        output
    ], check=True)

    with open(output, "rb") as v:
        bot.send_video(chat_id=CHAT_ID, video=v)

    shutil.rmtree("photos")
    os.remove(zip_path)
    os.remove(output)

    return {"status": "ok", "msg": "Video enviado a Telegram"}
