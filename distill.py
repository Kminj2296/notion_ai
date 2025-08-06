import os, json, subprocess, pathlib, textwrap
import openai
from slugify import slugify

client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])

OUT_DIR = pathlib.Path("output")
OUT_DIR.mkdir(exist_ok=True)

for line in pathlib.Path("notes.jsonl").read_text(encoding="utf-8").splitlines():
    page = json.loads(line)

    # 제목과 Raw가 비어 있으면 건너뜀
    title_prop = page["properties"]["Title"]["title"]
    raw_prop   = page["properties"]["Raw"]["rich_text"]
    if not title_prop or not raw_prop:
        continue

    title = title_prop[0]["plain_text"]
    raw   = raw_prop[0]["plain_text"]

    prompt = textwrap.dedent(f"""
        다음 내용을 한국어 120자 이내로 요약하고
        이어서 3문제 퀴즈를 만들어 주세요.

        === 원본 ===
        {raw}
    """)

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=400,
        temperature=0.7
    )

    body = resp.choices[0].message.content.strip()

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
