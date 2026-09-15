#!/usr/bin/env python3
"""Fallback updater for Douyin /video/ cards blocked on the normal Douyin web page.

The main updater remains authoritative. This helper only runs afterwards and only
tries public fallback pages for Douyin video items that may be hidden behind a
login / CAPTCHA on www.douyin.com.

Fallback order:
1. https://jingxuan.douyin.com/m/video/<aweme_id>
2. https://www.douyin.com/jingxuan?modal_id=<aweme_id>

Safety rule: if an exact item cannot be verified with at least three interaction
metrics, the existing social-data.json values are kept unchanged.
"""
from __future__ import annotations

import argparse
import json
import math
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "assets" / "social-data.json"
DEBUG_DIR = ROOT / "debug-social"
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36"
)

ALIASES = {
    "likes": ("digg_count", "like_count", "likes"),
    "comments": ("comment_count", "comments_count", "comments"),
    "favorites": ("collect_count", "favorite_count", "favorites"),
    "shares": ("share_count", "shares"),
}


def log(message: str) -> None:
    print(message, flush=True)


def parse_number(value: Any) -> int | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value if value >= 0 else None
    if isinstance(value, float):
        return int(value) if math.isfinite(value) and value >= 0 else None

    text = str(value).strip().replace(",", "").replace("＋", "+")
    text = re.sub(r"\s+", "", text)
    match = re.fullmatch(
        r"([0-9]+(?:\.[0-9]+)?)(万|w|W|亿|k|K|m|M|b|B)?\+?", text
    )
    if not match:
        return None
    unit = match.group(2)
    multiplier = {
        None: 1,
        "k": 1_000, "K": 1_000,
        "w": 10_000, "W": 10_000, "万": 10_000,
        "亿": 100_000_000,
        "m": 1_000_000, "M": 1_000_000,
        "b": 1_000_000_000, "B": 1_000_000_000,
    }[unit]
    return int(round(float(match.group(1)) * multiplier))


def metric_map(mapping: dict[str, Any]) -> dict[str, int]:
    found: dict[str, int] = {}
    for output_key, aliases in ALIASES.items():
        for key in aliases:
            if key in mapping:
                number = parse_number(mapping.get(key))
                if number is not None:
                    found[output_key] = number
                    break
    return found


def recursively_find_exact_stats(node: Any, wanted_id: str) -> dict[str, int]:
    """Only accept metrics attached to the exact requested aweme/video id."""
    best: dict[str, int] = {}

    def walk(value: Any, inside_exact: bool = False) -> None:
        nonlocal best
        if isinstance(value, dict):
            ids = {
                str(value.get(key))
                for key in (
                    "aweme_id", "item_id", "video_id", "note_id",
                    "id", "group_id", "modal_id",
                )
                if value.get(key) is not None
            }
            exact = inside_exact or wanted_id in ids

            candidates: list[dict[str, Any]] = []
            for key in ("statistics", "stats", "stat", "aweme_detail", "item"):
                child = value.get(key)
                if isinstance(child, dict):
                    candidates.append(child)
            candidates.append(value)

            if exact:
                for candidate in candidates:
                    found = metric_map(candidate)
                    if len(found) > len(best):
                        best = found

            for child in value.values():
                walk(child, exact)

        elif isinstance(value, list):
            for child in value:
                walk(child, inside_exact)

    walk(node)
    return best


def stats_from_embedded_html(source: str, wanted_id: str) -> dict[str, int]:
    """Inspect embedded React/SSR JSON without trusting unrelated recommendation cards."""
    best: dict[str, int] = {}
    positions = [m.start() for m in re.finditer(re.escape(wanted_id), source)]
    for pos in positions[:30]:
        start = max(0, pos - 20_000)
        end = min(len(source), pos + 80_000)
        segment = source[start:end]

        found: dict[str, int] = {}
        for output_key, aliases in ALIASES.items():
            for alias in aliases:
                patterns = (
                    rf'["\']{re.escape(alias)}["\']\s*:\s*["\']?([0-9]+(?:\.[0-9]+)?(?:万|亿|[kKmMwWbB])?)',
                    rf'\\"{re.escape(alias)}\\"\s*:\s*["\\]*([0-9]+)',
                )
                number = None
                for pattern in patterns:
                    match = re.search(pattern, segment)
                    if match:
                        number = parse_number(match.group(1))
                        if number is not None:
                            break
                if number is not None:
                    found[output_key] = number
                    break

        if len(found) > len(best):
            best = found
    return best


def stats_from_semantic_dom(page: Any) -> dict[str, int]:
    """Last-resort semantic counters; hashed CSS class names are intentionally ignored."""
    selector_map = {
        "likes": (
            '[data-e2e*="digg"]', '[data-e2e*="like"]',
            '[class*="like-count"]', '[class*="digg-count"]',
        ),
        "comments": (
            '[data-e2e*="comment"]', '[class*="comment-count"]',
        ),
        "favorites": (
            '[data-e2e*="collect"]', '[data-e2e*="favorite"]',
            '[class*="collect-count"]',
        ),
        "shares": (
            '[data-e2e*="share"]', '[class*="share-count"]',
        ),
    }
    found: dict[str, int] = {}
    for key, selectors in selector_map.items():
        for selector in selectors:
            try:
                locator = page.locator(selector).first
                if not locator.count():
                    continue
                text = locator.inner_text(timeout=2_000).strip()
                tokens = re.findall(r"[0-9]+(?:\.[0-9]+)?(?:万|亿|[kKmMwWbB])?", text)
                for token in reversed(tokens):
                    number = parse_number(token)
                    if number is not None:
                        found[key] = number
                        break
                if key in found:
                    break
            except Exception:
                continue
    return found


