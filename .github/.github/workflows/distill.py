import json, os, subprocess, pathlib, textwrap, openai, slugify

openai.api_key = os.environ['OPENAI_API_KEY']

OUT_DIR = pathlib.Path('output')
OUT_DIR.mkdir(exist_ok=True)

for line in pathlib.Path('notes.jsonl').read_text(encoding='utf-8').splitlines():
    page = json.loads(line)
    title = page['properties']['Title']['title'][0]['plain_text']
    raw   = page['properties']['Raw']['rich_text'][0]['plain_text']

    prompt = f"""한글로 120자 이내 요약: {raw}\n\n
    이어서 3문제 퀴즈를 만들어 주세요."""
    resp = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role":"user","content":prompt}],
        max_tokens=400)
    body = resp.choices[0].message.content.strip()

    md = f"# {title}\n\n{body}"
    slug = slugify.slugify(title)[:40]
    md_path = OUT_DIR / f"{slug}.md"
    pdf_path = OUT_DIR / f"{slug}.pdf"
    md_path.write_text(md, encoding='utf-8')

    subprocess.run(["pandoc", md_path, "-o", pdf_path,
                    "--pdf-engine=xelatex"], check=True)
