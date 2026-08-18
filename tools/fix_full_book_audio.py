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

UNITS_SW = {
    1: "moja", 2: "mbili", 3: "tatu", 4: "nne", 5: "tano",
    6: "sita", 7: "saba", 8: "nane", 9: "tisa",
}
TENS_SW = {
    10: "kumi", 20: "ishirini", 30: "thelathini", 40: "arobaini",
    50: "hamsini", 60: "sitini", 70: "sabini", 80: "themanini", 90: "tisini",
}


def number_to_swahili(number):
    if number == 0:
        return "sifuri"
    if number < 0:
        return str(number)
    if number < 10:
        return UNITS_SW[number]
    if number < 100:
        tens, remainder = divmod(number, 10)
        base = TENS_SW[tens * 10]
        return base if not remainder else f"{base} na {UNITS_SW[remainder]}"
    if number < 1000:
        hundreds, remainder = divmod(number, 100)
        base = f"mia {UNITS_SW[hundreds]}"
        return base if not remainder else f"{base} na {number_to_swahili(remainder)}"
    thousands, remainder = divmod(number, 1000)
    base = f"elfu {number_to_swahili(thousands)}"
    return base if not remainder else f"{base} {number_to_swahili(remainder)}"


def roman_to_int(symbol):
    values = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
    total = 0
    previous = 0
    for character in reversed(symbol):
        value = values[character]
        if value < previous:
            total -= value
        else:
            total += value
            previous = value
    return total


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
    sequence_indexes = set()
    sequence_starts = set()
    arithmetic_operators = {}
    step_indexes = set()
    question_indexes = set()
    in_steps = False
    for node_id, value in nodes:
        node_tokens = tokens(value)
        start = len(original)
        plain_value = re.sub(r"[^A-Za-zÀ-ž]+", " ", value).strip().lower()
        if plain_value == "hatua":
            in_steps = True
        elif in_steps and re.match(r"^(?:mfano|zoezi|sura)\b", plain_value):
            in_steps = False
        if in_steps and node_tokens:
            step_match = re.fullmatch(r"\(?([0-9]+)[.)]?", node_tokens[0])
            if step_match and step_match.group(1) in ORDINALS:
                step_indexes.add(start)
        for offset, token in enumerate(node_tokens):
            if re.fullmatch(r"\d+[.]", token):
                nearby = " ".join(node_tokens[offset + 1:offset + 6])
                if re.search(r"(?:\+|\-|−|–|â€“|âˆ’|×|Ã—|=)", nearby):
                    question_indexes.add(start + offset)
        original.extend(node_tokens)
        hidden.extend(["_matrix_" in node_id] * len(node_tokens))
        # Number-sequence questions contain comma-separated numbers followed
        # by blank dashes/dots. Only in these nodes should punctuation itself
        # be spoken aloud.
        if re.search(r"(?:_{1,}|\.{3,}|…+)", value) and re.search(r"\d\s*,", value):
            sequence_indexes.update(range(start, start + len(node_tokens)))
            sequence_starts.add(start)
        for offset, token in enumerate(node_tokens):
            absolute = start + offset
            symbol = token.strip(".,;:()")
            if symbol in {"+", "-", "−", "–", "â€“", "âˆ’", "×", "Ã—"}:
                if symbol == "+":
                    arithmetic_operators[absolute] = "kuongeza"
                elif symbol in {"×", "Ã—"}:
                    arithmetic_operators[absolute] = "kuzidisha"
                else:
                    arithmetic_operators[absolute] = "kutoa"
            elif "=" in symbol:
                has_answer = (
                    offset + 1 < len(node_tokens)
                    and re.fullmatch(r"\d+[.,;:]?", node_tokens[offset + 1])
                )
                arithmetic_operators[absolute] = "equals-answer" if has_answer else "equals-question"

    spoken = []
    origins = []
    index = 0
    while index < len(original):
        if index in arithmetic_operators:
            operation = arithmetic_operators[index]
            if operation == "equals-question":
                spoken.extend(["sawa", "sawa", "na", "ngapi?"])
                origins.extend([index, index, index, index])
            elif operation == "equals-answer":
                spoken.extend(["sawa", "sawa", "na"])
                origins.extend([index, index, index])
            else:
                spoken.append(operation)
                origins.append(index)
            index += 1
            continue
        current = norm(original[index])
        if index in step_indexes:
            step_number = re.sub(r"\D", "", original[index])
            spoken.extend(["Hatua", "ya"] + ORDINALS[step_number].split())
            origins.extend([index] * (2 + len(ORDINALS[step_number].split())))
            index += 1
            continue
        if index in question_indexes:
            question_number = int(re.sub(r"\D", "", original[index]))
            spoken.extend(["Swali", "namba"] + number_to_swahili(question_number).split())
            origins.extend([index] * (2 + len(number_to_swahili(question_number).split())))
            index += 1
            continue
        if index in sequence_starts and re.fullmatch(r"\d+[.)]", original[index]):
            spoken.extend(["Swali", "namba", re.sub(r"\D", "", original[index])])
            origins.extend([index, index, index])
            index += 1
            continue
        if index in sequence_indexes:
            pieces = re.findall(r"_{1,}|\.{3,}|…+|,|[^,_…]+", original[index])
            for piece in pieces:
                piece = piece.strip()
                if not piece:
                    continue
                if piece == ",":
                    spoken.append("mkato")
                elif re.fullmatch(r"_{1,}|\.{3,}|…+", piece):
                    spoken.append("dashi")
                else:
                    spoken.append(piece)
                origins.append(index)
            index += 1
            continue
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
        embedded_operator = re.fullmatch(r"(\+|\-|−|–|â€“|âˆ’|×|Ã—)(\d+)[.,;:]?", original[index])
        numeric_symbol = original[index].strip(".,;:()[]{}")
        roman_symbol = numeric_symbol
        if embedded_operator:
            symbol, digits = embedded_operator.groups()
            operation = "kuongeza" if symbol == "+" else "kuzidisha" if symbol in {"×", "Ã—"} else "kutoa"
            number_words = number_to_swahili(int(digits)).split()
            spoken.extend([operation] + number_words)
            origins.extend([index] * (1 + len(number_words)))
        elif re.fullmatch(r"\d+", numeric_symbol):
            number_words = number_to_swahili(int(numeric_symbol)).split()
            spoken.extend(number_words)
            origins.extend([index] * len(number_words))
        elif re.fullmatch(r"[IVXLCDM]+", roman_symbol):
            roman_words = number_to_swahili(roman_to_int(roman_symbol)).split()
            spoken.extend(roman_words + ["ya", "Kirumi"])
            origins.extend([index] * (len(roman_words) + 2))
        elif current.startswith("gpe"):
            spoken.append("gipiee")
            origins.append(index)
        elif current == "education":
            spoken.append("edukesheni")
            origins.append(index)
        elif current.startswith("kkk"):
            spoken.extend(["kei", "kei", "kei"])
            origins.extend([index, index, index])
        elif "×" in original[index] or "Ã—" in original[index]:
            parts = re.split(r"(×|Ã—)", original[index])
            for part in parts:
                if not part:
                    continue
                spoken.append("kuzidisha" if part in {"×", "Ã—"} else part)
                origins.append(index)
        elif "=" in original[index]:
            parts = re.split(r"(=)", original[index])
            for part in parts:
                if not part:
                    continue
                if part == "=":
                    spoken.extend(["sawa", "sawa", "na"])
                    origins.extend([index, index, index])
                else:
                    spoken.append(part)
                    origins.append(index)
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


