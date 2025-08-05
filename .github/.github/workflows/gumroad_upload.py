import os, requests, pathlib, json, time

TOKEN = os.environ['GUMROAD_TOKEN']
HEAD  = {"Authorization": f"Bearer {TOKEN}"}

for pdf in pathlib.Path('output').glob('*.pdf'):
    title = pdf.stem.replace('-', ' ').title()
    # 1) 상품 생성 (Draft)
    draft = requests.post(
        "https://api.gumroad.com/v2/products",
        headers=HEAD,
        data={"name": title, "price": 3000, "custom_permalink": str(int(time.time()))})
    pid = draft.json()['product']['id']
    # 2) 파일 업로드
    with open(pdf, 'rb') as f:
        requests.post(
            f"https://api.gumroad.com/v2/products/{pid}/files",
            headers=HEAD,
            files={'file': f})
    print("Uploaded:", title)