def write_debug(page: Any, item_id: str, source_name: str, message: str) -> None:
    DEBUG_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    base = DEBUG_DIR / f"{stamp}-douyin-fallback-{source_name}-{item_id}"
    try:
        page.screenshot(path=str(base.with_suffix(".png")), full_page=True)
    except Exception:
        pass
    try:
        base.with_suffix(".html").write_text(page.content(), encoding="utf-8")
    except Exception:
        pass
    base.with_suffix(".txt").write_text(message, encoding="utf-8")


def try_candidate(context: Any, item_id: str, source_name: str, url: str, debug: bool) -> dict[str, int]:
    page = context.new_page()
    captured: dict[str, int] = {}

    def on_response(response: Any) -> None:
        nonlocal captured
        try:
            ctype = (response.headers or {}).get("content-type", "")
            if "json" not in ctype.lower():
                return
            payload = response.json()
            stats = recursively_find_exact_stats(payload, item_id)
            if len(stats) > len(captured):
                captured = stats
        except Exception:
            return

    page.on("response", on_response)
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=60_000)
        page.wait_for_timeout(8_000)

        try:
            source = page.content()
        except Exception:
            source = ""

        embedded = stats_from_embedded_html(source, item_id)
        if len(embedded) > len(captured):
            captured = embedded

        if len(captured) < 3:
            dom_stats = stats_from_semantic_dom(page)
            if len(dom_stats) > len(captured):
                captured = dom_stats

        body = ""
        try:
            body = page.locator("body").inner_text(timeout=5_000)
        except Exception:
            pass

        blocked = any(
            word in body
            for word in ("验证码", "安全验证", "扫码登录", "登录后", "访问频繁")
        )

        if len(captured) >= 3:
            log(
                f"[douyin-fallback/{source_name}] {item_id}: "
                f"{json.dumps(captured, ensure_ascii=False)}"
            )
            if debug:
                write_debug(page, item_id, source_name, f"success\nurl={url}\nstats={captured}")
            return captured

        log(
            f"[douyin-fallback/{source_name}] {item_id}: no metrics"
            + (" (blocked)" if blocked else "")
        )
        if debug:
            write_debug(
                page,
                item_id,
                source_name,
                f"no metrics\nurl={url}\nblocked={blocked}\nbody_head={body[:2000]}",
            )
        return {}
    except Exception as exc:
        log(f"[douyin-fallback/{source_name}] {item_id}: {type(exc).__name__}: {exc}")
        if debug:
            write_debug(page, item_id, source_name, f"exception\nurl={url}\n{exc}")
        return {}
    finally:
        page.close()


def update_target(target: dict[str, Any], stats: dict[str, int]) -> bool:
    changed = False
    for key in ("likes", "comments", "favorites", "shares"):
        if key in stats and target.get(key) != stats[key]:
            target[key] = stats[key]
            changed = True
    return changed


def refresh_summary(data: dict[str, Any]) -> None:
    douyin = data.get("content", {}).get("douyin", {})
    likes = [
        item.get("likes")
        for item in douyin.values()
        if isinstance(item, dict) and isinstance(item.get("likes"), int)
    ]
    if likes:
        # Keep the existing media-kit convention: representative likes rounded to 10k.
        data.setdefault("summary", {})["representativeDouyinLikes"] = (
            int(round(sum(likes) / 10_000.0)) * 10_000
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    douyin = data.get("content", {}).get("douyin", {})
    if not isinstance(douyin, dict):
        log("[douyin-fallback] no content.douyin object; nothing to do")
        return 0

    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise SystemExit("Install playwright before running this helper") from exc

    changed = False

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
            ],
        )
        context = browser.new_context(
            user_agent=UA,
            locale="zh-CN",
            viewport={"width": 1440, "height": 1100},
        )

        try:
            for name, target in douyin.items():
                if not isinstance(target, dict):
                    continue
                url = str(target.get("url") or "")
                match = re.search(r"/video/(\d+)", url)
                if not match:
                    # /note/ continues to be handled by the existing main updater.
                    continue

                item_id = match.group(1)
                candidates = (
                    (
                        "jingxuan",
                        f"https://jingxuan.douyin.com/m/video/{item_id}",
                    ),
                    (
                        "douyin-jingxuan",
                        f"https://www.douyin.com/jingxuan?modal_id={item_id}",
                    ),
                )

                stats: dict[str, int] = {}
                for source_name, candidate_url in candidates:
                    stats = try_candidate(
                        context, item_id, source_name, candidate_url, args.debug
                    )
                    if len(stats) >= 3:
                        break

                if len(stats) >= 3:
                    if update_target(target, stats):
                        changed = True
                else:
                    log(
                        f"[douyin-fallback] {name}/{item_id}: "
                        "all public fallbacks failed; keeping stored values"
                    )
        finally:
            context.close()
            browser.close()

    if changed:
        refresh_summary(data)
        DATA_PATH.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        log(f"[douyin-fallback] updated {DATA_PATH}")
    else:
        log("[douyin-fallback] no verified metric changes")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
