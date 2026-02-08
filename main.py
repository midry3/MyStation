import requests

import os
import sys
import argparse
import datetime
import time
from playsound import playsound, PlaysoundException

AREA_CODE = "070000"
FOREST_ENDPOINT = f"https://www.jma.go.jp/bosai/forecast/data/forecast/{AREA_CODE}.json"

AUDIO_ENDPOINT = "http://localhost:50021/audio_query"
SYNTHESIS_ENDPOINT = "http://localhost:50021/synthesis"

def get_today_weather() -> str:
    data = requests.get(FOREST_ENDPOINT).json()
    return data[0]["timeSeries"][0]["areas"][2]["weathers"][0]

def voice(text, dest="a.wav"):
    query_payload = {"text": text, "speaker": 3}
    query_response = requests.post(AUDIO_ENDPOINT, params=query_payload)

    if query_response.status_code != 200:
        print(f"Error in audio_query: {query_response.text}", file=sys.stderr)
        return

    query = query_response.json()
    synthesis_payload = {"speaker": 3}
    synthesis_response = requests.post(SYNTHESIS_ENDPOINT, params=synthesis_payload, json=query)
    if synthesis_response.status_code == 200:
        with open(dest, "wb") as f:
            f.write(synthesis_response.content)
        print(f"音声が {os.path.abspath(dest)} に保存されました。")
    else:
        print(f"Error in synthesis: {synthesis_response.text}", file=sys.etderr)

def start_station():
    weather = get_today_weather()
    print(weather)
    voice(f"おはようなのだ。今日の天気は{weather}なのだ。")

def main():
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

    time_to_wait = (alarm_time - now).total_seconds()
    print(f"Alarm set for {alarm_time.strftime('%H:%M')}. Waiting for {int(time_to_wait)} seconds...")
    time.sleep(time_to_wait)

    print("Alarm ringing!")
    alarm_file = "alarm.wav"
    if os.path.exists(alarm_file):
        try:
            playsound(alarm_file)
        except PlaysoundException as e:
            print(f"Could not play alarm sound: {e}", file=sys.stderr)
    else:
        print(f"Alarm file '{alarm_file}' not found. Skipping alarm sound.", file=sys.stderr)
    start_station()

if __name__ == "__main__":
    main()
