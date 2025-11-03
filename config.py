# DMM API 認証情報
# 実際の運用時には、ここにAPIキーとアフィリエイトIDを設定してください。
DMM_API_ID = "YOUR_DMM_API_ID"
DMM_AFFILIATE_ID = "YOUR_DMM_AFFILIATE_ID"

# LLMの設定
# OpenAI APIキーは環境変数 OPENAI_API_KEY から自動で読み込まれます。
LLM_MODEL = "gpt-4.1-mini"

# 動画生成の設定
MAX_FRAMES = 5  # 生成する動画のフレーム数（Canvaテンプレートのページ数に合わせる）

# モックデータ (開発・テスト用)
MOCK_DMM_DATA = {
    "title": "【SORA2】AI美女が描く幻想的な未来都市",
    "description": "最先端AI「SORA2」が生成した、息をのむほど美しい映像作品。未来都市、自然の風景、そしてAI美女の繊細な表情が融合した、まさに芸術。この感動をぜひご体験ください。",
    "image_urls": [
        "https://picsum.photos/1080/1920?random=1",
        "https://picsum.photos/1080/1920?random=2",
        "https://picsum.photos/1080/1920?random=3",
        "https://picsum.photos/1080/1920?random=4",
        "https://picsum.photos/1080/1920?random=5",
    ],
    "author": "AIクリエイター",
    "genre": "SF/ファンタジー",
    "keywords": ["AI美女", "未来都市", "SORA2", "幻想的", "芸術"],
    "affiliate_link": "YOUR_DMM_AFFILIATE_LINK"
}
