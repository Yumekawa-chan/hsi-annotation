import os
import argparse
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

parser = argparse.ArgumentParser(description="Start the image annotation tool.")
parser.add_argument("date_folder", help="Specify the date folder within the static/images directory.")
args = parser.parse_args()

DATE_FOLDER = os.path.join('static', 'images', args.date_folder)

if not os.path.exists(DATE_FOLDER):
    raise FileNotFoundError(f"The specified folder {DATE_FOLDER} does not exist.")

# 日付をフォーマットしてファイル名に組み込む
today_date = datetime.now().strftime("%Y%m%d")
DATA_FILE = f'data_{today_date}.json'

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump([], f)

def get_image_files():
    image_files = []
    places = [d for d in os.listdir(DATE_FOLDER) if os.path.isdir(os.path.join(DATE_FOLDER, d))]

    for place in places:
        place_path = os.path.join(DATE_FOLDER, place)
        images_in_place = [f for f in os.listdir(place_path) if f.endswith(('.jpg', '.png')) and 'Dark' not in f]
        
        with open(DATA_FILE, 'r') as f:
            try:
                annotations = json.load(f)
                tagged_images = set([annotation['data_name'] for annotation in annotations])
            except json.JSONDecodeError:
                tagged_images = set()

        for image in images_in_place:
            image_path = f"static/images/{args.date_folder}/{place}/{image}"
            if image_path not in tagged_images:
                image_files.append({
                    "place": place,
                    "path": image_path
                })

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
    place = data['place']

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
        "tags": tags,
        "place": place
    })

    with open(DATA_FILE, 'w') as f:
        json.dump(annotations, f, indent=2)

    return jsonify({"status": "success"}), 200

if __name__ == "__main__":
    app.run(debug=True)
