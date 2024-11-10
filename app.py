import os
import argparse
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

parser = argparse.ArgumentParser(description="Start the image annotation tool.")
parser.add_argument("image_folder", help="Specify the image folder within the static/images directory.")
args = parser.parse_args()

IMAGE_FOLDER = os.path.join('static', 'images', args.image_folder)

if not os.path.exists(IMAGE_FOLDER):
    raise FileNotFoundError(f"The specified folder {IMAGE_FOLDER} does not exist.")

# 日付をフォーマットしてファイル名に組み込む
today_date = datetime.now().strftime("%Y%m%d")
DATA_FILE = f'data_{today_date}.json'

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump([], f)

def get_image_files():
    with open(DATA_FILE, 'r') as f:
        try:
            annotations = json.load(f)
            tagged_images = set([annotation['data_name'] for annotation in annotations])
        except json.JSONDecodeError:
            tagged_images = set()

    all_images = [f for f in os.listdir(IMAGE_FOLDER) if f.endswith(('.jpg', '.png')) and 'Dark' not in f]
    image_files = [f'{args.image_folder}/{f}' for f in all_images if f'{args.image_folder}/{f}' not in tagged_images]

    return image_files

@app.route('/')
def index():
    image_files = get_image_files()
    if not image_files:
        return "本フォルダーは既にアノテーションが済んでいます．"
    return render_template('index.html', image_files=image_files)

@app.route('/save_annotations', methods=['POST'])
def save_annotations():
    data = request.json
    image_name = data['data_name']
    tags = data['tags']

    try:
        with open(DATA_FILE, 'r') as f:
            file_content = f.read()
            if file_content.strip():
                annotations = json.loads(file_content)
            else:
                annotations = []
    except (FileNotFoundError, json.JSONDecodeError):
        annotations = []

    annotations.append({
        "data_name": image_name,
        "tags": tags
    })

    with open(DATA_FILE, 'w') as f:
        json.dump(annotations, f, indent=2)

    return jsonify({"status": "success"}), 200

if __name__ == "__main__":
    app.run(debug=True)
