#!/usr/bin/env python3
"""
Universal Valheim Mod Auto-Translation CLI Tool
Translates localization files for Path of Valheiman and any other installed Valheim mod
into any target language (e.g. German, Russian, French, Spanish, etc.) while preserving
game code, format tags, and variable tokens ({0}, {key.use}, <b>, <color=...>, $tokens, \n).

Features:
- Auto-scans BepInEx/plugins for all installed mods with localizations.
- Compact, clean 2-column menu that fits on one screen without scrolling.
- Automatically creates Localization/ and config/ folders and output files on disk BEFORE translating.
- Supports both JSON (.json) and line-based formats (.txt, .tsv, .yml).
- Smart version diffing (re-translates only new/changed lines on mod updates).
- Rate-limit resilient with batching via HTTP POST and configurable pacing.
- 100% portable Python standard library (no pip installs needed).
"""

import sys
import os
import re
import time
import json
import html
import random
import urllib.request
import urllib.parse

# Mapping of common language codes to Valheim's internal translation names
VALHEIM_LANG_MAP = {
    "de": "german",
    "german": "german",
    "ru": "russian",
    "russian": "russian",
    "fr": "french",
    "french": "french",
    "es": "spanish",
    "spanish": "spanish",
    "pl": "polish",
    "polish": "polish",
    "it": "italian",
    "italian": "italian",
    "pt-br": "portuguese_brazilian",
    "pt_br": "portuguese_brazilian",
    "pt": "portuguese_brazilian",
    "pt-pt": "portuguese_european",
    "pt_pt": "portuguese_european",
    "zh": "chinese",
    "zh-cn": "chinese",
    "chinese": "chinese",
    "ja": "japanese",
    "japanese": "japanese",
    "ko": "korean",
    "korean": "korean",
    "tr": "turkish",
    "turkish": "turkish",
    "vi": "vietnamese",
    "vietnamese": "vietnamese",
    "sv": "swedish",
    "swedish": "swedish",
    "da": "danish",
    "danish": "danish",
    "no": "norwegian",
    "norwegian": "norwegian",
    "fi": "finnish",
    "finnish": "finnish",
    "nl": "dutch",
    "dutch": "dutch",
    "cs": "czech",
    "czech": "czech",
    "uk": "ukrainian",
    "ukrainian": "ukrainian",
}

# Regex for protecting game formatting, wiki links, and variables
TOKEN_PATTERN = re.compile(
    r'(<link="[^"]*">|</link>|<link=[^>]*>|'
    r'<color=[^>]+>|</color>|'
    r'</?[bi]>|</?size(=[0-9]+)?>|'
    r'\{[^\{\}\r\n]+\}|'
    r'\$[a-zA-Z0-9_]+|'
    r'\\[nrt])'
)

def mask_tokens(text):
    tokens = []
    def _repl(m):
        tokens.append(m.group(0))
        return f" [[TOK{len(tokens)-1}]] "
    masked = TOKEN_PATTERN.sub(_repl, text)
    return masked, tokens

def unmask_tokens(translated_text, tokens):
    res = html.unescape(translated_text)
    for idx, tok in enumerate(tokens):
        pattern = re.compile(rf'\[\[\s*TOK\s*{idx}\s*\]\]', re.IGNORECASE)
        res = pattern.sub(tok, res)
    # Clean up excess spaces added by machine translation
    res = re.sub(r'(\d+)\s+%', r'\1%', res)
    res = re.sub(r'\+\s+(\d+)', r'+\1', res)
    return res.strip()

def translate_batch_mymemory(text_list, target_lang, source_lang="en"):
    """Backup translation engine using MyMemory API when Google is IP-throttled"""
    if not text_list:
        return [], True
    results = []
    chunk_size = 5
    delimiter = "\n<<<DIV>>>\n"
    
    for i in range(0, len(text_list), chunk_size):
        chunk = text_list[i:i+chunk_size]
        combined = delimiter.join(chunk)
        try:
            url = f"https://api.mymemory.translated.net/get?q={urllib.parse.quote(combined)}&langpair={source_lang}|{target_lang}"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
            with urllib.request.urlopen(req, timeout=10) as r:
                data = json.loads(r.read().decode("utf-8"))
                if data.get("responseStatus") != 200:
                    return [], False
                raw = html.unescape(data.get("responseData", {}).get("translatedText", ""))
                if not raw or "MYMEMORY WARNING" in raw.upper():
                    return [], False
                parts = re.split(r'\s*<<<DIV>>>\s*', raw)
                while len(parts) < len(chunk):
                    parts.append(chunk[len(parts)])
                results.extend(parts[:len(chunk)])
        except Exception:
            return [], False
        time.sleep(0.3)

    return results[:len(text_list)], True

