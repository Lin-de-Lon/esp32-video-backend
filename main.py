import os
import shutil
import subprocess
from fastapi import FastAPI, UploadFile, File, Form
from telegram import Bot

# ==================================================
# CONFIG TELEGRAM
# ==================================================
BOT_TOKEN = "8547405964:AAF3xsaRQlUAeFmdRjIRntCw7hDyFClduus"
CHAT_ID   = "8214639314"
bot = Bot(token=BOT_TOKEN)

# ==================================================
# FASTAPI
# ==================================================
app = FastAPI()

# ==================================================
# ENDPOINT 1:
# RECIBIR CADA FOTO INDIVIDUAL
# ==================================================
@app.post("/upload-photo")
async def upload_photo(file: UploadFile = File(...), index: int = Form(...)):

    # crear carpeta si no existe
    os.makedirs("photos", exist_ok=True)

    # ruta de la foto
    path = f"photos/photo_{index:02d}.jpg"

    # guardar foto
    with open(path, "wb") as f:
        f.write(await file.read())

    print(f"Foto recibida: {path}")
    return {"status": "ok", "index": index}


# ==================================================
# ENDPOINT 2:
# GENERAR VIDEO MP4 Y ENVIARLO A TELEGRAM
# ==================================================
@app.post("/render-video")
async def render_video():

    # asegurar que hay fotos
    if not os.path.exists("photos"):
        return {"error": "No hay carpeta de fotos"}

    images = sorted([f for f in os.listdir("photos") if f.endswith(".jpg")])
    if len(images) == 0:
        return {"error": "No hay fotos JPG"}

    print(f"{len(images)} fotos encontradas, creando video...")

    output = "video.mp4"

    # crear video con ffmpeg
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

    print("Vídeo creado, enviando a Telegram...")

    # enviar vídeo a telegram
    with open(output, "rb") as v:
        bot.send_video(chat_id=CHAT_ID, video=v, supports_streaming=True)

    print("Vídeo enviado.")

    # limpiar
    shutil.rmtree("photos")
    os.remove(output)

    print("Limpieza completada.")

    return {"status": "video enviado", "fotos": len(images)}
