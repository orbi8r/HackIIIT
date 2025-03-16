from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from fastapi.responses import StreamingResponse
import io
import shutil
import os

from caption_creator.caption import create as caption
from post_processing.combine_audio_video import video

app = FastAPI()


class MemeItem(BaseModel):
    template_id: str
    boxes: List[str]


class MemeData(BaseModel):
    memes: List[MemeItem]


@app.post("/generate_video")
def generate_video(meme_data: MemeData):
    # Process each meme data
    for item in meme_data.memes:
        caption({"template_id": item.template_id, "boxes": item.boxes})
    # Generate video and get output file path
    video_path = video()
    # Read the binary content of the video file
    with open(video_path, "rb") as f:
        video_bytes = f.read()
    # Delete the captioned_dataset folder if it exists
    dataset_dir = os.path.join(
        os.path.dirname(__file__), "caption_creator", "captioned_dataset"
    )
    if os.path.exists(dataset_dir):
        shutil.rmtree(dataset_dir)
    return StreamingResponse(
        io.BytesIO(video_bytes),
        media_type="video/mp4",
        headers={"Content-Disposition": "attachment; filename=output.mp4"},
    )


if __name__ == "__main__":
    import uvicorn

    # Running the server on all interfaces so playit.gg can forward traffic.
    uvicorn.run(app, host="0.0.0.0", port=19227)
