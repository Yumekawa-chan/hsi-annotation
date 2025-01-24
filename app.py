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

def extract_filename(path):
    """
    指定された文字列から最後のスラッシュ以降の部分を切り抜く関数。

    Parameters:
        path (str): 対象の文字列 (ファイルパスなど)。

    Returns:
        str: 最後のスラッシュ以降の部分。
    """
    # スラッシュで区切った最後の部分を返す
    return path.split("/")[-1]       

def extract_metadata(filename):
    """
    ファイル名からidとdatetimeを抽出する
    """
    try:
        # ファイル名末尾の15文字を抽出 (例: 20240924_120431)
        id_value = filename[-19:-4]  # ".jpg"または".png"を除外
        datetime = id_value[:8]  # YYYYMMDD
        return datetime, id_value
    except IndexError:
        return None, None

def get_image_files():
    image_files = []
    # 各場所フォルダを取得
    places = [d for d in os.listdir(DATE_FOLDER) if os.path.isdir(os.path.join(DATE_FOLDER, d))]

    # 既にアノテーション済みの画像を取得
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        try:
            annotations = json.load(f)
            tagged_images = set([annotation['data_name'] for annotation in annotations])
        except json.JSONDecodeError:
            tagged_images = set()

    for place in places:
        place_path = os.path.join(DATE_FOLDER, place)
        # 画像ファイルを取得（.jpg または .png で、ファイル名に 'Dark' を含まないもの）
        images_in_place = [f for f in os.listdir(place_path) if f.endswith(('.jpg', '.png')) and 'Dark' not in f]

        for image in images_in_place:
            # ファイル名のみをチェック
            if image not in tagged_images:  # 既にアノテーションされた画像をスキップ
                image_files.append({
                    "place": place,
                    "path": f"static/images/{FULL_DATE_FOLDER}/{place}/{image}",  # フロントエンド用のパス
                    "file_name": image  # ファイル名のみ
                })

    return image_files

@app.route('/')
def index():
    image_files = get_image_files()
    if not image_files:
        return "全ての画像がアノテーション済みです．"
    return render_template('index.html', image_files=image_files)

@app.route('/save_annotations', methods=['POST'])
def save_annotations():
    data = request.json
    image_name = data['data_name']  # ファイル名のみ
    tags = data['tags']
    place = data['place']

    # メタデータを抽出
    datetime, id_value = extract_metadata(image_name)

    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            file_content = f.read()
            if file_content.strip():
                annotations = json.loads(file_content)
            else:
                annotations = []
    except (FileNotFoundError, json.JSONDecodeError):
        annotations = []

    for tag in tags:
        category, sub_category, tag_name = None, None, None

        # タグの解析: 正しいフォーマットを確認
        try:
            for part in tag.split(","):
                if ":" in part:
                    key, value = part.strip().split(":")
                    if key.strip() == "category":
                        category = value.strip()
                    elif key.strip() == "sub-category":
                        sub_category = value.strip()
                    elif key.strip() == "tag":
                        tag_name = value.strip()
        except ValueError:
            # フォーマットが不正な場合、スキップ
            continue

        # scene-tags にデータを追加
        if category and sub_category and tag_name:
            scene_tags = {
                "category": category,
                "sub-category": sub_category,
                "tags": tag_name,
            }

            annotations.append({
                "data_name": extract_filename(image_name),  # ファイル名のみ
                "datetime": datetime,     # YYYYMMDD
                "id": id_value,           # YYYYMMDD_HHMMSS
                "scene-tags": scene_tags,
                "location": place,
            })

    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(annotations, f, indent=2, ensure_ascii=False)

    return jsonify({"status": "success"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
