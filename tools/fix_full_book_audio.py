import argparse
import asyncio
import difflib
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools" / "vendor"))
VOICE = "sw-TZ-RehemaNeural"
RATE = "-10%"
VERSION = 25

ORDINALS = {
    "1": "Kwanza", "2": "Pili", "3": "Tatu", "4": "Nne", "5": "Tano",
    "6": "Sita", "7": "Saba", "8": "Nane", "9": "Tisa", "10": "Kumi",
    "11": "Kumi na Moja", "12": "Kumi na Mbili", "13": "Kumi na Tatu",
    "14": "Kumi na Nne", "15": "Kumi na Tano", "16": "Kumi na Sita",
    "17": "Kumi na Saba", "18": "Kumi na Nane", "19": "Kumi na Tisa",
    "20": "Ishirini",
}


def norm(value):
    return re.sub(r"[^a-z0-9\u00c0-\u024f]+", "", str(value).lower())


def tokens(value):
    return re.findall(r"\S+", value)


def page_number(path):
    return int(re.search(r"pg(\d+)_", path.name).group(1))


def parse_page(path):
    raw = path.read_text(encoding="utf-8")
    match = re.search(r'<div class="accessible-transcript[^>]*>(.*?)</div>', raw, re.S)
    if not match:
        return raw, [], []
    nodes = []
    for node_id, value in re.findall(r'data-id="([^"]+)"[^>]*>(.*?)</span>', match.group(1), re.S):
        value = html.unescape(re.sub(r"<[^>]+>", "", value)).strip()
        if value:
            nodes.append((node_id, value))
    while nodes and (re.fullmatch(r"[ivxlcdm\d]+", nodes[-1][1], re.I) or ".indd" in nodes[-1][1]):
        nodes.pop()
    visible = [
        (int(index), html.unescape(re.sub(r"<[^>]+>", "", value)).strip())
        for index, value in re.findall(r'<span class="pdf-word" data-word-index="(\d+)"[^>]*>(.*?)</span>', raw, re.S)
    ]
    return raw, nodes, visible


def spoken_stream(nodes):
    original = []
    hidden = []
    for node_id, value in nodes:
        node_tokens = tokens(value)
        original.extend(node_tokens)
        hidden.extend(["_matrix_" in node_id] * len(node_tokens))

    spoken = []
    origins = []
    index = 0
    while index < len(original):
        current = norm(original[index])
        if index + 2 < len(original) and current in {"zoezi", "mfano"} and norm(original[index + 1]) in {"la", "wa"}:
            number = norm(original[index + 2])
            if number in ORDINALS:
                spoken.extend([original[index], original[index + 1]])
                origins.extend([index, index + 1])
                for word in ORDINALS[number].split():
                    spoken.append(word)
                    origins.append(index + 2)
                index += 3
                continue
        if current.startswith("gpe"):
            spoken.append("gipiee")
            origins.append(index)
        elif current == "education":
            spoken.append("edukesheni")
            origins.append(index)
        elif current.startswith("kkk"):
            spoken.extend(["kei", "kei", "kei"])
            origins.extend([index, index, index])
        else:
            spoken.append(original[index])
            origins.append(index)
        index += 1
    return original, hidden, spoken, origins


def original_to_visual(original, visible):
    a = [norm(value) for value in original]
    b = [norm(value) for _, value in visible]
    result = {}
    matcher = difflib.SequenceMatcher(None, a, b, autojunk=False)
    for a_start, b_start, size in matcher.get_matching_blocks():
        for offset in range(size):
            result[a_start + offset] = visible[b_start + offset][0]
    return result


def needs_new_audio(nodes):
    text = " ".join(value for _, value in nodes)
    return bool(re.search(r"\bZoezi\s+la\s+\d+\b|\bMfano\s+wa\s+\d+\b|\bGPE\b|\bEducation\b|\bKKK\b", text, re.I))


def needs_mfano_audio(nodes):
    text = " ".join(value for _, value in nodes)
    return bool(re.search(r"\bMfano\s+wa\s+\d+\b", text, re.I))


def align_cues_to_spoken(cues, spoken):
    spoken_norm = [norm(value) for value in spoken]
    cue_norm = [norm(cue.get("text")) for cue in cues]
    result = {}
    matcher = difflib.SequenceMatcher(None, cue_norm, spoken_norm, autojunk=False)
    for cue_start, spoken_start, size in matcher.get_matching_blocks():
        for offset in range(size):
            result[cue_start + offset] = spoken_start + offset
    return result