def needs_equals_audio(nodes):
    return any("=" in value for _, value in nodes)


def needs_sequence_audio(nodes):
    return any(
        re.search(r"(?:_{1,}|\.{3,}|…+)", value) and re.search(r"\d\s*,", value)
        for _, value in nodes
    )


def needs_arithmetic_audio(nodes):
    text = " ".join(value for _, value in nodes)
    return bool(re.search(r"\d\s*(?:\+|\-|−|–|â€“|âˆ’|×|Ã—)\s*\d\s*=", text))


def needs_multiplication_audio(nodes):
    text = " ".join(value for _, value in nodes)
    return bool(re.search(r"\d\s*(?:×|Ã—)\s*\d\s*=", text))


def needs_roman_audio(nodes):
    return any(
        re.search(r"(?<![A-Za-z])(?:[IVXLCDM]+)(?![A-Za-z])", value)
        for _, value in nodes
    )


def needs_steps_audio(nodes):
    in_steps = False
    for _, value in nodes:
        plain_value = re.sub(r"[^A-Za-zÀ-ž]+", " ", value).strip().lower()
        if plain_value == "hatua":
            in_steps = True
            continue
        if in_steps and re.match(r"^(?:mfano|zoezi|sura)\b", plain_value):
            in_steps = False
        if in_steps and re.match(r"^\s*\(?\d+[.)]?\s+", value):
            return True
    return False


