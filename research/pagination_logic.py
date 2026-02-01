import urllib.request
import json
import time

def fetch_all_note_keys(user_urlname):
    """
    指定されたユーザーの全記事のKeyを取得するサンプルロジック
    """
    base_url = "https://note.com/api/v2/creators/{}/contents?kind=note&page={}"
    page = 1
    all_keys = []

    print(f"Start fetching for user: {user_urlname}")

    while True:
        url = base_url.format(user_urlname, page)
        print(f"Fetching page {page}...", end="", flush=True)

        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) asres:
                data = json.loads(res.read())

                # レスポンスデータの検証
                api_data = data.get('data', {})
                if not api_data:
                    print(" No data found.")
                    break

                contents = api_data.get('contents', [])
                is_last_page = api_data.get('isLastPage', False)
                total_count = api_data.get('totalCount', 0)

                # Keyを抽出
                keys = [note.get('key') for note in contents if note.get('key')]
                all_keys.extend(keys)

                print(f" Got {len(keys)} items. (Total progress: {len(all_keys)}/{total_count} estimated)")

                # 判定ロジック: isLastPageがTrueなら終了
                if is_last_page:
                    print("Reached last page.")
                    break

                # 安全策: もしcontentsが空なら強制終了
                if not contents:
                    print("Contents empty, stopping.")
                    break

                page += 1
                time.sleep(1) # API制限への配慮

        except Exception as e:
            print(f"\nError occurred: {e}")
            break

    return all_keys

if __name__ == "__main__":
    # テスト実行
    target_user = "fuji1080"
    keys = fetch_all_note_keys(target_user)
    print(f"\nTotal keys collected: {len(keys)}")
    print("Sample keys (first 5):", keys[:5])
