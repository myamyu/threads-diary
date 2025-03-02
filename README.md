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

```
uv run main.py
```

```
uv run main.py 2025-03-01
```

```
uv run main.py all 2024-01-01
```