def needs_number_words_audio(nodes):
    return any(re.search(r"(?<!\d)\d{2,}(?!\d)", value) for _, value in nodes)


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
    audio_path = output / audio_name
    temp_path = output / f".{audio_name}.tmp"
    cues = []
    try:
        with temp_path.open("wb") as audio:
            page_rate = "-20%" if 8 <= page <= 15 or page == 17 else RATE
            stream = edge_tts.Communicate(
                text, VOICE, rate=page_rate, boundary="WordBoundary",
                connect_timeout=15, receive_timeout=90,
            )
            iterator = stream.stream().__aiter__()
            while True:
                try:
                    event = await asyncio.wait_for(iterator.__anext__(), timeout=60)
                except StopAsyncIteration:
                    break
                except TimeoutError:
                    # Edge occasionally leaves an already-complete stream open.
                    # Once audio and word boundaries exist, inactivity means the
                    # useful payload has finished and is safe to keep.
                    expected_tail = [norm(token) for token in spoken if norm(token)][-3:]
                    actual_tail = [norm(cue["text"]) for cue in cues if norm(cue["text"])][-3:]
                    if cues and audio.tell() >= 1000 and actual_tail == expected_tail:
                        break
                    raise
                if event["type"] == "audio":
                    audio.write(event["data"])
                elif event["type"] == "WordBoundary":
                    start = event["offset"] / 10_000_000
                    duration = event["duration"] / 10_000_000
                    cues.append({"text": event["text"], "start": round(start, 6), "end": round(start + duration, 6)})
        temp_path.replace(audio_path)
    finally:
        if temp_path.exists():
            temp_path.unlink()
    apply_safe_mapping(cues, nodes, visible, old_entry.get("words", []))
    return {"audio": audio_name, "voice": VOICE, "rate": 0.8 if 8 <= page <= 15 or page == 17 else 0.9, "pitch": "neutral", "version": VERSION, "words": cues}


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
    parser.add_argument("--only-equals", action="store_true")
    parser.add_argument("--only-sequences", action="store_true")
    parser.add_argument("--only-arithmetic", action="store_true")
    parser.add_argument("--only-multiplication", action="store_true")
    parser.add_argument("--only-roman", action="store_true")
    parser.add_argument("--only-steps", action="store_true")
    parser.add_argument("--only-number-words", action="store_true")
    parser.add_argument("--page", type=int)
    args = parser.parse_args()
    timecodes_path = ROOT / "content" / "rehema" / "timecodes.json"
    timecodes = json.loads(timecodes_path.read_text(encoding="utf-8"))
    pages = sorted(ROOT.glob("pg*_sec001.html"), key=page_number)
    report = {"pages": 0, "regenerated": [], "remapped": [], "special": [], "failed": []}
    for path in pages:
        page = page_number(path)
        if args.page and page != args.page:
            continue
        _, nodes, visible = parse_page(path)
        if not nodes:
            continue
        if args.only_equals and not needs_equals_audio(nodes):
            continue
        if args.only_sequences and not needs_sequence_audio(nodes):
            continue
        if args.only_arithmetic and not needs_arithmetic_audio(nodes):
            continue
        if args.only_multiplication and not needs_multiplication_audio(nodes):
            continue
        if args.only_roman and not needs_roman_audio(nodes):
            continue
        if args.only_steps and not needs_steps_audio(nodes):
            continue
        if args.only_number_words and not needs_number_words_audio(nodes):
            continue
        old_entry = timecodes.get(str(page), {})
        special = needs_new_audio(nodes)
        if special:
            report["special"].append(page)
        selected_for_audio = (
            needs_number_words_audio(nodes) if args.only_number_words
            else needs_steps_audio(nodes) if args.only_steps
            else needs_roman_audio(nodes) if args.only_roman
            else needs_multiplication_audio(nodes) if args.only_multiplication
            else needs_arithmetic_audio(nodes) if args.only_arithmetic
            else needs_sequence_audio(nodes) if args.only_sequences
            else needs_equals_audio(nodes) if args.only_equals
            else special and (not args.only_mfano or needs_mfano_audio(nodes))
        )
        if args.generate_special and selected_for_audio:
            try:
                entry = await generate_audio(page, nodes, visible, old_entry)
                report["regenerated"].append(page)
            except Exception as error:
                report["failed"].append({"page": page, "error": str(error)})
                print(f"page={page} failed={error}", flush=True)
                continue
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
