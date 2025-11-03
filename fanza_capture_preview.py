# fanza_capture_preview.py (rev4: async expect_popup + gate fix + per-page center click)
import asyncio, os, re, argparse, hashlib
from urllib.parse import urlparse
from playwright.async_api import async_playwright, TimeoutError as PWTimeout, Page, Frame

VIEWPORT = {"width": 1080, "height": 1920}
SHOT_DELAY_MS = 800
MAX_PAGES_DEFAULT = 15
OUT_ROOT = "captures"

PREVIEW_TRIGGERS = [
    'text=試し読み', 'text=立ち読み', 'text=サンプル',
    'button:has-text("試し読み")', 'button:has-text("立ち読み")'
]

VIEWER_SELECTORS = [
    'div[id*="viewer"]',
    'div[class*="viewer"]',
    'div[class*="reader"]',
    'div[class*="canvas"]',
    'div[role="document"]',
    'canvas'
]

# 年齢ゲートや同意ボタン想定
GATE_OK = [
    'text=はい',
    'text=ENTER',
    'text=18歳以上',
    'text=同意して入場',
    'button:has-text("はい")',
    'button:has-text("同意")',
    'button:has-text("ENTER")'
]

def slug_from_url(url: str) -> str:
    p = urlparse(url)
    m = re.search(r'cid=([^/]+)/?', url)
    if m: return m.group(1)
    tail = os.path.basename(p.path.rstrip('/')) or 'work'
    return re.sub(r'[^a-zA-Z0-9_-]+', '_', tail)

async def click_if_visible(scope: Page | Frame, selectors):
    for sel in selectors:
        try:
            loc = scope.locator(sel).first
            if await loc.count() > 0 and await loc.is_visible():
                await loc.click()
                await scope.wait_for_timeout(500)
                return True
        except Exception:
            pass
    return False

async def bypass_age_gate(page: Page):
    # 複数回トライ（サイト側で段階がある場合あり）
    for _ in range(3):
        clicked = await click_if_visible(page, GATE_OK)
        if clicked:
            await page.wait_for_timeout(600)
        # キー操作でも突破を試す
        try:
            await page.keyboard.press("Enter")
            await page.wait_for_timeout(400)
            await page.keyboard.press("Space")
            await page.wait_for_timeout(400)
        except Exception:
            pass

async def find_viewer(scope: Page | Frame):
    # iframe内を優先的に探索
    frames = scope.frames if isinstance(scope, Page) else scope.page.frames
    for frame in frames:
        try:
            for sel in VIEWER_SELECTORS:
                loc = frame.locator(sel).first
                if await loc.count() > 0 and await loc.is_visible():
                    canv = loc.locator("canvas").first
                    if await canv.count() > 0 and await canv.is_visible():
                        return frame, canv
                    return frame, loc
        except Exception:
            continue
    # 直下探索
    for sel in VIEWER_SELECTORS:
        loc = scope.locator(sel).first
        if await loc.count() > 0 and await loc.is_visible():
            canv = loc.locator("canvas").first
            if await canv.count() > 0 and await canv.is_visible():
                return scope, canv
            return scope, loc
    return scope, scope.locator("body")

async def center_click(frame, viewer):
    # UIを消すために中央をクリック（要素相対座標で）
    await viewer.scroll_into_view_if_needed()
    box = await viewer.bounding_box()
    if not box:
        return
    rel_x = box["width"] * 0.5
    rel_y = box["height"] * 0.5
    await viewer.click(position={"x": rel_x, "y": rel_y})

async def left_advance(frame, viewer):
    # 左半分クリックで次ページ（要素相対座標で）
    await viewer.scroll_into_view_if_needed()
    box = await viewer.bounding_box()
    if not box:
        return False
    rel_x = box["width"] * 0.25
    rel_y = box["height"] * 0.5
    await viewer.click(position={"x": rel_x, "y": rel_y})
    await (frame.page if hasattr(frame, "page") else frame).wait_for_timeout(SHOT_DELAY_MS)
    return True

def sha1file(path):
    h = hashlib.sha1()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()

async def main(url: str, max_pages: int, headful: bool):
    folder = os.path.join(OUT_ROOT, slug_from_url(url))
    os.makedirs(folder, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=not headful)
        ctx = await browser.new_context(viewport=VIEWPORT)
        page = await ctx.new_page()

        # 1) アクセス
        await page.goto(url, wait_until="domcontentloaded")

        # 2) 年齢ゲート突破（複数回）
        await bypass_age_gate(page)

        # 3) 試し読み起動（ポップアップ対応：async with）
        view: Page = page
        try:
            # まずpopup期待で試す
            async with page.expect_popup() as popup_info:
                await click_if_visible(page, PREVIEW_TRIGGERS)
            popup = await popup_info.value
            if popup:
                view = popup
        except Exception:
            # ポップアップが無い or 既に同タブ遷移するタイプ
            clicked = await click_if_visible(page, PREVIEW_TRIGGERS)
            if clicked:
                view = page  # 同タブ

        await view.wait_for_timeout(1200)

        # 念のため再度ゲート突破（ビューア側で出る場合あり）
        await bypass_age_gate(view)

        # 4) ビューア特定
        frame, viewer = await find_viewer(view)
        await frame.wait_for_timeout(600)

        prev_hash = None
        for i in range(1, max_pages + 1):
            # ★ 毎ページ開始時に中央クリックでUIを消す
            await center_click(frame, viewer)
            await frame.wait_for_timeout(200)

            path = os.path.join(folder, f"page_{i:02d}.png")
            await viewer.screenshot(path=path)
            curr_hash = sha1file(path)

            if prev_hash and curr_hash == prev_hash:
                # 同じ画像 → 左クリックで送り再撮影
                await left_advance(frame, viewer)
                await viewer.screenshot(path=path)
                curr_hash2 = sha1file(path)
                if curr_hash2 == curr_hash:
                    print(f"[INFO] same image again at {i}, stopping.")
                    break

            print(f"[SHOT] {path}")
            prev_hash = curr_hash

            # 次ページへ
            moved = await left_advance(frame, viewer)
            if not moved:
                print("[INFO] cannot advance by left click, stopping.")
                break

        await browser.close()

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True, help="FANZAブックス 作品URL（試し読み可能）")
    ap.add_argument("--pages", type=int, default=MAX_PAGES_DEFAULT)
    ap.add_argument("--show", action="store_true", help="ブラウザを表示（デバッグ用）")
    args = ap.parse_args()
    asyncio.run(main(args.url, args.pages, args.show))
