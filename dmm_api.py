import requests
from bs4 import BeautifulSoup
from config import DMM_API_ID, DMM_AFFILIATE_ID, MOCK_DMM_DATA

# 実際のDMM APIのURLに置き換えてください
DMM_API_ENDPOINT = "https://api.dmm.com/affiliate/v3/ItemList"

def fetch_sample_images(affiliate_url):
    """
    作品詳細ページをWebスクレイピングし、試し読み画像のURLリストを取得する。
    
    Args:
        affiliate_url (str): 作品詳細ページのアフィリエイトURL。
        
    Returns:
        list: 試し読み画像のURLリスト。
    """
    print(f"--- Webスクレイピング開始: {affiliate_url} ---")
    
    try:
        # ユーザーエージェントを設定して、スクレイピング対策を回避
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(affiliate_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # ★★★ ここが最も重要な修正箇所です ★★★
        # FANZAブックスの試し読み画像が格納されている要素を特定し、そのURLを抽出します。
        # 実際のサイト構造に合わせて、以下のセレクタを修正する必要があります。
        
        # 仮のセレクタ: 'img.sample-image' のようなクラス名を持つ要素を想定
        image_tags = soup.select('img.sample-image') 
        
        # 抽出ロジック: data-src属性やsrc属性からURLを取得
        image_urls = []
        for img in image_tags:
            # 遅延ロードされている場合は data-src を、そうでない場合は src を使用
            url = img.get('data-src') or img.get('src')
            if url and url.startswith('http'):
                image_urls.append(url)
        
        print(f"Webスクレイピング完了。{len(image_urls)}件の画像URLを取得しました。")
        return image_urls
        
    except requests.exceptions.RequestException as e:
        print(f"Webスクレイピング中にエラーが発生しました: {e}")
        return []
    except Exception as e:
        print(f"HTML解析中にエラーが発生しました: {e}")
        return []

def fetch_dmm_data(cid, use_mock=False):
    """
    DMM APIから作品情報を取得し、Webスクレイピングで試し読み画像URLを取得する。
    """
    if use_mock:
        print("--- モックデータを使用します ---")
        # モックデータに画像URLが含まれていることを前提とする
        return MOCK_DMM_DATA

    print(f"--- DMM APIからデータ取得中 (CID: {cid}) ---")
    
    params = {
        "api_id": DMM_API_ID,
        "affiliate_id": DMM_AFFILIATE_ID,
        "operation": "ItemList",
        "version": "3.00",
        "site": "DMM.com", # FANZAブックスはDMM.comサイト内のサービスです
        "service": "book", # FANZAブックスのサービスIDは "book" です
        "cid": cid,
        "output": "json",
    }
    
    try:
        response = requests.get(DMM_API_ENDPOINT, params=params)
        response.raise_for_status()
        data = response.json()
        
        # APIレスポンスから基本情報を抽出
        item = data["result"]["items"][0]
        affiliate_url = item["affiliateURL"]
        
        extracted_data = {
            "title": item["title"],
            "description": item["iteminfo"]["description"],
            "author": item["iteminfo"]["maker"][0]["name"],
            "genre": item["iteminfo"]["genre"][0]["name"],
            "keywords": [tag["name"] for tag in item["iteminfo"]["tag"]],
            "affiliate_link": affiliate_url,
            # 画像URLはWebスクレイピングで取得
            "image_urls": [], 
        }
        
        # Webスクレイピングで試し読み画像URLを取得
        sample_image_urls = fetch_sample_images(affiliate_url)
        extracted_data["image_urls"] = sample_image_urls
        
        return extracted_data
        
    except requests.exceptions.RequestException as e:
        print(f"DMM APIへのリクエストに失敗しました: {e}")
        return None
    except Exception as e:
        print(f"DMM APIレスポンスの処理中にエラーが発生しました: {e}")
        return None

if __name__ == "__main__":
    # テスト実行
    data = fetch_dmm_data("test_cid_001", use_mock=True)
    print("\n--- 取得データ構造の確認 ---")
    print(data)
    
    # 実際のAPIテスト (config.pyに認証情報を設定後)
    # data = fetch_dmm_data("test_cid_001", use_mock=False)
    # print(data)
