import os
import pandas as pd
import json
# from openai import OpenAI # LLM依存を削除
from dmm_api import fetch_dmm_data
from config import MAX_FRAMES, MOCK_DMM_DATA
from rule_based_text_generator import generate_rule_based_text # 新しいルールベースの関数をインポート

# --- LLMクライアントの初期化を削除 ---
# try:
#     client = OpenAI()
# except Exception as e:
#     print(f"OpenAIクライアントの初期化に失敗しました: {e}")
#     print("環境変数 OPENAI_API_KEY が設定されているか確認してください。")
#     exit()

# --- LLMを用いたテキスト生成関数をルールベースの関数に置き換え ---
def generate_marketing_text(dmm_data, num_clips):
    """ルールベースでマーケティングテキストを生成する"""
    return generate_rule_based_text(dmm_data, num_clips)

# --- メイン処理 ---
def generate_canva_csv(cid, use_mock=True):
    """Canvaの一括作成機能用のCSVデータを生成する"""
    
    # 1. DMM APIからデータを取得
    dmm_data = fetch_dmm_data(cid, use_mock=use_mock)
    if not dmm_data:
        print("DMMデータの取得に失敗しました。処理を終了します。")
        return

    # 2. ルールベースによるマーケティングテキストの生成
    print("ルールベースによるマーケティングテキストの生成を開始...")
    # MAX_FRAMESは動画の総ページ数。CTAページを1ページとして、テキストクリップは MAX_FRAMES - 1 ページ
    clips_text_data = generate_marketing_text(dmm_data, MAX_FRAMES - 1) 
    print("テキスト生成が完了しました。")
    
    # 3. Canva用のデータフレームを初期化
    columns = {}
    for i in range(1, MAX_FRAMES): # クリップ 1 から MAX_FRAMES-1 まで
        columns[f"frame_{i}_img"] = []
        columns[f"frame_{i}_top"] = []
        columns[f"frame_{i}_bottom"] = []
    
    # 最後のCTAページ用の列
    columns["cta_img"] = [] # CTAページ用の画像
    columns["title"] = []
    columns["author"] = []
    columns["cta_text"] = []
    columns["affiliate_link"] = []
    
    df = pd.DataFrame(columns)

    # 4. 各フレームのデータを生成
    new_row = {}
    
    # 画像URLと生成テキストを割り当て
    for i in range(1, MAX_FRAMES):
        # 画像URLを割り当て (画像が足りない場合はループして使用)
        image_urls = dmm_data.get("image_urls", [])
        if image_urls:
            image_index = (i - 1) % len(image_urls)
            new_row[f"frame_{i}_img"] = image_urls[image_index]
        else:
            new_row[f"frame_{i}_img"] = "NO_IMAGE_URL"
        
        # 生成テキストを割り当て
        # clips_text_dataは0から始まるインデックス
        if i - 1 < len(clips_text_data):
            text_data = clips_text_data[i - 1]
            new_row[f"frame_{i}_top"] = text_data.get("top_text", "【エラー】")
            # 改行コードをCSV用に変換（CSVはセル内の改行をサポート）
            new_row[f"frame_{i}_bottom"] = text_data.get("bottom_text", "テキスト生成に失敗しました。").replace("\\n", "\n") 
        else:
            # 生成数が足りなかった場合のフォールバック
            new_row[f"frame_{i}_top"] = "【エラー】"
            new_row[f"frame_{i}_bottom"] = "テキスト生成数が不足しています。"

    # 5. 最後のCTAページのデータを設定
    image_urls = dmm_data.get("image_urls", [])
    new_row["cta_img"] = image_urls[-1] if image_urls else "NO_IMAGE_URL"
    new_row["title"] = dmm_data.get("title", "タイトルなし")
    new_row["author"] = f"引用: {dmm_data.get('author', '作者不明')}"
    new_row["cta_text"] = "続きはDMMで！"
    new_row["affiliate_link"] = dmm_data.get("affiliate_link", "YOUR_DMM_AFFILIATE_LINK")

    # 6. データフレームに行を追加
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    # 7. CSVファイルとして出力
    output_filename = "canva_import_data.csv"
    # CanvaがUTF-8 BOM付きCSVを推奨するため、'utf-8-sig'を使用
    df.to_csv(output_filename, index=False, encoding='utf-8-sig')
    print(f"\nCanva用の最終CSVファイルを生成しました: {output_filename}")
    return output_filename

if __name__ == "__main__":
    # 実行例: モックデータを使用
    generate_canva_csv(cid="test_cid_001", use_mock=True)
    
    # 実行例: 実際のDMM APIを使用 (config.pyに認証情報を設定後)
    # generate_canva_csv(cid="実際のコンテンツID", use_mock=False)
