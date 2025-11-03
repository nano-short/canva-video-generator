# --- DMM API設定 ---
# 実際のDMM API IDとアフィリエイトIDに置き換えてください
DMM_API_ID = "YOUR_DMM_API_ID"
DMM_AFFILIATE_ID = "YOUR_DMM_AFFILIATE_ID"

# --- 動画生成設定 ---
MAX_FRAMES = 5  # 生成する動画のフレーム数（Canvaテンプレートのページ数に合わせる）

# --- LLM設定 (Ollama/OpenAI互換) ---
# ローカルLLM (Ollama) を使用する場合:
# 1. Ollamaをインストールし、Llama 3などのモデルをダウンロードしてください。
# 2. OLLAMA_BASE_URLをOllamaのエンドポイントに設定してください。
# 3. LLM_MODELをダウンロードしたモデル名に設定してください。
OLLAMA_BASE_URL = "http://localhost:11434/v1"
LLM_MODEL = "llama3" # 例: llama3, mistral, gemma:7b

# --- モックデータ (DMM APIから取得されるデータを想定) ---
# 実際にはDMM APIから取得したデータに置き換える
MOCK_DMM_DATA = {
    "title": "【SORA2】AI美女が描く幻想的な未来都市",
    "description": "最先端AI「SORA2」が生成した、息をのむほど美しい映像作品。未来都市、自然の風景、そしてAI美女の繊細な表情が融合した、まさに芸術。この感動をぜひご体験ください。",
    "image_urls": [
        "https://picsum.photos/1080/1920?random=1", # Frame 1
        "https://picsum.photos/1080/1920?random=2", # Frame 2
        "https://picsum.photos/1080/1920?random=3", # Frame 3
        "https://picsum.photos/1080/1920?random=4", # Frame 4
        "https://picsum.photos/1080/1920?random=5", # Frame 5
    ],
    "author": "AIクリエイター",
    "genre": "SF/ファンタジー",
    "keywords": ["AI美女", "未来都市", "SORA2", "幻想的", "芸術"],
    "affiliate_link": "YOUR_DMM_AFFILIATE_LINK" # 実際のリンクに置き換える
}
