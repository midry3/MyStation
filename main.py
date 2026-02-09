import requests

import os
import sys
import argparse
import datetime
import json
import random
import subprocess
import tarfile
import time
from threading import Thread

from alive_progress import alive_bar
from pydub import AudioSegment

WORDS = "abcdefghijklmnopqrstuvwxyz"

ALARM_FILE = "audio/alarm.mp3"
BGM_FILE = "bgm.txt"
PASS_LENGTH = 5
SCRIPT_FILE = "script.json"
VOICE_DIR = "reading"
STATION_FILE = "stream.wav"

AREA_CODE = "070000"

VOICEVOX_TAR = "voicevox.tar.gz"
VOICEVOX_RUN = "VOICEVOX/vv-engine/run"
VOICEVOX_URL = "https://github.com/VOICEVOX/voicevox/releases/download/0.25.1/voicevox-linux-cpu-x64-0.25.1.tar.gz"

FOREST_ENDPOINT = f"https://www.jma.go.jp/bosai/forecast/data/forecast/{AREA_CODE}.json"

AUDIO_ENDPOINT = "http://localhost:50021/audio_query"
SYNTHESIS_ENDPOINT = "http://localhost:50021/synthesis"

def download_with_progress(url: str, dst_path: str, chunk_size: int = 1024 * 64):
    with requests.get(url, stream=True) as r:
        r.raise_for_status()

        total = r.headers.get("Content-Length")
        total = int(total) if total is not None else None

        with open(dst_path, "wb") as f:
            if total is not None:
                with alive_bar(
                    total
                ) as bar:
                    for chunk in r.iter_content(chunk_size=chunk_size):
                        if not chunk:
                            continue
                        f.write(chunk)
                        bar(len(chunk))
            else:
                with alive_bar(
                    unknown="bytes"
                ) as bar:
                    for chunk in r.iter_content(chunk_size=chunk_size):
                        if not chunk:
                            continue
                        f.write(chunk)
                        bar(len(chunk))

def ready_voicevox():
    if not os.path.isfile(VOICEVOX_RUN):
        install_voicevox()
    return subprocess.Popen([VOICEVOX_RUN])

def install_voicevox():
    print("download voicevox ...")
    download_with_progress(VOICEVOX_URL, VOICEVOX_TAR)
    print("\nextracting ...")
    with tarfile.open(VOICEVOX_TAR, "r:gz") as tar:
        tar.extractall(".")
    print("\033[33mdone\033[0m.")

def prepare(wait: int, debug=False):
    time.sleep(wait)
    subprocess.run(["gemini", "-y", "-p", "prompt.mdに従って処理を実行"], shell=True)
    with open(SCRIPT_FILE, "r", encoding="utf-8") as f:
        script = json.load(f)
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
        if i != len(voices) - 1:
            result += AudioSegment.silent(duration=random.randint(300, 700))
    result.export(STATION_FILE, format="wav")

def get_bgm() -> str:
    with open(BGM_FILE, "r") as f:
        bgm = f.read().splitlines()
    res = random.choice(bgm)
    while res == "":
        res = random.choice(bgm)
    return res

def play_bgm():
    return subprocess.Popen(
        ["mpv", "--loop", get_bgm()],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        shell=True
    )

def make_words() -> str:
    res = ""
    for _ in range(PASS_LENGTH):
        res += random.choice(WORDS)
    return res

def morning():
    pass_ = make_words()
    p = subprocess.Popen(
        ["mpv", "--loop", ALARM_FILE],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        shell=True
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
    p = play_bgm()
    try:
        subprocess.run(
            ["ffplay", "-nodisp", STATION_FILE],
            shell=True
        )
    finally:
        p.terminate()

def main():
    if not os.path.isfile(VOICEVOX_RUN):
        install_voicevox()
    parser = argparse.ArgumentParser(description="Set an alarm and get today's weather.")
    parser.add_argument("hour", type=int, help="Hour for the alarm (0-23)")
    parser.add_argument("minute", type=int, help="Minute for the alarm (0-59)")
    args = parser.parse_args()

    alarm_hour = args.hour
    alarm_minute = args.minute

    if not (0 <= alarm_hour <= 23 and 0 <= alarm_minute <= 59):
        print("Invalid hour or minute. Hour must be 0-23, Minute must be 0-59.", file=sys.stderr)
        sys.exit(1)

    now = datetime.datetime.now()
    alarm_time = now.replace(hour=alarm_hour, minute=alarm_minute, second=0, microsecond=0)
    if alarm_time < now:
        alarm_time += datetime.timedelta(days=1)
    prepare_time = alarm_time - datetime.timedelta(minute=20)
    time_to_alarm = (alarm_time - now).total_seconds()
    time_to_prepare = (prepare_time_time - now).total_seconds()
    print(f"Alarm set for {alarm_time.strftime('%H:%M')}. Waiting for {int(time_to_wait)} seconds...")
    t = Thread(target=prepare, args=(time_to_prepare,))
    t.start()
    time.sleep(time_to_alarm)

    print("Alarm ringing!")
    morning()
    start_station()

if __name__ == "__main__":
    main()
