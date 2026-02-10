import json
import os
import platform
import shlex
import sys

def get_voicevox_engine_url(version="0.25.1") -> str | None:
    system = platform.system().lower()
    machine = platform.machine().lower()
    if system == "windows":
        if "64" in machine:
            asset = f"voicevox_engine-windows-cpu-{version}.7z.001"
        else:
            return None
    elif system == "darwin":
        if "arm64" in machine:
            asset = f"voicevox_engine-macos-arm64-{version}.7z.001"
        else:
            asset = f"voicevox_engine-macos-x64-{version}.7z.001"
    elif system == "linux":
        if "arm64" in machine or "aarch64" in machine:
            asset = f"voicevox_engine-linux-cpu-arm64-{version}.7z.001"
        else:
            asset = f"voicevox_engine-linux-cpu-x64-{version}.7z.001"
    else:
        return None
    base = "https://github.com/VOICEVOX/voicevox_engine/releases/download"
    return f"{base}/{version}/{asset}"

CONFIG_FILE = "config.json"

if os.path.isfile(CONFIG_FILE):
    with open(CONFIG_FILE, "r") as f:
        conf = json.load(f)
else:
    conf = {}

AI = shlex.split(conf.get("ai", "npx @google/gemini-cli -y -p 'prompt.mdに従って処理'"))

WORDS = "abcdefghijklmnopqrstuvwxyz"
BGM_VOLUME = conf.get("bgm_volume", 15)
WAIT_FOR_BGM = 15

ALARM_FILE = conf.get("alarm", "./audio/alarm.mp3")
BGM_FILE = "./bgm.txt"
PASS_LENGTH = conf.get("pass_length", 5)
SCRIPT_FILE = "./script.json"
VOICE_DIR = "./reading"
RADIO_FILE = "radio.wav"

# BGMプレイヤーは標準入力を受け取るコマンド
BGM_PLAYER = shlex.split(conf.get("bgm_player", "ffplay -nodisp -vn -loop 0 -volume '{volume}' -loglevel quiet -i -").format(volume=BGM_VOLUME))
ALARM_PLAYER = shlex.split(conf.get("alarm_player", "ffplay -nodisp -vn -loop 0 -i '{file}'").format(file=ALARM_FILE))
RADIO_PLAYER = shlex.split(conf.get("radio_player", "ffplay -nodisp -vn -autoexit -loglevel info -i '{file}'").format(file=RADIO_FILE))

VOICEVOX_7Z = "voicevox_engine.7z"
DEFAULT_VOICEVOX_ENGINE = "./VOICEVOX"
VOICEVOX_ENGINE_DIR = conf.get("voicevox_engine", DEFAULT_VOICEVOX_ENGINE)
AUDIO_ENDPOINT = "http://localhost:50021/audio_query"
SYNTHESIS_ENDPOINT = "http://localhost:50021/synthesis"

LOG_DIR = "./log"
AI_LOG_FILE = "./log/ai.log"
VOICEVOX_LOG_FILE = "./log/voicevox.log"

is_windows = platform.system().lower() == "windows"

if is_windows:
    VOICEVOX_RUN = os.path.join(VOICEVOX_ENGINE_DIR, "run.exe")
else:
    VOICEVOX_RUN = os.path.join(VOICEVOX_ENGINE_DIR, "run")

VOICEVOX_ENGINE_URL = get_voicevox_engine_url(conf.get("voicevox_version", "0.25.1"))

if VOICEVOX_ENGINE_URL is None and not os.path.isfile(VOICEVOX_RUN):
    print("It seems voicevox does not support this environment.")
    sys.exit(1)