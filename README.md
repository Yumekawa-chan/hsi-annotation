
# 画像アノテーションツール

このプロジェクトは、指定したフォルダ内の画像を表示し、ユーザーがタグを入力することでアノテーションを行うためのシンプルなツールです。`Flask`をバックエンドとして使用し、`HTML`、`JavaScript`を用いたインターフェースで、タグの入力・保存が可能です。

## 目次
- [機能](#機能)
- [必要な環境](#必要な環境)
- [セットアップ手順](#セットアップ手順)
- [使い方](#使い方)
- [実行方法](#実行方法)
- [トラブルシューティング](#トラブルシューティング)

## 機能
- ユーザーが指定したフォルダ内の画像を1枚ずつ表示
- 表示された画像に対してタグを入力し、次へ進む機能
- `Dark` という文字列を含む画像ファイルはスキップ
- 入力されたタグは`JSON`形式で保存され、後から確認可能
- パステルカラーを基調とした「ゆめかわいい」デザイン

## 必要な環境
- Python 3.x
- Flask 2.x
- Node.js (Tailwind CSSを使う場合)

## セットアップ手順
1. Flaskをインストールします。

   ```bash
   pip install Flask
   ```

2. Tailwind CSSを使用するために、Node.jsをインストールし、必要なパッケージをセットアップします。

   ```bash
   npm init -y
   npm install -D tailwindcss
   npx tailwindcss init
   ```

3. `tailwind.config.js` にHTMLとJSファイルを読み込む設定を追加します。

   ```javascript
   module.exports = {
     content: ['./templates/**/*.html', './static/**/*.js'],
     theme: {
       extend: {},
     },
     plugins: [],
   }
   ```

4. `static/css/tailwind.css` を作成し、Tailwindの基本設定を追加します。

   ```css
   @tailwind base;
   @tailwind components;
   @tailwind utilities;
   ```

5. Tailwindをビルドします。

   ```bash
   npx tailwindcss -i ./static/css/tailwind.css -o ./static/css/output.css --watch
   ```

## 使い方
1. アノテーション対象の画像フォルダを `static/images/` の中に配置してください。
   例: `static/images/rgb-2024-07-31/`

2. `app.py` を実行し、画像フォルダを指定します。

   ```bash
   python app.py rgb-2024-07-31
   ```

   このコマンドを実行することで、`static/images/rgb-2024-07-31/` 内の画像が表示され、アノテーションが可能になります。

3. タグをカンマ区切りで入力し、次へボタンを押すことで、次の画像が表示されます。タグ情報は `data.json` に保存されます。

## 実行方法
アプリケーションを実行するには、以下の手順でコマンドを実行します。

```bash
python app.py <image_folder>
```

例えば、`rgb-2024-07-31` というフォルダを指定する場合は以下のように実行します。

```bash
python app.py rgb-2024-07-31
```

ブラウザで `http://127.0.0.1:5000` にアクセスして、アノテーションツールを利用できます。

![image](https://github.com/user-attachments/assets/a049c5eb-94b2-4263-8fba-d2625828bb70)


## トラブルシューティング

1. **画像が表示されない場合**：
   - `Dark` という文字列がファイル名に含まれている画像は自動的にスキップされますので、これが原因で画像が表示されない可能性があります。
   - 画像パスが正しいか、ファイルが正しく配置されているかを確認してください。
   - ブラウザのキャッシュをクリアし、最新の状態を読み込んでください。

2. **JSONファイルが正しく保存されない場合**：
   - `data.json` ファイルが正しく作成されているか確認し、書き込み権限があるか確認してください。
   - アプリケーションが読み込みや書き込みのエラーを出していないか、ログを確認してください。
