import os
import pandas as pd
import json
from openai import OpenAI
from dmm_api import fetch_dmm_data
from config import MAX_FRAMES, LLM_MODEL, OLLAMA_BASE_URL

# --- LLMクライアントの初期化 ---
try:
    # OllamaのローカルAPIを使用するように設定
    # OllamaがOpenAI互換APIを提供しているため、OpenAIクライアントを再利用
    client = OpenAI(
        base_url=OLLAMA_BASE_URL,
        api_key="ollama" # OllamaではAPIキーは不要だが、OpenAIクライアントの要件を満たすためにダミーを設定
    )
except Exception as e:
    print(f"LLMクライアントの初期化に失敗しました: {e}")
    print("config.pyのOLLAMA_BASE_URLが正しいか確認してください。")
    exit()

# --- LLMを用いたテキスト生成関数 ---
def generate_marketing_text(dmm_data, num_clips):
    """LLMを用いてマーケティングテキストを生成する"""
    
    # DMMデータがNoneの場合はフォールバック
    if not dmm_data:
        return [
            {"clip_index": i + 1, "top_text": "【データエラー】", "bottom_text": "DMMデータが取得できませんでした。"}
            for i in range(num_clips)
        ]

    system_prompt = f"""
あなたは、YouTubeショート動画の視聴者の興味を最大限に惹きつけるプロのコピーライターです。
与えられた動画のタイトルとあらすじ（説明文）を元に、以下の要件を満たすテキストを生成してください。

## 要件
1.  **構成**: 全{num_clips}つのクリップ分のテキストを生成してください。
2.  **テキスト形式**: 各クリップは「上段テキスト（キャッチーな見出し）」と「下段テキスト（詳細な説明）」の2つの要素で構成されます。
3.  **フック**: 最初のクリップは、視聴者が思わずタップしてしまうような、最も衝撃的で興味を惹く「フック」となる内容にしてください。
4.  **展開**: 2つ目以降のクリップは、物語の核心に迫りつつ、情報を小出しにして期待感を高めてください。
5.  **クリフハンガー**: 最後のクリップ（{num_clips}つ目）は、物語の結末や最も重要な情報に触れず、**「続きは本編で！」**と思わせるような**クリフハンガー**で終わらせてください。
6.  **Canvaの制約**: Canvaの一括作成機能で表示されることを考慮し、**下段テキストは1行あたり15文字程度、最大4行程度**に収まるように、簡潔に記述してください。改行は「\n」を使用してください。
7.  **出力形式**: 必ずJSON形式で出力してください。JSONのルート要素は配列（リスト）にしてください。

## 入力データ
- タイトル: {dmm_data.get('title', 'タイトルなし')}
- あらすじ（説明文）: {dmm_data.get('description', '説明なし')}
- ジャンル: {dmm_data.get('genre', 'ジャンルなし')}
- キーワード: {', '.join(dmm_data.get('keywords', []))}

## 出力JSON形式
```json
[
    {{
        "clip_index": 1,
        "top_text": "フックとなるキャッチーな見出し",
        "bottom_text": "フックの詳細な説明文\\n（15文字程度で改行）"
    }},
    // ... クリップ {num_clips} まで続く
    {{
        "clip_index": {num_clips},
        "top_text": "クリフハンガーとなる見出し",
        "bottom_text": "続きを見たくなるような煽り文\\n（15文字程度で改行）"
    }}
]
```
"""
    
    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "上記の要件に基づき、ショート動画のテキストを生成してください。"}
            ],
            response_format={"type": "json_object"}
        )
        
        json_string = response.choices[0].message.content
        parsed_data = json.loads(json_string)
        
        # LLMがresponseキーでラップしてくる場合があるため、対応
        if isinstance(parsed_data, dict) and "response" in parsed_data:
            return parsed_data["response"]
        
        # LLMがリスト形式で返さない場合（例: {"clip_1": {...}, "clip_2": {...}}）を考慮
        if isinstance(parsed_data, dict) and all(isinstance(v, dict) for v in parsed_data.values()):
            # clip_indexでソートしてリストに変換
            sorted_clips = sorted(parsed_data.values(), key=lambda x: x.get("clip_index", 999))
            return sorted_clips
            
        # それ以外の場合は、そのままリストとして返す（またはリストであることを期待）
        if isinstance(parsed_data, list):
            return parsed_data
            
        # 予期せぬ形式の場合はエラーを出す
        raise ValueError("LLMの出力形式が予期されたJSONリストまたはオブジェクトではありません。")
        
    except Exception as e:
        print(f"LLM呼び出し中にエラーが発生しました: {e}")
        # エラー時はフォールバックとしてシンプルなテキストを返す
        return [
            {"clip_index": 1, "top_text": "【緊急速報】", "bottom_text": dmm_data.get('title', 'タイトルなし')},
            {"clip_index": 2, "top_text": "物語の核心", "bottom_text": dmm_data.get('description', '説明なし')[:30] + "..."},
            {"clip_index": 3, "top_text": "衝撃の展開", "bottom_text": "続きは本編で！"},
            {"clip_index": 4, "top_text": "見逃し厳禁", "bottom_text": "今すぐDMMをチェック！"}
        ][:num_clips]

# --- メイン処理 ---
def generate_canva_csv(cid, use_mock=True):
    """Canvaの一括作成機能用のCSVデータを生成する"""
    
    # 1. DMM APIからデータを取得
    dmm_data = fetch_dmm_data(cid, use_mock=use_mock)
    if not dmm_data:
        print("DMMデータの取得に失敗しました。処理を終了します。")
        return

    # 2. LLMによるマーケティングテキストの生成
    print("LLMによるマーケティングテキストの生成を開始...")
    # MAX_FRAMESは動画の総ページ数。CTAページを1ページとして、テキストクリップは MAX_FRAMES - 1 ページ
    clips_text_data = generate_marketing_text(dmm_data, MAX_FRAMES - 1) 
    print("LLMによるテキスト生成が完了しました。")
    
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
    
    # 画像URLとLLM生成テキストを割り当て
    for i in range(1, MAX_FRAMES):
        # 画像URLを割り当て (画像が足りない場合はループして使用)
        image_urls = dmm_data.get("image_urls", [])
        if image_urls:
            image_index = (i - 1) % len(image_urls)
            new_row[f"frame_{i}_img"] = image_urls[image_index]
        else:
            new_row[f"frame_{i}_img"] = "NO_IMAGE_URL"
        
        # LLM生成テキストを割り当て
        # clips_text_dataは0から始まるインデックス
        if i - 1 < len(clips_text_data):
            text_data = clips_text_data[i - 1]
            new_row[f"frame_{i}_top"] = text_data.get("top_text", "【エラー】")
            # LLMの改行コードをCSV用に変換（CSVはセル内の改行をサポート）
            new_row[f"frame_{i}_bottom"] = text_data.get("bottom_text", "テキスト生成に失敗しました。").replace("\\n", "\n") 
        else:
            # LLMの生成数が足りなかった場合のフォールバック
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