def translate_batch_deepl(text_list, target_lang, api_key, source_lang="en"):
    """Official DeepL Free API translator (500k chars free/month, zero rate limits)"""
    if not text_list:
        return [], True
    url = "https://api-free.deepl.com/v2/translate"
    lang_map = {
        "en": "EN",
        "de": "DE",
        "ru": "RU",
        "fr": "FR",
        "es": "ES",
        "pt-br": "PT-BR",
        "pt": "PT-BR",
        "pt-pt": "PT-PT",
        "it": "IT",
        "pl": "PL",
        "nl": "NL",
        "ja": "JA",
        "zh": "ZH",
        "sv": "SV",
        "da": "DA",
        "fi": "FI",
        "cs": "CS",
        "uk": "UK"
    }
    t_code = lang_map.get(target_lang.lower(), target_lang.upper())
    s_code = lang_map.get(source_lang.lower(), "EN")

    payload = json.dumps({
        "text": text_list,
        "target_lang": t_code,
        "source_lang": s_code
    }).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Authorization": f"DeepL-Auth-Key {api_key.strip()}",
            "Content-Type": "application/json"
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            translated = [item["text"] for item in data.get("translations", [])]
            while len(translated) < len(text_list):
                translated.append(text_list[len(translated)])
            return translated[:len(text_list)], True
    except Exception as e:
        print(f"\n[DeepL Error] {e}.")
        return [], False

COOLDOWN_FILENAME = ".google_cooldown.json"
COOLDOWN_DURATION_SEC = 3600  # 60 minutes cooldown

def get_cooldown_file_path(bepinex_dir=None):
    """Finds path for persistent cooldown file, preferring BepInEx/config then script dir"""
    if bepinex_dir:
        config_dir = os.path.join(bepinex_dir, "config")
        if os.path.isdir(config_dir):
            return os.path.join(config_dir, COOLDOWN_FILENAME)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, COOLDOWN_FILENAME)

def get_google_cooldown_remaining(cooldown_path):
    """Returns remaining cooldown time in seconds, or 0 if expired / not set"""
    if not cooldown_path or not os.path.exists(cooldown_path):
        return 0
    try:
        with open(cooldown_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            until = data.get("cooldown_until", 0)
            remaining = until - time.time()
            return max(0, remaining)
    except Exception:
        return 0

def set_google_cooldown(cooldown_path, duration_sec=COOLDOWN_DURATION_SEC):
    """Saves a timestamped cooldown to disk to persist across tool restarts"""
    if not cooldown_path:
        return
    try:
        os.makedirs(os.path.dirname(os.path.abspath(cooldown_path)), exist_ok=True)
        with open(cooldown_path, "w", encoding="utf-8") as f:
            json.dump({
                "throttled_at": time.time(),
                "cooldown_until": time.time() + duration_sec,
                "duration_minutes": duration_sec // 60,
                "reason": "Google Translate HTTP 429 (Too Many Requests)"
            }, f, indent=2)
    except Exception:
        pass

def clear_google_cooldown(cooldown_path):
    """Clears cooldown if user forces a retry (e.g. after changing network/VPN)"""
    if cooldown_path and os.path.exists(cooldown_path):
        try:
            os.remove(cooldown_path)
        except Exception:
            pass

def translate_batch_google(text_list, target_lang, source_lang="en", cooldown_path=None, max_retries=2):
    if not text_list:
        return [], True

    # Check persistent cooldown first - never query Google if cooldown is active
    if cooldown_path:
        remaining = get_google_cooldown_remaining(cooldown_path)
        if remaining > 0:
            return translate_batch_mymemory(text_list, target_lang, source_lang)

    delimiter = "\n<<<DIV>>>\n"
    combined = delimiter.join(text_list)

    url = (
        "https://translate.googleapis.com/translate_a/single?"
        f"client=gtx&sl={urllib.parse.quote(source_lang)}&tl={urllib.parse.quote(target_lang)}&dt=t"
    )
    post_data = urllib.parse.urlencode({"q": combined}).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=post_data,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/x-www-form-urlencoded;charset=utf-8"
        }
    )

    for attempt in range(max_retries):
        try:
            with urllib.request.urlopen(req, timeout=12) as response:
                payload = json.loads(response.read().decode("utf-8"))
                full_translated = "".join(chunk[0] for chunk in payload[0] if chunk and chunk[0])
                parts = re.split(r'\s*<<<DIV>>>\s*', full_translated)
                
                while len(parts) < len(text_list):
                    parts.append(text_list[len(parts)])
                return parts[:len(text_list)], True
        except urllib.error.HTTPError as e:
            if e.code == 429:
                if cooldown_path:
                    set_google_cooldown(cooldown_path, COOLDOWN_DURATION_SEC)
                print(f"\n[Notice] Google IP rate-limit hit (429). Switching to MyMemory...", flush=True)
                return translate_batch_mymemory(text_list, target_lang, source_lang)
            if attempt == max_retries - 1:
                return translate_batch_mymemory(text_list, target_lang, source_lang)
            time.sleep(1.0)
        except Exception:
            if attempt == max_retries - 1:
                return translate_batch_mymemory(text_list, target_lang, source_lang)
            time.sleep(1.0)
            
    return translate_batch_mymemory(text_list, target_lang, source_lang)

