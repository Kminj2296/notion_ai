import os, json, requests, datetime, pathlib

TOKEN   = os.environ['NOTION_TOKEN']
HEADERS = {"Authorization": f"Bearer {TOKEN}",
           "Notion-Version": "2022-06-28",
           "Content-Type": "application/json"}

DB_ID   = pathlib.Path('.github/notion_db_id.txt').read_text().strip()

def query():
    url = f"https://api.notion.com/v1/databases/{DB_ID}/query"
    payload = {
        "filter": {
            "and":[
                {"property":"Tag","multi_select":{"contains":"sell"}},
                {"property":"Status","select":{"equals":"new"}}
            ]
        }
    }
    resp = requests.post(url, headers=HEADERS, data=json.dumps(payload))
    resp.raise_for_status()
    return resp.json()["results"]

notes = query()
pathlib.Path('notes.jsonl').write_text(
    '\n'.join(json.dumps(page) for page in notes), encoding='utf-8')
