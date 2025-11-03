import requests
from config import DMM_API_ID, DMM_AFFILIATE_ID, MOCK_DMM_DATA

# 実際のDMM APIのURLに置き換えてください
DMM_API_ENDPOINT = "https://api.dmm.com/affiliate/v3/ItemList"

def fetch_dmm_data(cid, use_mock=True):
    """
    DMM APIから動画情報を取得する。
    
    Args:
        cid (str): 取得したい動画のコンテンツID。
        use_mock (bool): Trueの場合、モックデータを使用する。
        
    Returns:
        dict: 動画情報を含む辞書。
    """
    if use_mock:
        print("--- モックデータを使用します ---")
        return MOCK_DMM_DATA

    print(f"--- DMM APIからデータ取得中 (CID: {cid}) ---")
    
    params = {
        "api_id": DMM_API_ID,
        "affiliate_id": DMM_AFFILIATE_ID,
        "operation": "ItemList",
        "version": "3.00",
        "site": "DMM.com", # 適切なサイト名に置き換えてください
        "service": "videoa", # 適切なサービス名に置き換えてください
        "cid": cid,
        "output": "json",
    }
    
    try:
        response = requests.get(DMM_API_ENDPOINT, params=params)
        response.raise_for_status()
        data = response.json()
        
        # ここにAPIレスポンスから必要な情報を抽出するロジックを実装
        # 例: data["result"]["items"][0] から title, description, image_urlsなどを抽出
        
        # 抽出したデータを以下の形式で返す
        extracted_data = {
            "title": data["result"]["items"][0]["title"],
            "description": data["result"]["items"][0]["iteminfo"]["description"],
            "image_urls": [data["result"]["items"][0]["imageURL"]["large"]], # 適切な画像URLに置き換えてください
            "author": data["result"]["items"][0]["iteminfo"]["maker"][0]["name"],
            "genre": data["result"]["items"][0]["iteminfo"]["genre"][0]["name"],
            "keywords": [tag["name"] for tag in data["result"]["items"][0]["iteminfo"]["tag"]],
            "affiliate_link": data["result"]["items"][0]["affiliateURL"],
        }
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
