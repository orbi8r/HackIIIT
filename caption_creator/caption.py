import requests
import os
import json
import re

def _get_credentials():
    # Compute credentials path relative to this file. Assumes credentials are located one level up in "credentials\config.json"
    cred_path = os.path.join(os.path.dirname(__file__), "..", "credentials", "config.json")
    with open(cred_path) as f:
        creds = json.load(f)
    return creds["IMGFLIP_USERNAME"], creds["IMGFLIP_PASSWORD"]

def sanitize_filename(name):
    return re.sub(r"[^\w\-]", "_", name)

def create_meme_text(template_id, username, password, text0, text1=""):
    url = "https://api.imgflip.com/caption_image"
    params = {
        "template_id": template_id,
        "username": username,
        "password": password,
        "text0": text0,
        "text1": text1,
    }
    resp = requests.post(url, data=params)
    return resp.json()

def create_meme_boxes(template_id, username, password, boxes):
    url = "https://api.imgflip.com/caption_image"
    params = {
        "template_id": template_id,
        "username": username,
        "password": password,
    }
    for i, box in enumerate(boxes):
        params[f"boxes[{i}][text]"] = box["text"]
    resp = requests.post(url, data=params)
    return resp.json()

def _get_next_index(dataset_dir):
    max_index = 0
    if os.path.exists(dataset_dir):
        for fname in os.listdir(dataset_dir):
            if fname.endswith(".jpg"):
                try:
                    idx = int(fname.split("_")[0])
                    if idx > max_index:
                        max_index = idx
                except ValueError:
                    pass
    return max_index + 1

def create(json_data):
    # Expects a dict with keys "template_id" and "boxes" (list of texts)
    if "template_id" not in json_data or "boxes" not in json_data:
        raise ValueError("Missing 'template_id' or 'boxes' in input json")
    template_id = json_data["template_id"]
    boxes = json_data["boxes"]
    if not isinstance(boxes, list) or not boxes:
        raise ValueError("'boxes' must be a non-empty list")
    username, password = _get_credentials()
    if len(boxes) in [1, 2]:
        text0 = boxes[0]
        text1 = boxes[1] if len(boxes) == 2 else ""
        response = create_meme_text(template_id, username, password, text0, text1)
    else:
        boxes_param = [{"text": text} for text in boxes]
        response = create_meme_boxes(template_id, username, password, boxes_param)
    if not response.get("success"):
        raise Exception(response.get("error_message", "Unknown error"))
    caption_url = response["data"]["url"]
    img_resp = requests.get(caption_url)
    if img_resp.status_code != 200:
        raise Exception("Failed to download image")
    # Create dataset folder "captioned_dataset" near this file
    dataset_dir = os.path.join(os.path.dirname(__file__), "captioned_dataset")
    os.makedirs(dataset_dir, exist_ok=True)
    new_index = _get_next_index(dataset_dir)
    label = f"{new_index}_{sanitize_filename(str(template_id))}"
    img_path = os.path.join(dataset_dir, f"{label}.jpg")
    with open(img_path, "wb") as img_file:
        img_file.write(img_resp.content)
    json_path = os.path.join(dataset_dir, f"{label}.json")
    with open(json_path, "w") as json_file:
        json.dump({"boxes": boxes}, json_file)
    return label