def detect_bepinex_root(start_dir):
    """Searches current folder and upwards for BepInEx"""
    curr = os.path.abspath(start_dir)
    for _ in range(6):
        if os.path.basename(curr).lower() == "bepinex":
            return curr
        cand = os.path.join(curr, "BepInEx")
        if os.path.isdir(cand):
            return cand
        cand_lower = os.path.join(curr, "bepinex")
        if os.path.isdir(cand_lower):
            return cand_lower
        parent = os.path.dirname(curr)
        if parent == curr:
            break
        curr = parent
    return None

def scan_plugins_for_mods(bepinex_dir):
    """
    Scans BepInEx/plugins for all mods with localization files or directories.
    Returns a list of dicts with mod details.
    """
    plugins_dir = os.path.join(bepinex_dir, "plugins")
    if not os.path.isdir(plugins_dir):
        return []

    mods = []
    for entry in os.scandir(plugins_dir):
        if not entry.is_dir():
            continue

        folder_name = entry.name
        # Human-friendly display name (strip author prefixes like 'treextr-', 'Vapok-')
        display_name = re.sub(r'^[a-zA-Z0-9_]+-', '', folder_name)
        display_name = display_name.replace("_", " ").replace("-", " ")

        loc_candidates = []
        loc_dir = None

        for root, dirs, files in os.walk(entry.path):
            dir_name_lower = os.path.basename(root).lower()
            if dir_name_lower in ["localization", "translations", "languages", "lang"]:
                loc_dir = root

            for f in files:
                f_lower = f.lower()
                is_ext = f.endswith(('.txt', '.json', '.yml', '.yaml', '.tsv'))
                if not is_ext:
                    continue

                if (any(k in f_lower for k in ['english', 'localization', 'translation']) or
                    dir_name_lower in ["localization", "translations", "languages", "lang"]):
                    loc_candidates.append(os.path.join(root, f))

        if loc_candidates:
            # Pick best English candidate (prefer most comprehensive English dictionary)
            english_cands = [c for c in loc_candidates if "english" in os.path.basename(c).lower()]
            if english_cands:
                # Sort by size descending so full master dictionary (e.g. english.txt with 26k lines)
                # is chosen rather than abridged or template versions (e.g. english-for-translators.txt)
                english_cands.sort(key=lambda p: os.path.getsize(p) if os.path.exists(p) else 0, reverse=True)
                best_source = english_cands[0]
            else:
                best_source = loc_candidates[0]

            if not loc_dir:
                loc_dir = os.path.dirname(best_source)

            # Determine config translation folder (using exact BepInPlugin GUID)
            if "valheiman" in folder_name.lower():
                config_guid = "treextr.pathofvalheiman"
            else:
                config_guid = folder_name.replace("-", ".").replace(" ", "_").lower()
                config_root = os.path.join(bepinex_dir, "config")
                if os.path.isdir(config_root):
                    for cfg in os.listdir(config_root):
                        if cfg.endswith(".cfg"):
                            base_cfg = cfg[:-4]
                            if (base_cfg.lower() == folder_name.lower() or 
                                base_cfg.lower() == config_guid or
                                display_name.lower().replace(" ", "") in base_cfg.lower()):
                                config_guid = base_cfg
                                break
            config_dir = os.path.join(bepinex_dir, "config", f"{config_guid}.translations")

            mods.append({
                "display_name": display_name,
                "folder_name": folder_name,
                "source_file": best_source,
                "loc_dir": loc_dir,
                "config_dir": config_dir,
                "all_loc_files": loc_candidates
            })

    # Sort so Path of Valheiman is at the top if present, then alphabetical
    def sort_key(m):
        name = m["display_name"].lower()
        if "valheiman" in name:
            return "000_" + name
        return "001_" + name

    mods.sort(key=sort_key)
    return mods

