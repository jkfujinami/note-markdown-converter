# note-markdown-converter

Note.comの記事をダウンロードし、Markdown形式に変換して保存するCLIツールです。記事内の画像も自動的にダウンロードし、ローカルパスにリンクを書き換えます。

## 特徴 (Features)

*   **Markdown変換**: Noteの記事（HTML）をMarkdownに変換します。見出し、リスト、引用、コードブロックなどに対応しています。
*   **画像ダウンロード**: 記事に含まれる画像を自動的にダウンロードし、Markdown内のリンクをローカルの画像パスに更新します。
*   **シンプルなCLI**: URLを渡すだけで実行可能です。

## 必要要件 (Requirements)

*   Python 3.8+
*   beautifulsoup4

## インストール (Installation)

このリポジトリをクローンし、依存関係をインストールしてください。

```bash
git clone https://github.com/jkfujinami/note-markdown-converter.git
cd note-markdown-converter
pip install .
```

または、開発モードでインストールする場合:

```bash
pip install -e .
```

## 使い方 (Usage)

インストール後、`note-dl` コマンドまたは `python -m note_downloader.main` で実行できます。

> **注意**: 現在のソースコードディレクトリ名が `note-markdown-converter` となっている場合、Pythonのインポートルールに従い `note_downloader` 等に変更する必要があるかもしれません。

### 基本的な使い方

```bash
# コマンドとして実行（推奨）
note-dl <Noteの記事URL>

# または python モジュールとして直接実行
python -m note_downloader.main <Noteの記事URL>
```

複数のURLを一度に指定することも可能です。

```bash
note-dl https://note.com/user/n/article1 https://note.com/user/n/article2
```

### 出力 (Output)

実行ディレクトリ直下に `downloads/` ディレクトリが作成され、その中にMarkdownファイルと画像ファイルが保存されます。

```text
downloads/
  ├── <記事タイトル>.md
  └── images/
       ├── <画像ID>.jpg
       └── ...
```

## 開発者向け情報

### プロジェクト構成

```text
src/note_downloader/
├── main.py       # エントリーポイント
├── cli.py        # (現在未使用) CLI引数処理用
├── converter.py  # HTML -> Markdown 変換ロジック
├── fetcher.py    # Note API v3 データ取得
├── saver.py      # ファイル・画像保存処理
└── models.py     # データモデル (Data Classes)
```

### TODO

*   CLI引数（出力先ディレクトリ指定など）のサポート強化
*   TOC（目次）の動的生成
*   テストコードの追加

## License

MIT License
