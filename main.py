import requests

import os
import sys

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

def morning():
    weather = get_today_weather()
    print(weather)
    voice(f"おはようなのだ。今日の天気は{weather}なのだ。")

def main():
    morning()

if __name__ == "__main__":
    main()