def format_grid_menu(items, cols=2, col_width=36):
    """Formats items into a clean 2-column menu that fits on one terminal screen"""
    lines = []
    num_rows = (len(items) + cols - 1) // cols
    for r in range(num_rows):
        row_parts = []
        for c in range(cols):
            idx = r + c * num_rows
            if idx < len(items):
                label = f"[{idx+1:>2}] {items[idx]}"
                if len(label) > col_width:
                    label = label[:col_width-2] + ".."
                row_parts.append(f"{label:<{col_width}}")
            else:
                row_parts.append(" " * col_width)
        lines.append(" " + " | ".join(row_parts))
    return lines

def clean_path_input(path_str):
    if not path_str:
        return ""
    p = path_str.strip()
    if (p.startswith('"') and p.endswith('"')) or (p.startswith("'") and p.endswith("'")):
        p = p[1:-1].strip()
    return os.path.normpath(p)

def load_cache(cache_file):
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_cache(cache_file, cache_data):
    try:
        parent_dir = os.path.dirname(os.path.abspath(cache_file))
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def parse_existing_translation(filepath):
    res = {}
    if not os.path.exists(filepath):
        return res
    try:
        if filepath.endswith('.json'):
            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return {k: str(v) for k, v in data.items() if isinstance(v, (str, int, float))}
        else:
            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    if line.startswith("#") or not line.strip():
                        continue
                    if "\t" in line:
                        parts = line.split("\t", 1)
                        res[parts[0]] = parts[1].rstrip("\r\n")
                    elif ":" in line:
                        parts = line.split(":", 1)
                        res[parts[0].strip()] = parts[1].strip().strip('"').strip("'")
    except Exception:
        pass
    return res

def compute_output_filename(source_filename, target_code):
    valheim_lang = VALHEIM_LANG_MAP.get(target_code.lower(), target_code.lower())
    base_lower = source_filename.lower()

    # If filename is like 'english-for-translators.txt' or 'english.txt'
    if base_lower.startswith("english"):
        ext = os.path.splitext(source_filename)[1] or ".txt"
        if source_filename.startswith("English"):
            return f"{valheim_lang.capitalize()}{ext}"
        return f"{valheim_lang.lower()}{ext}"

    # If filename is like 'AdventureBackpacks.English.json' or 'Longship Upgrades.English.json'
    if re.search(r'\benglish\b', source_filename, re.IGNORECASE):
        m = re.search(r'\b(english)\b', source_filename, re.IGNORECASE)
        if m and m.group(1).islower():
            target_replacement = valheim_lang.lower()
        else:
            target_replacement = valheim_lang.capitalize()
            
        out = re.sub(r'\benglish\b', target_replacement, source_filename, flags=re.IGNORECASE)
        out = re.sub(r'-for-translators', '', out, flags=re.IGNORECASE)
        return out

    ext = os.path.splitext(source_filename)[1] or ".txt"
    return f"{valheim_lang.lower()}{ext}"

