# from fastapi import FastAPI, HTTPException
# from fastapi.responses import FileResponse
# from fastapi.middleware.cors import CORSMiddleware
# import yt_dlp
# import uuid
# import os


# app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# DOWNLOAD_DIR = "downloads"

# @app.post("/download")
# def download_video(data: dict):
#     yt_link = data.get("realYtLink")

#     if not yt_link: 
#         raise HTTPException(status_code=400, detail="No YouTube link provided")

#     file_id = str(uuid.uuid4())
#     output_template = os.path.join(DOWNLOAD_DIR, f"{file_id}.%(ext)s")

#     ydl_opts = {
#         "format": "mp4",
#         "outtmpl": output_template,
#         "quiet": True,
#         "no_warnings": True,
#     }

#     try:
#         with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#             info = ydl.extract_info(yt_link, download=True)
#             ext = info.get("ext", "mp4")
#             file_path = f"{DOWNLOAD_DIR}/{file_id}.{ext}"

#         if not os.path.exists(file_path):
#             raise HTTPException(status_code=500, detail="File not found after download")

#         return FileResponse(
#             path=file_path,
#             filename="video.mp4",
#             media_type="video/mp4"
#         )

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp
import uuid
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@app.post("/download")
def download_video(data: dict, bg: BackgroundTasks):
    yt_link = data.get("realYtLink")

    if not yt_link:
        raise HTTPException(status_code=400, detail="No YouTube link provided")

    file_id = str(uuid.uuid4())
    output_template = os.path.join(DOWNLOAD_DIR, f"{file_id}.%(ext)s")

    ydl_opts = {
        "format": "bestvideo+bestaudio/best",
        "merge_output_format": "mp4",
        "outtmpl": output_template,
        "quiet": True,
        "no_warnings": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(yt_link, download=True)
            ext = info.get("ext", "mp4")
            file_path = os.path.join(DOWNLOAD_DIR, f"{file_id}.{ext}")

        if not os.path.exists(file_path):
            raise HTTPException(500, "File not found after download")

        # delete file AFTER response is sent
        bg.add_task(os.remove, file_path)

        return FileResponse(
            path=file_path,
            filename="video.mp4",
            media_type="video/mp4"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
