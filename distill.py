# distill.py  (openai ≥1.0.0 호환 버전)

import os, json, subprocess, pathlib, textwrap
import openai
from slugify import slugify          # python-slugify

# 1) API 키 설정 ― ChatCompletion은 더 이상 global key 사용 권장 X
client = openai.OpenAI(
    api_key=os.environ["OPENAI_API_KEY"]
)

OUT_DIR = pathlib.Path("output")
OUT_DIR.mkdir(exist_ok=True)

# 노션에서 추출된 메모 JSONL 읽기
for line in pathlib.Path("notes.jsonl").read_text(encoding="utf-8").splitlines():
    page = json.loads(line)

    # 제목 & 내용 추출 (빈 값 방지용 검사)
    title_prop = page["properties"]["Title"]["title"]
    if not title_prop:
        print("⏭️  Title empty – skipping")
        continue
    raw_prop = page["properties"]["Raw"]["rich_text"]
    if not raw_prop:
        print("⏭️  Raw empty – skipping")
        continue

    title = title_prop[0]["plain_text"]
    raw   = raw_prop[0]["plain_text"]

    prompt = textwrap.dedent(f"""
        다음 내용을 한국어 120자 이내로 요약하고
        이어서 3문제 퀴즈를 만들어 주세요.

        === 원본 ===
        {raw}
    """)

    # 2) 1.x형 API 호출
    resp = client.chat.completions.create(
        model="gpt-4o-mini",          # 필요 시 모델명 변경
        messages=[{"role": "user", "content": prompt}],
        max_tokens=400,
        temperature=0.7
    )

    body = resp.choices[0].message.content.strip()

    # 3) Markdown → PDF
    md = f"# {title}\n\n{body}"
    slug = slugify(title)[:40]
    md_path  = OUT_DIR / f"{slug}.md"
    pdf_path = OUT_DIR / f"{slug}.pdf"

    md_path.write_text(md, encoding="utf-8")
    subprocess.run(
        ["pandoc", md_path, "-o", pdf_path, "--pdf-engine=xelatex"],
        check=True
    )
    print("✅  PDF created:", pdf_path)
