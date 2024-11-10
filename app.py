import os
import argparse
import json
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# コマンドライン引数の設定
parser = argparse.ArgumentParser(description="Start the image annotation tool.")
parser.add_argument("date_folder", help="Specify the date folder within the static/images directory (e.g., 08022024).")
args = parser.parse_args()

# フォルダ名に 'RGB-' プレフィックスを追加
FOLDER_PREFIX = "RGB-"
FULL_DATE_FOLDER = f"{FOLDER_PREFIX}{args.date_folder}"
DATE_FOLDER = os.path.join('static', 'images', FULL_DATE_FOLDER)

# フォルダの存在確認
if not os.path.exists(DATE_FOLDER):
    raise FileNotFoundError(f"The specified folder {DATE_FOLDER} does not exist.")

# データファイル名の設定
DATA_FILE = f'data_{args.date_folder}.json'

# データファイルの存在確認および初期化
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump([], f, ensure_ascii=False, indent=2)

def get_image_files():
    image_files = []
    # 各場所フォルダを取得
    places = [d for d in os.listdir(DATE_FOLDER) if os.path.isdir(os.path.join(DATE_FOLDER, d))]

    for place in places:
        place_path = os.path.join(DATE_FOLDER, place)
        # 画像ファイルを取得（.jpg または .png で、ファイル名に 'Dark' を含まないもの）
        images_in_place = [f for f in os.listdir(place_path) if f.endswith(('.jpg', '.png')) and 'Dark' not in f]
        
        # 既にアノテーション済みの画像を取得
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            try:
                annotations = json.load(f)
                tagged_images = set([annotation['data_name'] for annotation in annotations])
            except json.JSONDecodeError:
                tagged_images = set()

        for image in images_in_place:
            # 正しいパス形式に修正
            image_path = f"{FULL_DATE_FOLDER}/{place}/{image}"
            if image_path not in tagged_images:
                image_files.append({
                    "place": place,
                    "path": f"static/images/{image_path}"  # フロントエンド用のパス
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
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            file_content = f.read()
            if file_content.strip():
                annotations = json.loads(file_content)
            else:
                annotations = []
    except (FileNotFoundError, json.JSONDecodeError):
        annotations = []

    annotations.append({
        "data_name": image_name,  # 'RGB-08022024/place/image.jpg'
        "tags": tags,
        "place": place,
        "status": "not review"
    })

    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(annotations, f, indent=2, ensure_ascii=False)

    return jsonify({"status": "success"}), 200

if __name__ == "__main__":
    app.run(debug=True)
