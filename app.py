import os
import argparse
import json
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# コマンドライン引数を処理する
parser = argparse.ArgumentParser(description="Start the image annotation tool.")
parser.add_argument("image_folder", help="Specify the image folder within the static/images directory.")
args = parser.parse_args()

# 画像フォルダのパスを引数で指定
IMAGE_FOLDER = os.path.join('static', 'images', args.image_folder)

# もしフォルダが存在しなければエラーメッセージを表示
if not os.path.exists(IMAGE_FOLDER):
    raise FileNotFoundError(f"The specified folder {IMAGE_FOLDER} does not exist.")

# フォルダ内の画像リストを取得（jpgまたはpng形式）
# "Dark"という文字列が含まれているファイルをスキップ
image_files = [f'{args.image_folder}/{f}' for f in os.listdir(IMAGE_FOLDER)
               if f.endswith(('.jpg', '.png')) and 'Dark' not in f]

# タグを保存するJSONファイルのパス
DATA_FILE = 'data.json'

# もしdata.jsonがなければ作成
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump([], f)

@app.route('/')
def index():
    if not image_files:
        return "No valid images to display."
    return render_template('index.html', image_files=image_files)


# タグの保存
@app.route('/save_annotations', methods=['POST'])
def save_annotations():
    data = request.json
    image_name = data['data_name']
    tags = data['tags']

    # 既存のJSONを読み込む
    try:
        with open(DATA_FILE, 'r') as f:
            # ファイルが空でないか確認し、空なら空のリストを設定
            file_content = f.read()
            if file_content.strip():
                annotations = json.loads(file_content)
            else:
                annotations = []
    except (FileNotFoundError, json.JSONDecodeError):
        # ファイルが存在しないか、JSONの読み込みエラーが発生した場合は空のリストを使用
        annotations = []

    # 新しいデータを追加
    annotations.append({
        "data_name": image_name,
        "tags": tags
    })

    # JSONに書き込み
    with open(DATA_FILE, 'w') as f:
        json.dump(annotations, f, indent=2)

    return jsonify({"status": "success"}), 200

if __name__ == "__main__":
    app.run(debug=True)
