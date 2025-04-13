# Threads日記

Threadsの自分の投稿を日記形式で保存する。

## 開発準備

最初に `uv sync` してください。

### .env

```
THREADS_TOKEN=
```

- THREADS_TOKEN  
  Meta Appsのユースケース > カスタマイズ >  ユーザートークン生成ツールで取得したトークン。

## 実行

### データ収集

```
uv run main_collect_data.py
```

```
uv run main_collect_data.py 2025-03-01
```

```
uv run main_collect_data.py all 2024-01-01
```

### mdファイル作成

```
uv run main_output_md.py
```
