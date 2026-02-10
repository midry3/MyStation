from settings import *

import py7zr
import requests

import os
import datetime
import json
import random
import subprocess
import sys
import time
from threading import Thread

from alive_progress import alive_bar
from pydub import AudioSegment

BARS = [
    "smooth",
    "classic",
    "classic2",
    "brackets",
    "blocks",
    "bubbles",
    "solid",
    "checks",
    "circles",
    "squares",
    "halloween",
    "filling",
    "notes",
    "ruler",
    "ruler2",
    "fish",
    "scuba"
]

SPINNERS = [
    "classic",
    "stars",
    "twirl",
    "twirls",
    "horizontal",
    "vertical",
    "waves",
    "waves2",
    "waves3",
    "dots",
    "dots_waves",
    "dots_waves2",
    "it",
    "ball_belt",
    "balls_belt",
    "triangles",
    "brackets",
    "bubbles",
    "circles",
    "squares",
    "flowers",
    "elements",
    "loving",
    "notes",
    "notes2",
    "arrow",
    "arrows",
    "arrows2",
    "arrows_in",
    "arrows_out",
    "radioactive",
    "boat",
    "fish",
    "fish2",
    "fishes",
    "crab",
    "alive",
    "wait",
    "wait2",
    "wait3",
    "wait4",
    "pulse"
]

