import re

def generate_rule_based_text(dmm_data, num_clips):
    """
    DMMのメタデータから、ルールベースでショート動画用のテキストを生成する。
    
    Args:
        dmm_data (dict): DMMの動画メタデータ。
        num_clips (int): 生成するクリップの数（CTAクリップを除く）。
        
    Returns:
        list: 各クリップのテキストデータを含む辞書のリスト。
    """
    
    title = dmm_data.get('title', '衝撃の新作')
    description = dmm_data.get('description', '物語の核心に迫る！')
    author = dmm_data.get('author', '作者不明')
    genre = dmm_data.get('genre', 'ジャンル不明')
    
    # 1. あらすじを分割し、クリフハンガーを作る
    # 句読点（。、.）で分割し、簡潔な文のリストにする
    sentences = re.split(r'[。、．\.]', description)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    # 2. 各クリップのテキストを生成
    clips_text_data = []
    
    # --- クリップ 1: フック ---
    # タイトルとジャンルを組み合わせたフック
    hook_top = f"【{genre}】の常識を覆す！"
    hook_bottom = f"衝撃の新作『{title}』\n見逃し厳禁！"
    clips_text_data.append({"clip_index": 1, "top_text": hook_top, "bottom_text": hook_bottom})
    
    # --- クリップ 2: 導入/設定 ---
    # あらすじの最初の部分を使用
    if len(sentences) >= 1:
        intro_top = f"物語の始まりは…"
        intro_bottom = sentences[0]
        clips_text_data.append({"clip_index": 2, "top_text": intro_top, "bottom_text": intro_bottom})
    
    # --- クリップ 3: 展開/葛藤 ---
    # あらすじの中盤を使用
    if len(sentences) >= 2:
        mid_top = f"そして、運命の歯車が回り出す"
        mid_bottom = sentences[1]
        clips_text_data.append({"clip_index": 3, "top_text": mid_top, "bottom_text": mid_bottom})
    
    # --- クリップ 4: クライマックス/クリフハンガー ---
    # あらすじの最後の部分を使い、途中でカット
    if len(sentences) >= 3:
        cliff_top = f"この結末は、誰も予想できない…"
        # 最後の文を途中でカットしてクリフハンガーにする
        cliff_sentence = sentences[2]
        cut_point = len(cliff_sentence) // 2
        cliff_bottom = cliff_sentence[:cut_point] + "…続きは本編で！"
        clips_text_data.append({"clip_index": 4, "top_text": cliff_top, "bottom_text": cliff_bottom})
    
    # 必要なクリップ数に満たない場合は、汎用的なクリップで埋める
    while len(clips_text_data) < num_clips:
        clips_text_data.append({
            "clip_index": len(clips_text_data) + 1,
            "top_text": "【見逃し厳禁】",
            "bottom_text": "今すぐDMMをチェック！"
        })
        
    return clips_text_data[:num_clips]

if __name__ == "__main__":
    # モックデータ (config.pyからインポート)
    from config import MOCK_DMM_DATA
    
    print("--- ルールベースのテキスト生成の実行 ---")
    generated_texts = generate_rule_based_text(MOCK_DMM_DATA, num_clips=4)
    
    print("\n--- 生成結果 ---")
    for item in generated_texts:
        print(f"クリップ {item['clip_index']}:")
        print(f"  上段: {item['top_text']}")
        print(f"  下段: {item['bottom_text'].replace('\n', ' ')}")
        print("-" * 20)
