"""원고(src/*.html)를 합쳐 book.html을 만들고, Chrome 헤드리스로 PDF를 출력한다."""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
OUT_HTML = ROOT / "한권으로끝내는_보험보장가이드.html"
OUT_PDF = ROOT / "한권으로끝내는_보험보장가이드.pdf"
CHROME_CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
]

parts = sorted(p for p in SRC.glob("*.html") if p.name[0].isdigit())
body = "\n".join(p.read_text(encoding="utf-8") for p in parts)

# 목차 자동 생성: 파트 구분 페이지와 장 제목을 순서대로 수집
toc = ['<section class="toc"><h1>차례</h1>']
pattern = re.compile(
    r'<section class="divider">.*?<div class="num">(.*?)</div>\s*<h1>(.*?)</h1>'
    r'|<span class="no">((?:CHAPTER|APPENDIX) .*?)</span>\s*<h1>(.*?)</h1>',
    re.S,
)
for m in pattern.finditer(body):
    if m.group(1):
        toc.append(f'<div class="part">{m.group(1)} · {re.sub("<.*?>", "", m.group(2).replace("<br>", " — "))}</div>')
    else:
        no = m.group(3).replace("CHAPTER ", "").replace("APPENDIX ", "부록 ")
        toc.append(f'<div class="item"><span>{no}</span><span>{re.sub("<.*?>", " ", m.group(4))}</span></div>')
toc.append("</section>")
body = body.replace("<!--TOC-->", "\n".join(toc))

css = (SRC / "style.css").read_text(encoding="utf-8")

# 이미지(사진·QR)를 HTML 안에 넣어 한 파일로 배포할 수 있게 한다
import base64
for img in SRC.glob("*.*"):
    if img.suffix.lower() in (".jpg", ".jpeg", ".png"):
        mime = "image/png" if img.suffix.lower() == ".png" else "image/jpeg"
        data = base64.b64encode(img.read_bytes()).decode()
        body = body.replace(f'src="{img.name}"', f'src="data:{mime};base64,{data}"')
html = f"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8">
<title>한 권으로 끝내는 보험 보장 가이드</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
{css}
</style>
</head><body>
{body}
</body></html>"""
OUT_HTML.write_text(html, encoding="utf-8")
print("HTML:", OUT_HTML)

chrome = next((c for c in CHROME_CANDIDATES if Path(c).exists()), None)
if not chrome:
    sys.exit("Chrome/Edge를 찾지 못했습니다.")
subprocess.run(
    [chrome, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
     f"--print-to-pdf={OUT_PDF}", OUT_HTML.as_uri()],
    check=True, timeout=300,
)
print("PDF:", OUT_PDF)