def main():
    print("=" * 78)
    print("                 VALHEIM MOD AUTO-TRANSLATION TOOL")
    print("=" * 78)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    bepinex_root = detect_bepinex_root(script_dir)

    selected_mod = None
    discovered_mods = []

    if bepinex_root:
        print(f"[Profile Context] Detected BepInEx: {bepinex_root}\n")
        discovered_mods = scan_plugins_for_mods(bepinex_root)

    if discovered_mods:
        labels = [m["display_name"] for m in discovered_mods]
        print(f"Discovered {len(discovered_mods)} mod(s) with localization in your profile:")
        print("-" * 78)
        grid_lines = format_grid_menu(labels, cols=2, col_width=36)
        for line in grid_lines:
            print(line)
        print("-" * 78)
        print("  [ 0] Custom File / Drag & Drop       | [ F] Filter / Search mods by name")
        print("=" * 78)

        choice = input("\nSelect mod number [default: 1]: ").strip().lower()

        if choice in ["f", "filter", "search"]:
            query = input("Enter search word (e.g. 'valheiman' or 'backpack'): ").strip().lower()
            filtered = [m for m in discovered_mods if query in m["display_name"].lower() or query in m["folder_name"].lower()]
            if filtered:
                print("\nMatching Mods:")
                for idx, m in enumerate(filtered, 1):
                    print(f"  [{idx}] {m['display_name']} -> {os.path.basename(m['source_file'])}")
                sub_choice = input("\nSelect matching number [default: 1]: ").strip()
                sel_idx = int(sub_choice) - 1 if sub_choice.isdigit() else 0
                if 0 <= sel_idx < len(filtered):
                    selected_mod = filtered[sel_idx]
            else:
                print(f"No mods matched '{query}'. Using custom file.")

        elif choice.isdigit():
            c_int = int(choice)
            if 1 <= c_int <= len(discovered_mods):
                selected_mod = discovered_mods[c_int - 1]

        if not selected_mod and choice in ["", "1"] and len(discovered_mods) >= 1:
            selected_mod = discovered_mods[0]

    # Source File
    if selected_mod:
        source_file = selected_mod["source_file"]
        mod_name = selected_mod["display_name"]
        mod_loc_dir = selected_mod["loc_dir"]
        config_trans_dir = selected_mod["config_dir"]
        print(f"\n[Selected Mod] {mod_name}")
        print(f"  Source: {source_file}")
    else:
        print("\nTip: Drag and drop your English localization file here, or enter its path.")
        src_input = input("Source file path: ").strip()
        source_file = clean_path_input(src_input)
        if not source_file or not os.path.exists(source_file):
            print(f"[Error] File not found: {source_file}")
            input("\nPress Enter to exit...")
            return
        mod_loc_dir = os.path.dirname(source_file)
        config_trans_dir = os.path.join(bepinex_root, "config", "custom_translations") if bepinex_root else mod_loc_dir

    # Language Codes
    source_code = input("\nEnter source language code [default: en]: ").strip().lower() or "en"

    print("\nExamples of language codes: de (German), ru (Russian), fr (French),")
    print("es (Spanish), pl (Polish), it (Italian), pt-br (Portuguese), zh (Chinese)...")
    target_code = ""
    while not target_code:
        target_code = input("\nEnter target language code (e.g. de, ru, fr): ").strip().lower()

    # Determine recommended filename
    source_filename = os.path.basename(source_file)
    default_out_name = compute_output_filename(source_filename, target_code)
    out_input = input(f"Output filename [default: {default_out_name}]: ").strip()
    output_filename = out_input if out_input else default_out_name

    # =========================================================================
    # PRE-CREATE DIRECTORIES AND FILES ON DISK BEFORE TRANSLATING
    # =========================================================================
    os.makedirs(mod_loc_dir, exist_ok=True)
    if config_trans_dir:
        os.makedirs(config_trans_dir, exist_ok=True)

    plugin_dest_file = os.path.join(mod_loc_dir, output_filename)
    config_dest_file = os.path.join(config_trans_dir, output_filename) if config_trans_dir else None
    cache_path = os.path.join(config_trans_dir if config_trans_dir else mod_loc_dir, f".{output_filename}.cache.json")

    # Touch / Initialize target files on disk immediately
    if not os.path.exists(plugin_dest_file):
        with open(plugin_dest_file, "w", encoding="utf-8") as f:
            f.write("")
    if config_dest_file and not os.path.exists(config_dest_file):
        with open(config_dest_file, "w", encoding="utf-8") as f:
            f.write("")
    if not os.path.exists(cache_path):
        save_cache(cache_path, {})

    print("\n" + "=" * 78)
    print("[Disk Initialized] Ready on disk BEFORE translating:")
    print(f"  📁 Mod Folder   : {mod_loc_dir}")
    print(f"  📄 Plugin File  : {plugin_dest_file}")
    if config_dest_file:
        print(f"  📄 Config File  : {config_dest_file}")
    print(f"  💾 Cache File   : {cache_path}")
    print("=" * 78)

    # 4. Load Source Data
    cache = load_cache(cache_path)
    is_json = source_file.endswith(".json")

    # Check existing translation files from plugins and config folders
    existing_map = {}
    found_sources = []
    if plugin_dest_file and os.path.exists(plugin_dest_file) and os.path.getsize(plugin_dest_file) > 0:
        m1 = parse_existing_translation(plugin_dest_file)
        if m1:
            existing_map.update(m1)
            found_sources.append(os.path.basename(plugin_dest_file))
    if config_dest_file and os.path.exists(config_dest_file) and os.path.getsize(config_dest_file) > 0:
        m2 = parse_existing_translation(config_dest_file)
        if m2:
            existing_map.update(m2)  # Config overrides plugin as per mod developer design
            found_sources.append(os.path.basename(config_dest_file))

    # Seed cache with existing translations
    for k, v in existing_map.items():
        if k not in cache or not cache[k].get("dst"):
            cache[k] = {"src": "", "dst": v}

    # Load source keys and raw data
    source_items = []
    if is_json:
        with open(source_file, "r", encoding="utf-8", errors="replace") as f:
            json_source_data = json.load(f)
        print(f"\nLoaded {len(json_source_data):,} keys from JSON source.")
        for k, v in json_source_data.items():
            source_items.append((k, str(v)))
    else:
        with open(source_file, "r", encoding="utf-8", errors="replace") as f:
            source_lines = f.readlines()
        print(f"\nLoaded {len(source_lines):,} lines from text source.")
        for line in source_lines:
            if line.startswith("#") or not line.strip():
                source_items.append((None, line))
                continue
            if "\t" in line:
                parts = line.split("\t", 1)
                source_items.append((parts[0], parts[1].rstrip("\r\n")))
            elif ":" in line and not line.strip().startswith("http"):
                parts = line.split(":", 1)
                source_items.append((parts[0].strip(), parts[1].strip().strip('"').strip("'")))
            else:
                source_items.append((None, line))

    # Analyze translation progress against source items
    genuine_trans = 0
    still_english = 0
    missing = 0

    for item in source_items:
        k, text = item
        if k is None or not text.strip():
            continue
        entry = cache.get(k)
        if not entry:
            missing += 1
        else:
            dst = entry.get("dst", "").strip()
            if not dst:
                missing += 1
            elif dst.lower() == text.strip().lower() and any(c.isalpha() for c in text):
                still_english += 1
            else:
                genuine_trans += 1

    retranslate_english = False
    if genuine_trans > 0 or still_english > 0:
        total_remaining = still_english + missing
        print("\n" + "=" * 78)
        print("                 TRANSLATION STATUS DETECTED")
        print("=" * 78)
        print(f"  -> Translated lines (Genuine)       : {genuine_trans:,}")
        print(f"  -> Lines currently still in English : {still_english:,}")
        print(f"  -> Completely missing lines         : {missing:,}")
        print("=" * 78)

        if total_remaining > 0:
            print("\nHow would you like to proceed?")
            print(f"  [1] Keep translated lines, translate all {total_remaining:,} remaining/English lines (Default)")
            print(f"  [2] Keep existing translations as-is (translate ONLY {missing:,} completely missing lines)")
            print("  [3] Re-translate everything from scratch (ignore existing files)")
            ans = input("Select mode [default: 1]: ").strip().lower()
            if ans in ("", "1", "y", "yes"):
                retranslate_english = True
            elif ans == "2":
                retranslate_english = False
            elif ans in ["3", "scratch", "reset", "n", "no"]:
                cache = {}
                retranslate_english = False
        else:
            print("\nAll strings are already translated!")

    # Build execution plan
    plan = []
    for item in source_items:
        k, text = item
        if k is None:
            plan.append(("comment", None, text, None))
            continue
        if not text.strip():
            existing_val = cache.get(k, {}).get("dst", "")
            plan.append(("reuse", k, "", existing_val))
            continue

        if k in cache:
            cached_entry = cache[k]
            cached_src = cached_entry.get("src", "")
            cached_dst = cached_entry.get("dst", "")
            if cached_dst and (cached_src == text or not cached_src):
                is_eng = (cached_dst.strip().lower() == text.strip().lower() and any(c.isalpha() for c in text.strip()))
                if retranslate_english and is_eng:
                    plan.append(("translate", k, text, None))
                    continue
                if not is_eng or not retranslate_english:
                    plan.append(("reuse", k, text, cached_dst))
                    continue
        plan.append(("translate", k, text, None))

    unchanged_count = sum(1 for p in plan if p[0] == "reuse")
    changed_count = sum(1 for p in plan if p[0] == "translate")

    print("\n" + "-" * 78)
    print(f"Change Detection Summary:")
    print(f"  -> Unchanged strings (reused instantly) : {unchanged_count:,}")
    print(f"  -> New / Modified strings to translate  : {changed_count:,}")
    print("-" * 78)

    # Helper function to flush files to disk
    results_dict = {}

    def write_output_to_disk():
        if is_json:
            out_data = {}
            for item in plan:
                k = item[1]
                if item[0] == "reuse":
                    out_data[k] = item[3]
                elif item[0] == "translate":
                    out_data[k] = results_dict.get(k, cache.get(k, {}).get("dst", item[2]))
            with open(plugin_dest_file, "w", encoding="utf-8") as f:
                json.dump(out_data, f, ensure_ascii=False, indent=2)
            if config_dest_file:
                with open(config_dest_file, "w", encoding="utf-8") as f:
                    json.dump(out_data, f, ensure_ascii=False, indent=2)
        else:
            lines_out = []
            for item in plan:
                if item[0] == "comment":
                    lines_out.append(item[2])
                elif item[0] == "reuse":
                    lines_out.append(f"{item[1]}\t{item[3]}\n")
                elif item[0] == "translate":
                    k = item[1]
                    trans = results_dict.get(k, cache.get(k, {}).get("dst", item[2]))
                    lines_out.append(f"{k}\t{trans}\n")
            with open(plugin_dest_file, "w", encoding="utf-8") as f:
                f.writelines(lines_out)
            if config_dest_file:
                with open(config_dest_file, "w", encoding="utf-8") as f:
                    f.writelines(lines_out)

    if changed_count == 0:
        print("\nAll strings are already up-to-date! No translation needed.")
        write_output_to_disk()
        print(f"Validated and saved directly to:")
        print(f"  -> {plugin_dest_file}")
        input("\nPress Enter to exit...")
        return

    # 5. Pacing Delay & Engine Configuration
    cooldown_path = get_cooldown_file_path(bepinex_root)
    cooldown_rem = get_google_cooldown_remaining(cooldown_path)
    google_on_cooldown = cooldown_rem > 0
    cooldown_mins = int(cooldown_rem // 60) + 1 if google_on_cooldown else 0

    print("\nTranslation Engine:")
    if google_on_cooldown:
        print(f"  [1] MyMemory Backup (Auto-Selected: Google is cooling down for another {cooldown_mins}m)")
        print(f"  [2] DeepL API (Requires Free DeepL Key - 500k chars/mo, Best Quality & 0 rate limits)")
        print(f"  [3] Reset Cooldown & Try Google (Only if you changed network/VPN)")
    else:
        print("  [1] Google Translate (Default - Fast & Free, auto-switches to MyMemory if throttled)")
        print("  [2] MyMemory (Free - Instant bypass if Google is rate-limiting your IP)")
        print("  [3] DeepL API (Requires Free DeepL Key - 500k chars/mo, Best Quality & 0 rate limits)")

    engine_choice = input("Select engine [default: 1]: ").strip().lower()
    deepl_key = None
    use_mymemory = False

    if google_on_cooldown:
        if engine_choice == "2":
            deepl_key = input("Enter your DeepL API Key: ").strip()
        elif engine_choice in ["3", "reset", "force"]:
            clear_google_cooldown(cooldown_path)
            print("  -> Cooldown cleared! Attempting Google Translate.")
            use_mymemory = False
            google_on_cooldown = False
        else:
            use_mymemory = True
    else:
        if engine_choice == "2":
            use_mymemory = True
        elif engine_choice == "3":
            deepl_key = input("Enter your DeepL API Key: ").strip()

    print("\nBatch Pacing: A delay between batches keeps traffic under rate limits.")
    delay_input = input("Enter delay in seconds between batches [default: 5.0, or 15.0 for extra safety]: ").strip()
    try:
        batch_delay = float(delay_input) if delay_input else 5.0
    except ValueError:
        batch_delay = 5.0

    batch_size = 50
    max_batch_chars = 4000  # Strict ceiling safely below the 5,000-character web limit
    buffer_keys = []
    buffer_masked = []
    buffer_tokens = []
    google_throttled = use_mymemory or google_on_cooldown

    if deepl_key:
        engine_name = "DeepL API"
    elif google_throttled:
        engine_name = f"MyMemory API (Google on 60m cooldown, {cooldown_mins}m left)" if google_on_cooldown else "MyMemory API"
    else:
        engine_name = "Google Translate (with auto MyMemory backup)"

    def format_eta(seconds):
        if seconds <= 0:
            return "0s"
        s = int(seconds)
        hours = s // 3600
        mins = (s % 3600) // 60
        secs = s % 60
        if hours > 0:
            return f"~{hours}h {mins:02d}m"
        if mins > 0:
            return f"~{mins}m {secs:02d}s"
        return f"~{secs}s"

    # Conservative higher-end estimate calculation
    avg_strings_per_batch = 42
    est_total_batches = max(1, (changed_count + avg_strings_per_batch - 1) // avg_strings_per_batch)
    if deepl_key:
        overhead = 2.0
    elif google_throttled or use_mymemory:
        overhead = 4.5
    else:
        overhead = 3.5

    conservative_sec_per_batch = batch_delay + 1.2 + overhead
    initial_eta_seconds = est_total_batches * conservative_sec_per_batch
    initial_eta_display = format_eta(initial_eta_seconds)

    print(f"\nTranslating using {engine_name} (max {batch_size} strings or {max_batch_chars} chars per batch, {batch_delay:.1f}s pause)...")
    print(f"Estimated Time Remaining: {initial_eta_display} (higher-end estimate based on {batch_delay:.1f}s delay)")
    print("(Press Ctrl+C at any time to pause & save progress)\n")

    def flush_batch():
        nonlocal buffer_keys, buffer_masked, buffer_tokens, google_throttled
        if not buffer_masked:
            return True

        if deepl_key:
            translations, success = translate_batch_deepl(buffer_masked, target_lang=target_code, api_key=deepl_key, source_lang=source_code)
        elif google_throttled:
            translations, success = translate_batch_mymemory(buffer_masked, target_lang=target_code, source_lang=source_code)
        else:
            translations, success = translate_batch_google(buffer_masked, target_lang=target_code, source_lang=source_code, cooldown_path=cooldown_path)
            if not success:
                google_throttled = True

        if not success or not translations or len(translations) < len(buffer_keys):
            return False

        for k, res_text, tokens in zip(buffer_keys, translations, buffer_tokens):
            unmasked = unmask_tokens(res_text, tokens)
            results_dict[k] = unmasked
            cache[k] = {"src": plan_lookup.get(k, ""), "dst": unmasked}

        buffer_keys = []
        buffer_masked = []
        buffer_tokens = []
        return True

    plan_lookup = {p[1]: p[2] for p in plan if p[1]}
    translated_so_far = 0
    current_batch_chars = 0
    trans_start_time = time.time()

    try:
        for item in plan:
            if item[0] != "translate":
                continue

            k = item[1]
            text = item[2]
            masked_str, tokens = mask_tokens(text)
            str_len = len(masked_str) + 12  # Account for delimiter

            # If adding this string would exceed character ceiling or item count, flush existing batch first
            if buffer_masked and (len(buffer_masked) >= batch_size or (current_batch_chars + str_len > max_batch_chars)):
                flushed_count = len(buffer_masked)
                success = flush_batch()
                if not success:
                    print("\n\n" + "=" * 78)
                    print("[Rate Limit Alert] All free translation services are temporarily throttled on your IP.")
                    print(f"Your translated progress ({len(cache):,} strings) has been safely saved to disk!")
                    print("\nTo finish the remaining strings without waiting:")
                    print("  1. Connect to a VPN or phone hotspot (new IP immediately resets free quotas), OR")
                    print("  2. Use DeepL Free API (Option 3 at startup - 500k chars/mo with 0 rate limits).")
                    print("=" * 78)
                    save_cache(cache_path, cache)
                    write_output_to_disk()
                    return

                translated_so_far += flushed_count
                pct = min(100.0, translated_so_far / changed_count * 100)

                # Dynamic higher-end ETA calculation
                strings_left = max(0, changed_count - translated_so_far)
                batches_left = max(1, (strings_left + avg_strings_per_batch - 1) // avg_strings_per_batch)
                elapsed_total = time.time() - trans_start_time

                if translated_so_far > 0 and elapsed_total > 0:
                    measured_rate = translated_so_far / elapsed_total
                    measured_eta = (strings_left / measured_rate) * 1.15 if measured_rate > 0 else 0
                    model_eta = batches_left * conservative_sec_per_batch
                    eta_seconds = max(measured_eta, model_eta)
                else:
                    eta_seconds = batches_left * conservative_sec_per_batch

                eta_display = format_eta(eta_seconds)
                print(f"\rProgress: {translated_so_far:,}/{changed_count:,} changed strings ({pct:.1f}%) | ETA: {eta_display}   ", end="", flush=True)
                save_cache(cache_path, cache)
                write_output_to_disk()
                jitter = random.uniform(0.3, 1.2)
                time.sleep(batch_delay + jitter)
                current_batch_chars = 0

            buffer_keys.append(k)
            buffer_masked.append(masked_str)
            buffer_tokens.append(tokens)
            current_batch_chars += str_len

        if buffer_masked:
            flushed_count = len(buffer_masked)
            success = flush_batch()
            if success:
                translated_so_far += flushed_count
                save_cache(cache_path, cache)
                write_output_to_disk()

        total_elapsed_str = format_eta(time.time() - trans_start_time)
        print(f"\rProgress: {changed_count:,}/{changed_count:,} changed strings (100.0%) - Completed in {total_elapsed_str}!\n")

    except KeyboardInterrupt:
        print("\n\n[Paused] Saving current progress and cache to disk...")

    # Final write
    save_cache(cache_path, cache)
    write_output_to_disk()

    print("=" * 78)
    print(f"SUCCESS: Translation successfully written to:")
    print(f"  -> Plugin Mod Folder : {plugin_dest_file}")
    if config_dest_file:
        print(f"  -> Profile Config    : {config_dest_file}")
    print(f"  -> Cache File        : {cache_path}")
    print("=" * 78)
    print("\nNext steps in Valheim:")
    print("1. Open Settings -> Language -> Select your language.")
    print("2. Restart Valheim to enjoy the mod in your language!")
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