class BGM:
    def __init__(self, url: str):
        self.ytdlp = subprocess.Popen(
            ["yt-dlp", "-qx", "-o", "-", get_bgm()],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL
        )
        self.ffplay = subprocess.Popen(
            BGM_PLAYER,
            stdin=self.ytdlp.stdout,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        self.ytdlp.stdout.close()

    def __enter__(self):
        return self

    def __exit__(self, _, __, ___):
        self.ffplay.terminate()
        self.ytdlp.terminate()

def download_with_progress(url: str, dst_path: str, chunk_size: int = 1024 * 64):
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        total = r.headers.get("Content-Length")
        total = int(total) if total is not None else None
        with open(dst_path, "wb") as f:
            if total is not None:
                with alive_bar(
                    total,
                    bar=random.choice(BARS),
                    spinner=random.choice(SPINNERS)
                ) as bar:
                    for chunk in r.iter_content(chunk_size=chunk_size):
                        if not chunk:
                            continue
                        f.write(chunk)
                        bar(len(chunk))
            else:
                with alive_bar(
                    unknown="bytes",
                    bar=random.choice(BARS),
                    spinner=random.choice(SPINNERS)
                ) as bar:
                    for chunk in r.iter_content(chunk_size=chunk_size):
                        if not chunk:
                            continue
                        f.write(chunk)
                        bar(len(chunk))

def ready_voicevox(log):
    if not os.path.isfile(VOICEVOX_RUN):
        install_voicevox()
    return subprocess.Popen(
        [VOICEVOX_RUN],
        stdin=subprocess.DEVNULL,
        stdout=log,
        stderr=log,
        text=True
    )

def install_voicevox():
    print("downloading voicevox ...")
    download_with_progress(VOICEVOX_ENGINE_URL, VOICEVOX_7Z)
    print("\nextracting ...")
    with py7zr.SevenZipFile(VOICEVOX_7Z, mode="r") as z:
        z.extractall(path=".")
        os.rename(z.getnames()[0], DEFAULT_VOICEVOX_ENGINE)
    print("________\033[33mdone\033[0m________.")

def prepare(wait: int, debug=False):
    time.sleep(wait)
    now = datetime.datetime.now()
    with open(VOICEVOX_LOG_FILE, "a") as fv:
        fv.write(f"________{now}________\n")
        fv.flush()
        p = ready_voicevox(fv)
        print("start voicevox.")
        try:
            with open(GEMINI_LOG_FILE, "a") as fg:
                try:
                    fg.write(f"________{now}________\n")
                    fg.flush()
                    subprocess.run(
                        AI,
                        stdout=fg,
                        stderr=fg,
                        text=True,
                        shell=is_windows
                    )
                finally:
                    fg.flush()
                    fg.write("\n________end.________\n\n")
            with open(SCRIPT_FILE, "r", encoding="utf-8") as f:
                script = json.load(f)
            if not os.path.isdir(VOICE_DIR):
                os.mkdir(VOICE_DIR)
            voices = []
            for n, s in enumerate(script):
                if 0 < s["speaker"]:
                    path = os.path.join(VOICE_DIR, f"voice_{n+1}.wav")
                    if debug:
                        print(f"[{n+1}/{len(script)}] `{path}`, {(s["speaker"])}: {(s["text"])}")
                    make_voice(s["text"], s["speaker"], path)
                    voices.append(path)
            result = AudioSegment.empty()
            if debug:
                print("joining...")
            for i, f in enumerate(voices):
                if debug:
                    print(f"[{i+1}/{len(voices)}]")
                audio = AudioSegment.from_file(f)
                result += audio
                if i == len(voices) - 1:
                    result += AudioSegment.silent(duration=2000)
                else:
                    result += AudioSegment.silent(duration=random.randint(300, 700))
            result.export(RADIO_FILE, format="wav")
        finally:
            p.terminate()
            fv.flush()
            fv.write("\n________closed.________\n\n")
            print("made a new program.")

def get_bgm() -> str:
    with open(BGM_FILE, "r") as f:
        bgm = f.read().splitlines()
    res = random.choice(bgm)
    while res == "":
        res = random.choice(bgm)
    return res

def make_words() -> str:
    res = ""
    for _ in range(PASS_LENGTH):
        res += random.choice(WORDS)
    return res

def morning():
    pass_ = make_words()
    p = subprocess.Popen(
        ALARM_PLAYER,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    while True:
        if pass_ == input(f"{pass_}: ").strip(): break
    p.terminate()

def make_voice(text: str, speaker: int, dest):
    query_payload = {"text": text, "speaker": speaker}
    query_response = requests.post(AUDIO_ENDPOINT, params=query_payload)

    if query_response.status_code != 200:
        print(f"Error in audio_query: {query_response.text}", file=sys.stderr)
        return

    query = query_response.json()
    synthesis_payload = {"speaker": speaker}
    synthesis_response = requests.post(SYNTHESIS_ENDPOINT, params=synthesis_payload, json=query)
    if synthesis_response.status_code == 200:
        with open(dest, "wb") as f:
            f.write(synthesis_response.content)
    else:
        print(f"Error in synthesis: {synthesis_response.text}", file=sys.etderr)

def start_station():
    print("______start program!______")
    with BGM(get_bgm()):
        time.sleep(WAIT_FOR_BGM)
        subprocess.run(
            RADIO_PLAYER
        )

def main():
    if not os.path.isdir(LOG_DIR):
        os.mkdir(LOG_DIR)
    if not os.path.isfile(VOICEVOX_RUN):
        install_voicevox()
    match len(sys.argv):
        case 1:
            alarm_hour = -1
            alarm_minute = 0
        case 2:
            alarm_hour = int(sys.argv[1])
            alarm_minute = 0
        case 3:
            alarm_hour = int(sys.argv[1])
            alarm_minute = int(sys.argv[2])
        case _:
            print("too many arguments! (<=2)")
            sys.exit(1)
    if alarm_hour == -1:
        prepare(0)
        start_station()
    else:
        if not (0 <= alarm_hour <= 23 and 0 <= alarm_minute <= 59):
            print("Invalid hour or minute. Hour must be 0-23, Minute must be 0-59.", file=sys.stderr)
            sys.exit(1)
        now = datetime.datetime.now()
        alarm_time = now.replace(hour=alarm_hour, minute=alarm_minute, second=0, microsecond=0)
        if alarm_time < now:
            alarm_time += datetime.timedelta(days=1)
        prepare_time = alarm_time - datetime.timedelta(minutes=20)
        time_to_alarm = (alarm_time - now).total_seconds()
        time_to_prepare = (prepare_time - now).total_seconds()
        print(f"Alarm set for {alarm_time.strftime("%H:%M")}.")
        t = Thread(target=prepare, args=(max(0, time_to_prepare),))
        t.start()
        time.sleep(time_to_alarm)
        print("Alarm ringing!")
        morning()
        start_station()

if __name__ == "__main__":
    main()
