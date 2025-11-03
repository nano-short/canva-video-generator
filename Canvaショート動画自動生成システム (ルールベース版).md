# Canvaショート動画自動生成システム (Ollama/OpenAI対応版)

このプロジェクトは、DMMなどの外部データソースから取得した情報を元に、大規模言語モデル (LLM) を活用してマーケティング効果の高いテキストを自動生成し、Canvaの「一括作成」機能にインポートするためのCSVファイルを生成するシステムです。

**OpenAI APIとローカルLLM (Ollama) の両方に対応し、コストとクオリティの両立を目指します。**

## 特徴

- **LLMによるテキスト自動生成**: DMMのあらすじを「フック→展開→クリフハンガー」の構成にアレンジし、視聴者の興味を惹くコピーを自動生成します。
- **Ollama対応**: ローカルLLM (Llama 3など) を使用することで、**OpenAI APIの費用をかけずに**高いクオリティのテキスト生成が可能です。
- **Canva連携の最適化**: Canvaの「一括作成」機能に合わせたCSV形式で出力し、動画の量産を可能にします。
- **運用に配慮した設計**: 設定ファイル (`config.py`) とAPIラッパー (`dmm_api.py`) を分離し、実際のDMM API連携を容易にしました。

## ファイル構成

| ファイル名 | 役割 |
| :--- | :--- |
| `final_canva_csv_generator.py` | メインの実行スクリプト。LLM連携とCSV生成ロジックを実装。 |
| `config.py` | DMM APIキー、LLM設定（Ollama/OpenAI）、動画設定、モックデータなどを格納。 |
| `dmm_api.py` | DMM APIからデータを取得するためのラッパー関数を実装。 |
| `requirements.txt` | 必要なPythonライブラリを記述。 |
| `canva_import_data.csv` | スクリプト実行時に生成されるCanvaインポート用CSVファイル。 |

## 必要な環境

- Python 3.x
- **ローカルLLMを使用する場合**: Ollamaのインストールと、使用するモデル（例: `llama3`）のダウンロード。

## セットアップ

1.  **リポジトリのクローン**
    ```bash
    git clone [GitHubリポジトリURL]
    cd canva-video-generator
    ```

2.  **依存関係のインストール**
    ```bash
    pip install -r requirements.txt
    ```

3.  **LLMとAPIキーの設定**
    - **ローカルLLM (Ollama) を使用する場合**:
        - Ollamaを起動し、モデルをダウンロードします (`ollama run llama3`)。
        - `config.py` の `OLLAMA_BASE_URL` と `LLM_MODEL` を設定します。
    - **OpenAI APIを使用する場合**:
        - 環境変数 `OPENAI_API_KEY` を設定します。
        - `config.py` の `OLLAMA_BASE_URL` をコメントアウトし、`LLM_MODEL` を `gpt-4.1-mini` などに設定します。
    - `config.py` の `DMM_API_ID` と `DMM_AFFILIATE_ID` をご自身の情報に置き換えてください。

## 使用方法

1.  **DMM API連携の実装**:
    - `dmm_api.py` を開き、`fetch_dmm_data` 関数内のAPIレスポンスから必要な情報を抽出するロジックを、ご自身のDMM APIのレスポンス形式に合わせて実装してください。

2.  **スクリプトの実行**:
    - **モックデータでテストする場合**:
      ```bash
      python final_canva_csv_generator.py
      ```
    - **実際のDMM APIを使用する場合**:
      `final_canva_csv_generator.py` の末尾にある `if __name__ == "__main__":` ブロックを以下のように変更し、実行してください。
      ```python
      if __name__ == "__main__":
          # 実行例: 実際のDMM APIを使用 (config.pyに認証情報を設定後)
          generate_canva_csv(cid="実際のコンテンツID", use_mock=False)
      ```
      ```bash
      python final_canva_csv_generator.py
      ```

3.  `canva_import_data.csv` が生成されます。
4.  このCSVファイルをCanvaの「一括作成」機能にインポートし、動画テンプレートとマッピングして動画を生成します。

## Canvaテンプレートの設計

Canva側では、以下の列名に対応する要素を配置したテンプレートが必要です。

| 列名 | 用途 |
| :--- | :--- |
| `frame_i_img` | 各フレームの背景画像URL |
| `frame_i_top` | 各フレームの上段テキスト（見出し） |
| `frame_i_bottom` | 各フレームの下段テキスト（詳細） |
| `cta_img` | CTAページの背景画像URL |
| `title` | CTAページに表示する作品タイトル |
| `author` | CTAページに表示する引用元/作者名 |
| `cta_text` | CTAページに表示する行動喚起テキスト |
| `affiliate_link` | CTAページに表示するアフィリエイトリンク |