def preserve_custom_targets(old_words, new_words):
    old_norm = [norm(cue.get("text")) for cue in old_words]
    new_norm = [norm(cue.get("text")) for cue in new_words]
    matcher = difflib.SequenceMatcher(None, old_norm, new_norm, autojunk=False)
    for old_start, new_start, size in matcher.get_matching_blocks():
        for offset in range(size):
            old = old_words[old_start + offset]
            new = new_words[new_start + offset]
            if "targetSelector" in old:
                new["targetSelector"] = old["targetSelector"]
            elif old.get("targetImage"):
                new["targetImage"] = True


def apply_safe_mapping(cues, nodes, visible, old_words=()):
    original, hidden, spoken, origins = spoken_stream(nodes)
    origin_visual = original_to_visual(original, visible)
    cue_spoken = align_cues_to_spoken(cues, spoken)
    preserve_custom_targets(old_words, cues)
    for cue_index, cue in enumerate(cues):
        if "targetSelector" in cue or cue.get("targetImage"):
            cue.pop("sourceIndex", None)
            continue
        spoken_index = cue_spoken.get(cue_index)
        origin = origins[spoken_index] if spoken_index is not None and spoken_index < len(origins) else None
        visual = origin_visual.get(origin) if origin is not None and not hidden[origin] else None
        if visual is None:
            cue.pop("sourceIndex", None)
            cue["targetImage"] = True
        else:
            cue.pop("targetImage", None)
            cue["sourceIndex"] = visual


async def generate_audio(page, nodes, visible, old_entry):
    import edge_tts

    _, _, spoken, _ = spoken_stream(nodes)
    text = " ".join(spoken)
    audio_name = f"page-{page:03d}-fullbook-v1.mp3"
    output = ROOT / "content" / "rehema"
    cues = []
    with (output / audio_name).open("wb") as audio:
        stream = edge_tts.Communicate(text, VOICE, rate=RATE, boundary="WordBoundary")
        async for event in stream.stream():
            if event["type"] == "audio":
                audio.write(event["data"])
            elif event["type"] == "WordBoundary":
                start = event["offset"] / 10_000_000
                duration = event["duration"] / 10_000_000
                cues.append({"text": event["text"], "start": round(start, 6), "end": round(start + duration, 6)})
    apply_safe_mapping(cues, nodes, visible, old_entry.get("words", []))
    return {"audio": audio_name, "voice": VOICE, "rate": 0.9, "pitch": "neutral", "version": VERSION, "words": cues}


def remap_existing(entry, nodes, visible):
    cues = entry.get("words", [])
    apply_safe_mapping(cues, nodes, visible, cues)
    entry["voice"] = VOICE
    entry["rate"] = 0.9
    entry["version"] = VERSION
    return entry


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--generate-special", action="store_true")
    parser.add_argument("--only-mfano", action="store_true")
    parser.add_argument("--page", type=int)
    args = parser.parse_args()
    timecodes_path = ROOT / "content" / "rehema" / "timecodes.json"
    timecodes = json.loads(timecodes_path.read_text(encoding="utf-8"))
    pages = sorted(ROOT.glob("pg*_sec001.html"), key=page_number)
    report = {"pages": 0, "regenerated": [], "remapped": [], "special": []}
    for path in pages:
        page = page_number(path)
        if args.page and page != args.page:
            continue
        _, nodes, visible = parse_page(path)
        if not nodes:
            continue
        old_entry = timecodes.get(str(page), {})
        special = needs_new_audio(nodes)
        if special:
            report["special"].append(page)
        selected_for_audio = special and (not args.only_mfano or needs_mfano_audio(nodes))
        if args.generate_special and selected_for_audio:
            entry = await generate_audio(page, nodes, visible, old_entry)
            report["regenerated"].append(page)
        else:
            entry = remap_existing(old_entry, nodes, visible)
            report["remapped"].append(page)
        timecodes[str(page)] = entry
        (ROOT / "content" / "rehema" / f"page-{page:03d}.json").write_text(
            json.dumps(entry, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        timecodes_path.write_text(json.dumps(timecodes, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        report["pages"] += 1
        if args.generate_special and selected_for_audio:
            print(f"page={page} regenerated", flush=True)
    (ROOT / "content" / "rehema" / "full-book-audio-report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps({key: len(value) if isinstance(value, list) else value for key, value in report.items()}))


if __name__ == "__main__":
    asyncio.run(main())
