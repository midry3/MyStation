# 目覚まし & ラジオ自動作成ツール
ずんだもんと四国めたんのラジオ番組を自動で作って再生してくれるプログラムです。目覚まし付き。

# 対象プラットフォーム
- Windows 11
- Linux
- Mac

Macは持っておらず動作確認が出来てませんが多分動きます。

# 必要な物
- Node.js
- gemini-cli
- Python 3.13>=
- ffmpeg, ffplay
- Git (なければzipをダウンロードしてください)
- yt-dlp (BGM用、要らなければ不要)
- uv (あれば楽)

それぞれ各自で調べてインストールしてください。

手元での検証では、`npx`からの`gemini-cli`は不可です。

# 導入
```bash
$ git clone https://github.com/midry3/MyStation
$ cd MyStation
$ pip install .
```

また、もし`gemini-cli`をこれまで使用したことがなければ、以下のコマンドを実行しGoogleアカウントにログインしておいてください。一度ログインすれば以降は不要です。
```bash
$ gemini
```

## VOICEVOXを既にダウンロードしてある方
VOICEVOXがない場合は自動でダウンロードとセットアップをしますが、既にある場合はそちらを使用することが出来ます。
`run`(Windows環境では`run.exe`)が含まれている**ディレクトリ**の絶対パスを`config.json`の`voicevox_engine`に指定してください。

# 使い方
```bash
# 朝の7時10分に目覚まし & ラジオ再生
$ python main.py 7 10

# アラームなしでラジオだけ
$ python main.py

# uv
$ uv run main.py
```

ラジオの作成には10分程度時間を要します。アラーム付きの場合はアラームの20分前からラジオ作成を始めます。

# アラーム音の指定
`config.json`の`alarm`にアラーム音として使いたい音声ファイルを指定してください。
デフォルトは`audio/alarm.mp3`です。

# ラジオ中にBGMをかける方法
`bgm.txt`にBGMとしてかけたい曲を改行区切りで列挙すれば、そこからランダムに一曲選んでラジオ中に流すことが出来ます。(yt-dlpが対応しているプラットフォームであれば全て可能です)

なお補助スクリプトとして、`make_bgm_list.sh`があります。

YouTubeであらかじめBGM用のプレイリストを作成してください。 
その後
```
$ sh make_bgm_list.sh プレイリストのURL
```

を実行すると`bgm.txt`が生成されます。

# 作る番組の指定について
[prompt.md](./prompt.md)がAIに渡す指示文です。つまり、このファイルを編集すれば好きな番組を作ることが可能になります。


