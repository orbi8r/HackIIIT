import os
import json
import shutil
from gtts import gTTS
from moviepy import (
    AudioFileClip,
    concatenate_videoclips,
    ImageClip,
    VideoFileClip,
    CompositeAudioClip,
    concatenate_audioclips,
)


def generate_tts_audio(text, out_path):
    """Generate TTS audio from text and save to out_path."""
    tts = gTTS(text=text, lang="en")
    tts.save(out_path)


def generate_audio_files():
    """Generate audio files from JSON caption files.

    Looks for JSON files in '../caption_creator/captioned_dataset' that contain a 'boxes'
    key with a list of sentences. For each non-empty sentence, a corresponding audio file
    is generated in the 'audio_sentences' folder using text-to-speech.
    """
    base_dir = os.path.join(
        os.path.dirname(__file__), "..", "caption_creator", "captioned_dataset"
    )
    audio_output_dir = os.path.join(os.path.dirname(__file__), "audio_sentences")
    os.makedirs(audio_output_dir, exist_ok=True)
    for filename in sorted(os.listdir(base_dir)):
        if filename.endswith(".json"):
            json_path = os.path.join(base_dir, filename)
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            boxes = data.get("boxes", [])
            for i, sentence in enumerate(boxes):
                if sentence.strip():
                    out_file = os.path.join(
                        audio_output_dir, f"{os.path.splitext(filename)[0]}_{i}.mp3"
                    )
                    generate_tts_audio(sentence, out_file)


def create_bg_loop(bg_music, target_duration):
    """Create an audio loop of the background music to match target_duration."""
    clips = []
    current = 0
    while current < target_duration:
        sub_duration = min(bg_music.duration, target_duration - current)
        clips.append(bg_music.subclipped(0, sub_duration))
        current += sub_duration
    return concatenate_audioclips(clips)


def video():
    """
    Generates a video by performing the following steps:

    1. Audio Generation:
       - Searches for JSON files in the '../caption_creator/captioned_dataset' directory.
       - Expects each JSON file to have a key 'boxes' with a list of sentences.
       - Uses text-to-speech (gTTS) to generate audio files for non-empty sentences.
       - Saves the generated MP3 files in the 'audio_sentences' folder.

    2. Video Creation:
       - Loads audio files from the 'audio_sentences' folder.
       - For each audio file, finds a JPEG image in '../caption_creator/captioned_dataset' with a
         matching prefix (the part of the audio filename before the last underscore).
       - Creates an image clip resized to a base size (1280x720) and sets its duration to match the audio.
       - Inserts a transition clip (from 'transition.mp4') if the audio file prefix changes between clips.

    3. Background Music:
       - Loads a background music MP3 ('background.mp3') and loops it to match the total video duration.
       - Combines the looping background music with the original clip audio.

    4. Finalization:
       - Concatenates all video clips into a single video and writes the output to 'output.mp4'.
       - Closes all video and audio clips.
       - Deletes the temporary 'audio_sentences' folder containing the generated audio files.

    Returns:
        str: The filepath of the generated video ('output.mp4').

    Usage:
        >>> from combine_audio_video import video
        >>> output_path = video()
    """
    # Step 1: Generate temporary TTS audio files from the captions
    generate_audio_files()

    # Define paths for generated audio, images, transition, and background music
    audio_dir = os.path.join(os.path.dirname(__file__), "audio_sentences")
    caption_dataset_dir = os.path.join(
        os.path.dirname(__file__), "..", "caption_creator", "captioned_dataset"
    )
    transition_path = os.path.join(os.path.dirname(__file__), "transition.mp4")
    bg_music_path = os.path.join(os.path.dirname(__file__), "background.mp3")

    # Get sorted list of all MP3 files generated
    mp3_files = sorted(
        [
            os.path.join(audio_dir, f)
            for f in os.listdir(audio_dir)
            if f.lower().endswith(".mp3")
        ]
    )
    if not mp3_files:
        raise ValueError("No mp3 files found in: " + audio_dir)

    base_size = (1280, 720)
    video_clips = []
    for i, file in enumerate(mp3_files):
        audio_clip = AudioFileClip(file)
        base = os.path.basename(file)
        prefix = base.rsplit("_", 1)[0]
        matching_images = [
            f
            for f in os.listdir(caption_dataset_dir)
            if f.lower().endswith(".jpg") and f.startswith(prefix)
        ]
        if not matching_images:
            raise ValueError(
                f"No matching image found for audio {file} using prefix '{prefix}'"
            )
        image_path = os.path.join(caption_dataset_dir, matching_images[0])
        image_clip = (
            ImageClip(image_path)
            .resized(new_size=base_size)
            .with_duration(audio_clip.duration)
        )
        clip = image_clip.with_audio(audio_clip)
        video_clips.append(clip)
        if i < len(mp3_files) - 1:
            next_base = os.path.basename(mp3_files[i + 1])
            next_prefix = next_base.rsplit("_", 1)[0]
            if prefix != next_prefix:
                trans_clip = VideoFileClip(transition_path).resized(new_size=base_size)
                video_clips.append(trans_clip)

    # Concatenate the video clips
    final_clip = concatenate_videoclips(video_clips)

    # Step 3: Add background music by creating a looping clip
    bg_music = AudioFileClip(bg_music_path)
    bg_loop = create_bg_loop(bg_music, final_clip.duration)
    combined_audio = CompositeAudioClip([final_clip.audio, bg_loop])
    final_clip = final_clip.with_audio(combined_audio)

    # Step 4: Write the output video and clean up temporary files
    output_path = "output.mp4"
    final_clip.write_videofile(output_path, fps=24)

    for clip in video_clips:
        clip.close()
    final_clip.close()
    shutil.rmtree(audio_dir)

    return output_path


if __name__ == "__main__":
    video()
