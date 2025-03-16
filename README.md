# HackIIIT
 This repo is for HackIIIT '25 hackathon FOSS work

# Project Instructions

## Generating Memes and Video

This project allows you to generate meme images using captions and then combine them into a final video.

### Meme Generation

Use the `caption()` function from the caption_creator package to create memes. Each call to `caption()` takes a dictionary with keys `template_id` and `boxes`, and it saves the meme image and its corresponding JSON metadata into the `captioned_dataset` folder.

Example:
````python
# ...existing code...
from caption_creator.caption import create as caption

# Generate multiple memes
meme_labels = []
meme_data = [
    {"template_id": "112126428", "boxes": ["Meme text 1", "Meme text 2"]},
    {"template_id": "112126429", "boxes": ["Another meme text 1", "Another meme text 2"]},
    # Add additional meme data as needed
]

for data in meme_data:
    label = caption(data)
    meme_labels.append(label)
    print(f"Meme generated with label: {label}")
# ...existing code...
````

### Video Generation

After generating the memes, a corresponding JSON file is saved in the `captioned_dataset` folder. You can use the `video()` function in the post_processing package to:
  - Generate TTS audio from the meme captions,
  - Create video clips by matching audio files with meme images,
  - Combine background music, and
  - Produce a final video (output.mp4).
  
Import and call the `video()` function as follows:
````python
# ...existing code...
from post_processing.combine_audio_video import video

output_video = video()
print("Video generated at:", output_video)
# ...existing code...
````

Now, by first calling the `caption()` function repeatedly and then the `video()` function once, you can generate multiple memes and combine them into a single video output.
