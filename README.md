# note-markdown-converter

Note.comの記事をダウンロードし、Markdown形式に変換して保存するCLIツールです。記事内の画像も自動的にダウンロードし、ローカルパスにリンクを書き換えます。

## 特徴 (Features)

*   **高精度なMarkdown変換**: Noteの内部API構造を解析し、HTMLタグとMarkdownの正確なマッピングを実装。見出し、リスト、引用、コードブロックなどを忠実に再現します。
*   **目次の自動生成**: 記事内の見出し構成（h2, h3）を解析し、Markdown内の適切な位置に目次を自動生成・挿入します。
*   **完全な画像サポート**:
    *   記事内の画像だけでなく、**ヘッダー画像（アイキャッチ）**の取得にも対応。
    *   すべての画像をローカルに自動ダウンロードし、Markdown内のリンクをローカルパスに自動で書き換えます。
*   **柔軟なダウンロード**:
    *   記事単位（URLまたはKey指定）
    *   **ユーザー単位（ユーザーURL指定で全記事一括ダウンロード）**
*   **シンプルなCLI**: 直感的なコマンドライン操作。出力先ディレクトリも指定可能。

## 他のダウンローダーとの違い

多くのNoteダウンローダーは単にHTMLをMarkdownに変換するライブラリを通すだけですが、本ツールは以下の点で異なります：

1.  **Note専用の最適化**: Note記事のDOM構造やAPIレスポンス（v3）を解析し、独自のマッピングルールを作成しているため、変換精度が非常に高いです。
2.  **ヘッダー画像の取得**: 多くのツールが見落としがちな、記事の「顔」であるヘッダー画像（アイキャッチ）も確実に取得し、Markdownの冒頭に配置します。
3.  **完全なオフライン化**: 記事内の画像をすべてローカルに保存しリンクを置換するため、元記事が消えても手元に完全なバックアップを残せます。

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

インストール後、`note-dl` コマンドまたは `python -m note_markdown_converter.main` で実行できます。

> **Note**: コマンド名は設定により異なりますが、リポジトリ内のスクリプトとして実行する場合は以下のようにします。
> `python -m src.note-markdown-converter.main [オプション] [ターゲット]`

### 基本的な使い方

**1. 記事を単体でダウンロード**
URLまたは記事Key（ID）を指定します。

```bash
# URL指定（自動判別）
python -m src.note-markdown-converter.main --url https://note.com/user/n/n1234567890

# Key指定
python -m src.note-markdown-converter.main --id n1234567890
```

**2. ユーザーの全記事を一括ダウンロード**
ユーザーのプロフィールURLを指定すると、そのユーザーの公開記事をすべて取得します。

```bash
python -m src.note-markdown-converter.main --user https://note.com/fuji1080
```

**3. 簡易実行（自動判別）**
フラグなしで渡すと、入力内容から自動で判断します。

```bash
# 複数のURLやKeyを渡すことも可能
python -m src.note-markdown-converter.main na3c861f59d8b https://note.com/another_user
```

### オプション (Options)

*   `-h`, `--help`: ヘルプを表示
*   `--user USER`: 指定したユーザーID/URLの記事をすべてダウンロード
*   `--id ID`: 指定した記事Key(ID)の記事をダウンロード
*   `--url URL`: 指定したURL（記事またはユーザー）をダウンロード
*   `-o DIRECTORY`, `--output DIRECTORY`: 出力先のディレクトリを指定（デフォルト: `downloads`）

### 出力 (Output)

実行ディレクトリ直下に `downloads/` ディレクトリが作成され、その中にMarkdownファイルと画像ファイルが保存されます。

```text
downloads/
  ├── <記事タイトル>/
  │    ├── <記事タイトル>.md
  │    └── images/
  │         ├── <画像ID>.jpg
  │         └── ...
```

## 開発者向け情報

### プロジェクト構成

```text
src/note-markdown-converter/
├── main.py       # エントリーポイント
├── cli.py        # (現在未使用) CLI引数処理用
├── converter.py  # HTML -> Markdown 変換ロジック
├── fetcher.py    # Note API v3 データ取得
├── saver.py      # ファイル・画像保存処理
└── models.py     # データモデル (Data Classes)
```

## License

MIT License
