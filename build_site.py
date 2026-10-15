"""전자책 원고(../전자책/src)를 메뉴형 홈페이지(여러 HTML 페이지)로 변환한다.

생성물
  index.html            홈(분야별 메뉴, 검색, 자주 찾는 주제)
  cat-<분야>.html        대분류 페이지(파트 → 장 목록)
  ch01~ch41.html        장별 본문
  appA~appD.html        자료실(부록)
  about.html            머리말·면책 고지
  assets/site.js        메뉴·검색 스크립트(검색 색인 포함)
  _artifact_home.html   Artifact 게시용 홈(doctype 없는 버전)
"""
import html
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "전자책" / "src"
OUT = HERE

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@500'
         '&family=IBM+Plex+Sans+KR:wght@400;500;700&family=Noto+Serif+KR:wght@700;900&display=swap">')
SITE_NAME = "보험 보장 가이드"

# ▼▼▼ 상담·연락처 설정 — 여기만 바꾸면 사이트 전체에 반영됩니다 ▼▼▼
CONTACT = {
    "name": "박혜경",                               # 상담사 이름
    "role": "보험친구 · 보장분석 상담",                     # 직함/소개 한 줄
    "company": "(주)뉴니케 보험자산관리전문회사(GA)",            # 소속
    "reg_no": "NK301239",# 보험설계사 등록번호(광고 시 표시)
    "phone": "010-3112-3533",                       # 대표 전화
    "kakao": "https://pf.kakao.com/_AGxlFX",        # 카카오톡 채널 주소(pf.kakao.com/_로 시작)
    "hours": "평일 09:00~18:00 · 카톡 상담은 24시간 접수",
    "blog": "https://blog.naver.com/lake1448",
}
KAKAO_CHAT = CONTACT["kakao"].rstrip("/") + "/chat"
TEL = "tel:" + CONTACT["phone"].replace("-", "")
ORG_LINE = " · ".join(x for x in ([f"소속 {CONTACT['company']}"] if CONTACT["company"] else []) + ([f"등록번호 {CONTACT['reg_no']}"] if CONTACT["reg_no"] else []))
ORG_ROWS = (f'<dt>소속</dt><dd>{CONTACT["company"]}</dd>' if CONTACT["company"] else "") + (f'<dt>등록번호</dt><dd>{CONTACT["reg_no"]}</dd>' if CONTACT["reg_no"] else "")
# ▲▲▲ 상담·연락처 설정 끝 ▲▲▲

# 대분류(상단 메뉴) — 파트 번호를 묶는다
GROUPS = [
    ("basic",   "보험 기초",  "보험 기초 다지기", "증권 읽는 법, 보장분석, 갱신형과 비갱신형, 계약 전 알릴의무까지 모든 보험 점검의 출발점입니다.", ["PART 1"]),
    ("death",   "사망·장해",  "사망과 장해", "사망보장의 범주와 필요 금액, 사망원인 통계, 신체 부위별 후유장해 지급률을 정리했습니다.", ["PART 2"]),
    ("disease", "암·뇌·심장", "암·뇌·심장과 수술비", "3대 질병의 통계·진단·치료와 보장 범위, 산정특례, 그리고 수술비 담보 네 종류를 비교합니다.", ["PART 3", "PART 4"]),
    ("care",    "간병·치매",  "장기요양·치매·간병", "노인장기요양보험의 등급과 비용, 치매 척도(CDR), 요양병원과 요양원, 간병보험을 묶었습니다.", ["PART 5"]),
    ("life",    "종신·연금",  "노후 준비 — 종신·연금·상속재원·변액", "종신보험의 연금전환과 사망보험금 유동화, 연금 3층과 세액공제, 상속세와 증여, 변액보험을 다룹니다.", ["PART 6"]),
    ("auto",    "자동차보험", "자동차보험·운전자보험", "자동차보험 담보와 부상등급, 12대 중과실과 형사책임, 운전자보험 변천사와 2026년 변호사 현물급부까지.", ["PART 7"]),
    ("silson",  "실손보험",   "실손의료보험 1~5세대", "세대별 보장 차이, 보상하지 않는 사항, 4세대 차등제, 5세대 전환 손익분기점 계산법을 정리했습니다.", ["PART 10"]),
    ("living",  "치아·화재",  "치아보험·화재보험", "치과 치료비 구조와 치아보험 가입 요령, 실화책임법과 주택화재보험을 설명합니다.", ["PART 8", "PART 9"]),
    ("gov",     "정부지원",   "몰라서 못 받는 정부 지원제도", "본인부담상한제, 재난적 의료비, 산정특례, 임플란트·틀니 지원과 보험금 청구 요령입니다.", ["PART 11"]),
    ("lib",     "자료실",     "실무 자료실", "질병분류코드(KCD) 읽는 법과 코드표, 보험 용어 사전, 보장분석 워크시트를 모았습니다.", ["부록"]),
]
PART2GROUP = {p: g[0] for g in GROUPS for p in g[4]}
GROUP = {g[0]: g for g in GROUPS}

QUICK = [  # 홈 '자주 찾는 주제'
    ("ch37", "5세대 실손 전환, 손해일까?", "BEP"),
    ("ch28", "운전자보험 변호사 현물급부", "2026"),
    ("ch23", "상속세 얼마나 나올까", "20억 예시"),
    ("ch20", "종신보험 연금전환·유동화", "65세+"),
    ("ch18", "치매 CDR 척도와 등급", "CDR 0~5"),
    ("ch13", "뇌혈관 진단비 보장 범위", "I60~I69"),
    ("ch12", "산정특례 본인부담 5%", "5%"),
    ("ch03", "알릴의무 3·N·5 간편심사", "3·N·5"),
    ("ch39", "본인부담상한제 환급", "3년"),
    ("appB", "질병코드 요약표", "KCD-8"),
]


def strip_tags(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s)).strip()


# ---------------------------------------------------------------- 파싱
body = "\n".join(p.read_text(encoding="utf-8") for p in sorted(SRC.glob("*.html")) if p.name[0].isdigit())
sections = re.findall(r'<section class="(chapter|divider|cover)"[^>]*>(.*?)</section>', body, re.S)

parts = []      # {num, title, lead, group, chapters:[key]}
pages = {}      # key -> {key, no, title, intro, html, part}
order = []      # 본문 페이지 순서(이전/다음)
about_html = []
cur = None
for kind, inner in sections:
    if kind == "cover":
        continue
    if kind == "divider":
        num = strip_tags(re.search(r'<div class="num">(.*?)</div>', inner, re.S).group(1))
        title_raw = re.search(r"<h1>(.*?)</h1>", inner, re.S).group(1)
        title = strip_tags(title_raw.replace("<br>", " — "))
        lead = strip_tags(re.search(r'<p class="lead">(.*?)</p>', inner, re.S).group(1))
        cur = {"num": num, "title": title, "lead": lead, "group": PART2GROUP[num], "chapters": []}
        parts.append(cur)
        continue
    no = strip_tags(re.search(r'<span class="no">(.*?)</span>', inner, re.S).group(1))
    title = strip_tags(re.search(r"<h1>(.*?)</h1>", inner, re.S).group(1))
    m_intro = re.search(r'<p class="intro">(.*?)</p>', inner, re.S)
    intro = strip_tags(m_intro.group(1)) if m_intro else ""
    content = re.sub(r'<div class="ch-head">.*?</div>', "", inner, count=1, flags=re.S)
    if no in ("PROLOGUE", "EPILOGUE"):
        about_html.append((no, title, content))
        continue
    if no.startswith("CHAPTER"):
        key = "ch" + no.split()[1]
        label = no.split()[1]
    else:  # APPENDIX A
        key = "app" + no.split()[1]
        label = no.split()[1]
    pages[key] = {"key": key, "no": no, "label": label, "title": title, "intro": intro,
                  "html": content, "part": cur}
    cur["chapters"].append(key)
    order.append(key)


def fix_content(h):
    """본문 HTML을 웹용으로 정리: 표 감싸기, 장 번호 참조를 링크로."""
    h = h.replace("<table", '<div class="tbl"><table').replace("</table>", "</table></div>")
    h = re.sub(r'style="margin-top:\d+mm"', "", h)

    def link_refs(m):
        nums = re.findall(r"\d\d", m.group(0))
        out = m.group(0)
        for n in dict.fromkeys(nums):
            if f"ch{n}" in pages:
                out = re.sub(rf"(?<![\d>]){n}(?!\d)", f'<a href="ch{n}.html">{n}</a>', out, count=1)
        return out.replace("CHAPTER ", "CHAPTER&nbsp;", 1)
    h = re.sub(r"(?<=[\s(])CHAPTER \d\d(?:\s?[·~,]\s?\d\d)*", link_refs, h)
    return h


# ---------------------------------------------------------------- 공통 조각
def gnb(active_group=None):
    items = []
    for i, (gid, label, gtitle, _desc, pnums) in enumerate(GROUPS):
        cols = []
        for p in parts:
            if p["group"] != gid:
                continue
            lis = "".join(
                f'<li><a href="{k}.html"><span class="n">{pages[k]["label"]}</span>{html.escape(pages[k]["title"])}</a></li>'
                for k in p["chapters"])
            plabel = p["num"] if p["num"] != "부록" else "APPENDIX"
            cols.append(f'<div class="part-label">{plabel}</div><a class="part-title" href="cat-{gid}.html">{html.escape(p["title"])}</a><ul>{lis}</ul>')
        cur_attr = ' aria-current="true"' if gid == active_group else ""
        right = " right" if i >= len(GROUPS) - 3 else ""
        items.append(f'<li class="top{right}"><a class="top-link" href="cat-{gid}.html"{cur_attr}>{label}</a>'
                     f'<div class="mega">{"".join(cols)}</div></li>')
    # 모바일 아코디언
    mitems = []
    for gid, label, gtitle, _d, _p in GROUPS:
        inner = [f'<a class="mall" href="cat-{gid}.html">{html.escape(gtitle)} 전체 보기</a>']
        for p in parts:
            if p["group"] != gid:
                continue
            inner.append(f'<div class="mpart">{html.escape(p["title"])}</div><ul>' + "".join(
                f'<li><a href="{k}.html">{pages[k]["label"]}. {html.escape(pages[k]["title"])}</a></li>' for k in p["chapters"]) + "</ul>")
        mitems.append(f'<details><summary>{label}</summary>{"".join(inner)}</details>')
    return f"""<a class="skip" href="#main">본문으로 건너뛰기</a>
<header class="site-head" id="top">
  <div class="wrap head-row">
    <a class="logo" href="index.html"><b>{SITE_NAME}</b><small>2026.10 개정</small></a>
    <span class="spacer"></span>
    <a class="head-link" href="profile.html">상담사 소개</a>
    <a class="head-cta" href="contact.html">상담 신청</a>
    <button class="menu-btn" id="menu-btn" type="button" aria-expanded="false" aria-controls="mnav">메뉴</button>
  </div>
  <nav class="gnb" aria-label="분야 메뉴"><div class="wrap"><ul>{"".join(items)}</ul></div></nav>
  <nav class="mnav" id="mnav" aria-label="모바일 메뉴"><div class="wrap"><div class="search msearch" role="search"><label for="mq" class="skip">주제 검색</label><input id="mq" type="search" data-search placeholder="주제 검색 (예: 상속세, 치매)" autocomplete="off"><div class="results" hidden></div></div>{"".join(mitems)}<div class="mcontact"><a class="btn btn-primary" href="contact.html">상담 신청하기</a><a class="btn btn-kakao" href="{KAKAO_CHAT}" target="_blank" rel="noopener">카카오톡 상담</a></div><a class="mall" href="profile.html">상담사 소개 — 보험친구 박혜경</a><a class="mall" href="about.html">이 사이트에 대해</a></div></nav>
</header>"""


FOOT = f"""<footer class="site-foot"><div class="wrap">
  <figure class="qr foot-qr"><img src="assets/qr-kakao.png" alt="카카오톡 상담 QR코드" width="88" height="88" loading="lazy"><figcaption>카톡 상담 QR</figcaption></figure>
  <div class="foot-contact"><b>{CONTACT["name"]}</b> · {CONTACT["role"]}{"<br>" + ORG_LINE if ORG_LINE else ""}<br>전화 <span class="sel">{CONTACT["phone"]}</span> · {CONTACT["hours"]} · <a href="contact.html">상담 신청</a> · <a href="{KAKAO_CHAT}" target="_blank" rel="noopener">카카오톡 채널</a></div>
  <div><b>보험 보장 가이드</b> · 『한 권으로 끝내는 보험 보장 가이드』(2026년 10월 개정판) 웹판</div>
  <div>이 사이트는 보험에 대한 일반적인 정보를 제공하며 특정 상품의 가입·해지·전환을 권유하지 않습니다. 통계·제도·금액은 2026년 10월 기준 공개 자료를 바탕으로 하며 이후 바뀔 수 있습니다. 개별 계약의 보장은 해당 약관과 보험증권, 보험회사의 심사에 따릅니다. 보험계약 체결 전 상품설명서와 약관을 반드시 읽어 보시기 바랍니다.</div>
</div></footer>"""


TABBAR = f"""<nav class="tabbar" aria-label="빠른 이동">
  <a href="index.html"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 11l9-7 9 7v9a1 1 0 0 1-1 1h-5v-6h-6v6H4a1 1 0 0 1-1-1z"/></svg>홈</a>
  <button type="button" data-open="menu"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 6h16M4 12h16M4 18h16"/></svg>분야</button>
  <button type="button" data-open="search"><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/></svg>검색</button>
  <a href="contact.html" class="tab-cta"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 5h16v11H8l-4 4z"/><path d="M8 9h8M8 12h5"/></svg>상담 신청</a>
</nav>
<a class="kakao-fab" href="{KAKAO_CHAT}" target="_blank" rel="noopener" aria-label="카카오톡으로 상담하기"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 4C7 4 3 7.1 3 11c0 2.5 1.7 4.7 4.2 5.9l-.9 3.3c-.1.3.3.6.6.4l3.9-2.6c.4 0 .8.1 1.2.1 5 0 9-3.1 9-7S17 4 12 4z"/></svg><span>카톡 상담</span></a>"""


SITE_URL = "https://theorm303-droid.github.io/insurance-guide/"
OG_DESC = "어려운 보험을 쉽게, 내 보험 점검부터. 실손·건강·간병·노후 준비·보험금 청구까지 보험친구 박혜경이 쉽게 풀어 드립니다."


def og_tags(title, desc):
    """카톡·문자·SNS 링크 미리보기(썸네일) 정보."""
    d = html.escape(desc or OG_DESC)
    t = html.escape(title if title != SITE_NAME else "보험이 쉬워지는 시간 · 보험친구 박혜경")
    img = SITE_URL + "assets/og-image.jpg"
    return (f'<meta property="og:type" content="website">\n'
            f'<meta property="og:site_name" content="보험이 쉬워지는 시간">\n'
            f'<meta property="og:title" content="{t}">\n'
            f'<meta property="og:description" content="{d}">\n'
            f'<meta property="og:image" content="{img}">\n'
            f'<meta property="og:image:width" content="1200">\n<meta property="og:image:height" content="630">\n'
            f'<meta property="og:url" content="{SITE_URL}">\n'
            f'<meta name="twitter:card" content="summary_large_image">\n'
            f'<meta name="twitter:image" content="{img}">\n'
            f'<link rel="icon" href="assets/profile-face.jpg">')


def page(title, inner, active_group=None, desc="", doctype=True):
    head = (f'<title>{html.escape(title)}</title>\n'
            f'<meta name="claude:viewport-fit-sides" content="cover">\n'
            f'<meta name="description" content="{html.escape(desc)}">\n'
            f'{og_tags(title, desc)}\n{FONTS}\n'
            '<link rel="stylesheet" href="assets/site.css">')
    content = f"{gnb(active_group)}\n<main id=\"main\">{inner}</main>\n{FOOT}\n{TABBAR}\n<script src=\"assets/site.js\"></script>"
    if not doctype:
        return f"{head}\n{content}\n"
    return (f'<!doctype html>\n<html lang="ko"><head><meta charset="utf-8">\n'
            f'<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            f'{head}\n</head><body>\n{content}\n</body></html>\n')


CTA = f"""<aside class="cta" aria-label="상담 안내">
  <a class="cta-face" href="profile.html"><img src="assets/profile-face.jpg" alt="보험친구 박혜경 사진" width="64" height="64" loading="lazy"></a>
  <div><b>이 내용, 내 보험에 적용해 보고 싶다면</b><p>보험증권 사진 한 장만 보내 주세요. 부족한 보장과 겹치는 보장을 함께 살펴봐 드릴게요. 가입보다 점검이 먼저입니다. <a href="profile.html">— 보험친구 박혜경</a></p></div>
  <div class="cta-btns"><a class="btn btn-kakao" href="{KAKAO_CHAT}" target="_blank" rel="noopener">카카오톡 상담</a><a class="btn btn-primary" href="contact.html">상담 신청</a></div>
</aside>"""


def crumb(*items):
    out = ['<a href="index.html">홈</a>']
    for label, href in items:
        out.append('<span class="sep">/</span>')
        out.append(f'<a href="{href}">{html.escape(label)}</a>' if href else f'<span>{html.escape(label)}</span>')
    return f'<nav class="crumb" aria-label="현재 위치">{"".join(out)}</nav>'


# ---------------------------------------------------------------- 본문 페이지
for idx, key in enumerate(order):
    pg = pages[key]
    part = pg["part"]
    gid = part["group"]
    g = GROUP[gid]
    side = [f'<a class="g" href="cat-{gid}.html">{html.escape(g[2])}</a>']
    for p in parts:
        if p["group"] != gid:
            continue
        side.append(f'<div class="p">{html.escape(p["num"] if p["num"] != "부록" else "APPENDIX")} · {html.escape(p["title"])}</div><ul>')
        for k in p["chapters"]:
            cur_attr = ' aria-current="page"' if k == key else ""
            side.append(f'<li><a href="{k}.html"{cur_attr}>{pages[k]["label"]}. {html.escape(pages[k]["title"])}</a></li>')
        side.append("</ul>")
    prev_k = order[idx - 1] if idx > 0 else None
    next_k = order[idx + 1] if idx + 1 < len(order) else None
    pager = '<nav class="pager" aria-label="이전·다음 장">'
    if prev_k:
        pager += f'<a class="prev" href="{prev_k}.html"><small>← 이전 {pages[prev_k]["no"]}</small>{html.escape(pages[prev_k]["title"])}</a>'
    if next_k:
        pager += f'<a class="next" href="{next_k}.html"><small>다음 {pages[next_k]["no"]} →</small>{html.escape(pages[next_k]["title"])}</a>'
    pager += "</nav>"
    eyebrow = f'{pg["no"]} · {part["num"]} {part["title"]}' if part["num"] != "부록" else f'자료실 · 부록 {pg["label"]}'
    inner = f"""<div class="wrap">{crumb((g[1], f"cat-{gid}.html"), (pg["title"], None))}
<div class="doc">
  <aside class="side" aria-label="이 분야의 다른 장">{"".join(side)}</aside>
  <article class="content">
    <details class="m-side"><summary>{html.escape(g[1])} · 이 분야 다른 장 보기</summary>{"".join(side[1:])}</details>
    <header class="ch-head"><div class="eyebrow">{html.escape(eyebrow)}</div><h1>{html.escape(pg["title"])}</h1>{f'<p class="intro">{html.escape(pg["intro"])}</p>' if pg["intro"] else ""}</header>
    {fix_content(pg["html"])}
    {CTA}
    {pager}
  </article>
</div></div>"""
    (OUT / f"{key}.html").write_text(page(f'{pg["title"]} | {SITE_NAME}', inner, gid, pg["intro"]), encoding="utf-8")

# ---------------------------------------------------------------- 분류 페이지
for gid, label, gtitle, gdesc, _p in GROUPS:
    blocks = []
    for p in parts:
        if p["group"] != gid:
            continue
        lis = "".join(
            f'<li><a href="{k}.html"><span class="n">{pages[k]["label"]}</span><b>{html.escape(pages[k]["title"])}</b>'
            f'<span class="i">{html.escape(pages[k]["intro"])}</span></a></li>' for k in p["chapters"])
        plabel = p["num"] if p["num"] != "부록" else "APPENDIX"
        blocks.append(f'<section class="part-block"><div class="eyebrow">{plabel}</div><h2>{html.escape(p["title"])}</h2>'
                      f'<p>{html.escape(p["lead"])}</p><ul class="ch-list">{lis}</ul></section>')
    n = sum(len(p["chapters"]) for p in parts if p["group"] == gid)
    inner = f"""<div class="cat-hero"><div class="wrap">{crumb((label, None))}
<div class="eyebrow">{label} · {n}개 주제</div><h1>{html.escape(gtitle)}</h1><p>{html.escape(gdesc)}</p></div></div>
<div class="wrap">{"".join(blocks)}<div style="height:48px"></div></div>"""
    (OUT / f"cat-{gid}.html").write_text(page(f"{label} | {SITE_NAME}", inner, gid, gdesc), encoding="utf-8")

# ---------------------------------------------------------------- 소개 페이지
about_inner = ""
for no, title, content in about_html:
    about_inner += f'<header class="ch-head"><div class="eyebrow">{no}</div><h1>{html.escape(title)}</h1></header>{fix_content(content)}'
about_inner = about_inner.replace("이 책", "이 가이드")
inner = f"""<div class="wrap">{crumb(("이 사이트에 대해", None))}
<div class="doc"><aside class="side"><a class="g" href="index.html">{SITE_NAME}</a></aside>
<article class="content">{about_inner}</article></div></div>"""
(OUT / "about.html").write_text(page(f"이 사이트에 대해 | {SITE_NAME}", inner, None, "가이드의 구성과 이용 방법, 면책 고지"), encoding="utf-8")


# ---------------------------------------------------------------- 상담 신청 페이지
topics = "".join(f'<label class="chk"><input type="checkbox" name="topic" value="{g[1]}"> {g[1]}</label>' for g in GROUPS if g[0] != "lib")
contact_inner = f"""<div class="wrap">{crumb(("상담 신청", None))}
<div class="contact-grid">
  <section class="contact-card" aria-label="상담사 정보">
    <div class="contact-face"><img src="assets/profile-face.jpg" alt="보험친구 박혜경 사진" width="96" height="96"><div><div class="eyebrow">CONTACT</div><h1>보험 상담 신청</h1></div></div>
    <p class="lead2">안녕하세요, 보험이 쉬워지는 시간 보험친구 박혜경입니다. 보장분석, 실손 전환, 부모님 간병·치매 보험까지 궁금한 점을 편하게 남겨 주세요. 확인 후 직접 연락드립니다.</p>
    <dl class="who">
      <dt>상담사</dt><dd><b>{CONTACT["name"]}</b> · {CONTACT["role"]}</dd>
      {ORG_ROWS}
      <dt>상담 시간</dt><dd>{CONTACT["hours"]}</dd>
    </dl>
    <div class="reach">
      <div class="reach-row"><span class="k">전화</span><span class="v sel">{CONTACT["phone"]}</span>
        <button type="button" class="btn btn-ghost" data-copy="{CONTACT["phone"]}">번호 복사</button>
        <a class="btn btn-ghost" href="{TEL}">전화 걸기</a></div>
      <a class="btn btn-kakao wide" href="{KAKAO_CHAT}" target="_blank" rel="noopener">카카오톡 채널로 바로 상담하기</a>
      <div class="qr-row"><figure class="qr"><img src="assets/qr-kakao.png" alt="카카오톡 상담 QR코드" width="120" height="120"><figcaption>휴대폰 카메라로 찍으면<br>카톡 상담창이 열려요</figcaption></figure><figure class="qr"><img src="assets/qr-blog.png" alt="블로그 QR코드" width="120" height="120"><figcaption>블로그<br>보험이 쉬워지는 시간</figcaption></figure></div>
      <p class="small">카카오톡 채널을 추가하면 상담 내역이 대화방에 남아 편리합니다.</p>
    </div>
  </section>

  <section class="form-card" aria-label="상담 신청서">
    <h2>상담 신청서</h2>
    <form id="consult" novalidate>
      <div class="field"><label for="f-name">이름 <em>*</em></label><input id="f-name" name="name" type="text" required autocomplete="name" placeholder="홍길동"></div>
      <div class="field"><label for="f-phone">연락처 <em>*</em></label><input id="f-phone" name="phone" type="tel" required inputmode="tel" autocomplete="tel" placeholder="010-1234-5678"></div>
      <div class="field"><label for="f-age">나이대</label>
        <select id="f-age" name="age"><option value="">선택 안 함</option><option>20대</option><option>30대</option><option>40대</option><option>50대</option><option>60대 이상</option></select></div>
      <fieldset class="field"><legend>관심 분야 (여러 개 선택 가능)</legend><div class="chks">{topics}</div></fieldset>
      <div class="field"><label for="f-time">연락 받기 편한 시간</label>
        <select id="f-time" name="time"><option value="">상관없음</option><option>오전(9~12시)</option><option>오후(12~18시)</option><option>저녁(18시 이후)</option></select></div>
      <div class="field"><label for="f-msg">문의 내용</label><textarea id="f-msg" name="msg" rows="4" placeholder="예: 1세대 실손을 유지할지 5세대로 바꿀지 고민입니다."></textarea></div>
      <label class="chk agree"><input id="f-agree" type="checkbox" required> <span>[필수] 상담을 위한 개인정보(이름·연락처·문의 내용) 수집·이용에 동의합니다. 수집한 정보는 상담 목적으로만 사용하며 상담 완료 후 1년 이내 파기합니다.</span></label>
      <p class="form-error" id="f-error" role="alert" hidden></p>
      <button class="btn btn-primary wide" type="submit">신청 내용 만들기</button>
    </form>
    <div class="done" id="done" hidden>
      <h3>신청 내용이 준비됐습니다</h3>
      <p>아래 버튼을 누르면 내용이 복사되고 카카오톡 상담창이 열립니다. 대화창에 <b>붙여넣기</b>해서 보내 주세요.</p>
      <textarea id="done-text" rows="8" readonly aria-label="신청 내용"></textarea>
      <a class="btn btn-kakao wide" id="send-kakao" href="{KAKAO_CHAT}" target="_blank" rel="noopener">복사하고 카카오톡으로 보내기</a>
      <button type="button" class="btn btn-ghost wide" data-copy-from="done-text">내용만 복사</button>
      <p class="small" id="copy-msg" role="status"></p>
    </div>
    <p class="small">입력한 정보는 이 화면에서만 쓰이고 사이트에 저장되지 않습니다. 카카오톡으로 보낼 때만 상담사에게 전달됩니다.</p>
  </section>
</div></div>"""
(OUT / "contact.html").write_text(page(f"상담 신청 | {SITE_NAME}", contact_inner, None, "보험 보장분석·실손 전환·종신·자동차보험 무료 상담 신청"), encoding="utf-8")

# ---------------------------------------------------------------- 상담사 소개
HOME_PROFILE = f"""<div class="pf-band">
  <a class="pf-photo" href="profile.html"><picture><source media="(max-width: 760px)" srcset="assets/profile-face.jpg"><img src="assets/profile-portrait.jpg" alt="보험친구 박혜경 사진" width="330" height="341" loading="lazy"></picture></a>
  <div class="pf-body">
    <div class="eyebrow">상담사 소개</div>
    <h2>안녕하세요, <span class="nb">보험이 쉬워지는 시간</span><br><span class="nb">보험친구 <span>박혜경</span>입니다</span></h2>
    <p class="pf-story">공방에서 아로마테라피·천연비누 강사로<br>10년 넘게 사람들을 만나 왔고,<br>지금은 <b>뉴니케GA</b>에서<br>보험설계사로 새 출발했습니다.</p>
    <p class="pf-hello">보험이 어렵게 느껴지셨다면<br>여기서 하나씩 쉽게 풀어 드릴게요.<br><b>내 보험 점검·실손·간병</b>, 편하게 물어보세요.</p>
    <ul class="pf-tags"><li><a href="ch01.html">내 보험 점검</a></li><li><a href="cat-silson.html">실손보험</a></li><li><a href="cat-disease.html">암·뇌·심장</a></li><li><a href="cat-care.html">부모님 간병·치매</a></li><li><a href="profile.html">요양보호사 자격 취득</a></li></ul>
    <div class="pf-btns"><a class="btn btn-kakao" href="{KAKAO_CHAT}" target="_blank" rel="noopener">카카오톡 상담</a><a class="btn btn-ghost" href="profile.html">소개 더 보기</a></div>
  </div>
</div>"""

profile_inner = f"""<div class="pf-hero"><div class="wrap">
  {crumb(("상담사 소개", None))}
  <div class="pf-hero-grid">
    <div class="pf-card">
      <img src="assets/profile-portrait.jpg" alt="보험친구 박혜경 사진" width="330" height="341">
      <div class="pf-name"><small>보험이 쉬워지는 시간</small><b>박혜경</b><span>{CONTACT["company"]} 보험설계사</span><span>설계사 등록번호 {CONTACT["reg_no"]}</span></div>
    </div>
    <div class="pf-intro">
      <div class="eyebrow">보험친구 박혜경</div>
      <h1>어려운 보험은 쉽게,<br>필요한 보장은 제대로</h1>
      <p>보험은 단순한 금융상품이 아니라, 살다가 힘든 순간에 곁을 지켜 주는 준비라고 생각합니다. 보험을 잘 아는 사람을 위한 상담이 아니라, 보험을 잘 모르는 고객님이 이해할 수 있는 상담을 하고 싶습니다.</p>
      <div class="pf-btns"><a class="btn btn-kakao" href="{KAKAO_CHAT}" target="_blank" rel="noopener">카카오톡으로 편하게 묻기</a><a class="btn btn-primary" href="contact.html">상담 신청</a></div>
    </div>
  </div>
</div></div>

<div class="wrap pf-main">
  <section class="pf-sec">
    <h2>공방 선생님에서 보험친구로</h2>
    <p>대구에서 천연비누·천연화장품 공방 '엔비솝'을 운영하며 아로마테라피스트로 10년 넘게 일했습니다. 초등학교 방학 특강, 대학 진로체험, 여성인력개발센터 16주 과정까지, 처음 해 보는 분들 눈높이에 맞춰 차근차근 설명하는 일을 오래 해 왔습니다.</p>
    <p>지금은 {CONTACT["company"]}에서 보험설계사로 새 출발했습니다. 공방에서 하던 것처럼, 처음 듣는 용어도 하나씩 풀어서 "아, 그런 거였구나" 하실 때까지 설명해 드리는 것이 제 방식입니다.</p>
    <div class="pf-timeline">
      <div><b>공방 시절</b><span>아로마테라피스트 · 천연비누·화장품 강사 · 외부 출강</span></div>
      <div><b>2026년</b><span>뉴니케GA 보험설계사로 새 출발 · 블로그 '보험이 쉬워지는 시간' 시작</span></div>
      <div><b>2026년 여름</b><span>요양보호사 자격 취득</span></div>
    </div>
  </section>

  <section class="pf-sec">
    <h2>제가 상담할 때 지키는 세 가지</h2>
    <div class="pf-promise">
      <div><b>고객의 언어로</b><p>주계약, 특약, 면책기간, 감액기간… 어려운 말은 쉬운 말로 바꿔서 설명합니다.</p></div>
      <div><b>'많이'보다 '제대로'</b><p>보험료를 많이 낸다고 좋은 보험이 아닙니다. 지금 소득과 가족 상황에 맞는지부터 봅니다.</p></div>
      <div><b>가입보다 점검이 먼저</b><p>기존 보험에 좋은 보장이 있다면 바꿀 이유가 없습니다. 지금 가진 보험부터 함께 살펴봅니다.</p></div>
    </div>
  </section>

  <section class="pf-sec">
    <h2>요양보호사 자격을 가진 설계사</h2>
    <p>올여름 두 달 동안 요양보호사 자격증을 땄습니다. 공부하는 동안 부모님께 안부 전화를 더 자주 드리게 됐고, 장기요양 등급을 받은 뒤 가족이 실제로 무엇을 고민하는지 더 깊이 이해하게 되었습니다.</p>
    <p>그래서 부모님 간병·치매 보험과 장기요양 제도는 특히 자신 있게 설명해 드릴 수 있습니다. 관련 내용은 <a href="cat-care.html">간병·치매 분야</a>에도 정리해 두었습니다.</p>
  </section>

  <section class="pf-sec">
    <h2>이런 분들과 이야기 나누고 싶어요</h2>
    <ul class="check">
      <li>보험료는 매달 나가는데 무슨 보험에 가입돼 있는지 잘 모르는 분</li>
      <li>암보험은 있는데 진단받으면 얼마를 받는지 모르는 분</li>
      <li>내 실손보험이 몇 세대인지, 5세대로 바꿔야 할지 고민인 분</li>
      <li>부모님 간병과 장기요양을 미리 준비하고 싶은 분</li>
      <li>보험이 여러 개인데 겹치거나 부족한 건 없는지 궁금한 분</li>
    </ul>
  </section>

  <section class="pf-sec pf-how">
    <h2>상담은 이렇게 진행돼요</h2>
    <div class="flow">
      <div class="step"><b>1. 카톡으로 인사</b>궁금한 점을 편하게 남겨 주세요</div><div class="arrow">›</div>
      <div class="step"><b>2. 증권 사진 한 장</b>주민번호·계좌번호는 가리고 보내 주세요</div><div class="arrow">›</div>
      <div class="step"><b>3. 함께 살펴보기</b>겹치는 보장, 부족한 보장을 쉽게 설명해 드려요</div><div class="arrow">›</div>
      <div class="step"><b>4. 판단은 고객님이</b>유지할지 바꿀지 충분히 이해한 뒤 결정하세요</div>
    </div>
  </section>

  <section class="pf-sec">
    <h2>블로그 '보험이 쉬워지는 시간'</h2>
    <p>실손보험 세대 구분, 암·뇌·심장 진단비 확인법, 부모님 장기요양 등급 이야기 등을 블로그에 꾸준히 올리고 있습니다.</p>
    <ul class="pf-posts">
      <li><a href="https://blog.naver.com/lake1448/224388269935" target="_blank" rel="noopener">보험이 쉬워지는 시간, 박혜경입니다</a></li>
      <li><a href="https://blog.naver.com/lake1448/224389824725" target="_blank" rel="noopener">내 보험, 제대로 가입되어 있을까? 보험점검이 필요한 3가지 이유</a></li>
      <li><a href="https://blog.naver.com/lake1448/224392179458" target="_blank" rel="noopener">실손보험, 나는 몇 세대일까? 가입 시기부터 확인하세요</a></li>
      <li><a href="https://blog.naver.com/lake1448/224392853575" target="_blank" rel="noopener">암·뇌·심장 보험, 가입했다면 끝일까요?</a></li>
      <li><a href="https://blog.naver.com/lake1448/224404833556" target="_blank" rel="noopener">부모님 장기요양등급, 몇 등급부터 도움을 받을 수 있을까요?</a></li>
    </ul>
    <div class="qr-row"><figure class="qr"><img src="assets/qr-kakao.png" alt="카카오톡 상담 QR코드" width="120" height="120"><figcaption>휴대폰 카메라로 찍으면<br>카톡 상담창이 열려요</figcaption></figure><figure class="qr"><img src="assets/qr-blog.png" alt="블로그 QR코드" width="120" height="120"><figcaption>블로그<br>보험이 쉬워지는 시간</figcaption></figure></div>
    <a class="btn btn-ghost" href="{CONTACT["blog"]}" target="_blank" rel="noopener">블로그 전체 보기</a>
  </section>

  {CTA}
</div>"""
(OUT / "profile.html").write_text(page(f"상담사 소개 | {SITE_NAME}", profile_inner, None, "보험친구 박혜경 — 뉴니케GA 보험설계사, 어려운 보험을 쉽게 풀어드립니다"), encoding="utf-8")

# ---------------------------------------------------------------- 홈
cards = []
for gid, label, gtitle, gdesc, _p in GROUPS:
    keys = [k for p in parts if p["group"] == gid for k in p["chapters"]]
    shown = keys[:5]
    lis = "".join(f'<li><a href="{k}.html"><span class="n">{pages[k]["label"]}</span>{html.escape(pages[k]["title"])}</a></li>' for k in shown)
    more = f'<a class="more" href="cat-{gid}.html">{label} 전체 {len(keys)}개 주제 보기 →</a>'
    cards.append(f'<div class="cat"><span class="count">{len(keys)} TOPICS</span><h3><a href="cat-{gid}.html">{label}</a></h3>'
                 f'<p class="desc">{html.escape(gdesc)}</p><ul>{lis}</ul>{more}</div>')
chips = "".join(f'<a href="{k}.html">{html.escape(t)} <code>{html.escape(c)}</code></a>' for k, t, c in QUICK)
home_inner = f"""<section class="hero2">
  <div class="wrap hero2-in">
    <p class="h2-top">어려운 보험을 쉽게, 내 보험 점검부터</p>
    <div class="h2-leaf" aria-hidden="true"><span></span><svg viewBox="0 0 40 20"><path d="M20 18C14 18 6 14 4 4c8 0 14 4 16 14zM20 18c6 0 14-4 16-14-8 0-14 4-16 14z"/></svg><span></span></div>
    <h1>보험이 쉬워지는 시간</h1>
    <p class="h2-name">보험친구 박혜경</p>
    <nav class="h2-pills" aria-label="주요 분야">
      <a href="cat-silson.html">실손</a><a href="cat-disease.html">건강</a><a href="cat-care.html">간병</a><a href="cat-life.html">노후 준비</a><a href="ch41.html">보험금 청구</a>
    </nav>
    <div class="search" role="search">
      <label for="q" class="skip">주제 검색</label>
      <input id="q" type="search" data-search placeholder="궁금한 보험 검색 (예: 실손, 치매)" autocomplete="off">
      <div class="results" hidden></div>
    </div>
  </div>
  <div class="h2-scene" role="img" aria-label="나무 집 모형과 책, 찻잔이 놓인 창가"></div>
</section>
<section class="section pf-home"><div class="wrap">{HOME_PROFILE}</div></section>
<section class="section" style="padding-top:0"><div class="wrap">
  <div class="section-head"><h2>분야별 안내</h2><p>상단 메뉴와 같은 10개 분야입니다.</p></div>
  <div class="cats">{"".join(cards)}</div>
</div></section>
<section class="section" style="padding-top:0"><div class="wrap">
  <div class="section-head"><h2>자주 찾는 주제</h2></div>
  <div class="chips">{chips}</div>
</div></section>
<section class="section" style="padding-top:0"><div class="wrap">
  <div class="section-head"><h2>이렇게 활용하세요</h2></div>
  <div class="howto">
    <div><b>보험증권 모으기</b><p>'내보험다보여'에서 가족 전체 가입 내역을 조회합니다.</p></div>
    <div><b>분야별 점검</b><p>메뉴에서 관심 분야를 골라 각 장 끝의 체크리스트를 확인합니다.</p></div>
    <div><b>워크시트 정리</b><p><a href="appD.html">보장분석 워크시트</a>에 위험별 보장 금액을 채웁니다.</p></div>
    <div><b>1년마다 다시</b><p>갱신·만기·가족 변화가 있을 때마다 다시 점검합니다.</p></div>
  </div>
</div></section>"""
(OUT / "index.html").write_text(page(SITE_NAME, home_inner, None, OG_DESC), encoding="utf-8")
(OUT / "_artifact_home.html").write_text(page(SITE_NAME, home_inner, None, "", doctype=False), encoding="utf-8")

# ---------------------------------------------------------------- 스크립트(검색 색인 포함)
index = []
for key in order:
    pg = pages[key]
    heads = [strip_tags(h) for h in re.findall(r"<h2[^>]*>(.*?)</h2>", pg["html"], re.S)]
    index.append({"k": key, "t": pg["title"], "n": pg["no"], "g": GROUP[pg["part"]["group"]][1],
                  "s": " ".join([pg["intro"]] + heads)})
js = """(function () {
  var head = document.querySelector('.site-head');
  var btn = document.getElementById('menu-btn');
  function setMenu(open) {
    if (!head) return;
    head.classList.toggle('open', open);
    document.body.classList.toggle('menu-open', open);
    if (btn) { btn.setAttribute('aria-expanded', open ? 'true' : 'false'); btn.textContent = open ? '닫기' : '메뉴'; }
  }
  if (btn) btn.addEventListener('click', function () { setMenu(!head.classList.contains('open')); });

  // 하단 탭바
  document.querySelectorAll('.tabbar [data-open]').forEach(function (b) {
    b.addEventListener('click', function () {
      var mode = b.getAttribute('data-open');
      var isOpen = head.classList.contains('open');
      if (mode === 'menu') { setMenu(!isOpen); window.scrollTo(0, window.scrollY); return; }
      var home = document.getElementById('q');
      if (home && home.getBoundingClientRect) { setMenu(false); home.scrollIntoView({ block: 'center' }); home.focus(); return; }
      setMenu(true);
      var mq = document.getElementById('mq'); if (mq) mq.focus();
    });
  });
  var top = document.querySelector('.tabbar [data-top]');
  if (top) top.addEventListener('click', function (e) { e.preventDefault(); setMenu(false); window.scrollTo({ top: 0, behavior: 'smooth' }); });

  // 메뉴 안의 링크를 누르면 메뉴 닫기
  document.querySelectorAll('.mnav a').forEach(function (a) { a.addEventListener('click', function () { setMenu(false); }); });

  // 넓은 표: 옆으로 밀어 보기 안내
  function markTables() {
    document.querySelectorAll('.tbl').forEach(function (w) {
      var over = w.scrollWidth > w.clientWidth + 4;
      var prev = w.previousElementSibling;
      var has = prev && prev.classList && prev.classList.contains('swipe');
      if (over && !has) { var d = document.createElement('div'); d.className = 'swipe'; d.textContent = '표를 옆으로 밀어서 보세요 →'; w.parentNode.insertBefore(d, w); }
      if (!over && has) { prev.remove(); }
    });
  }
  markTables();
  window.addEventListener('resize', markTables);

  // 복사 버튼
  function copyText(text, done) {
    function fallback() {
      var ta = document.createElement('textarea'); ta.value = text; document.body.appendChild(ta); ta.select();
      var ok = false; try { ok = document.execCommand('copy'); } catch (e) {} ta.remove(); done(ok);
    }
    try { navigator.clipboard.writeText(text).then(function () { done(true); }, fallback); } catch (e) { fallback(); }
  }
  document.querySelectorAll('[data-copy]').forEach(function (b) {
    b.addEventListener('click', function () {
      copyText(b.getAttribute('data-copy'), function (ok) { var o = b.textContent; b.textContent = ok ? '복사됨' : '길게 눌러 복사'; setTimeout(function () { b.textContent = o; }, 1600); });
    });
  });
  function copyMsg(ok, el) {
    var m = document.getElementById('copy-msg');
    if (m) m.textContent = ok ? '복사했습니다. 카카오톡 대화창에 붙여넣어 보내 주세요.' : '복사가 안 되면 위 내용을 길게 눌러 직접 복사해 주세요.';
    if (!ok && el) { el.focus(); el.select(); }
  }
  document.querySelectorAll('[data-copy-from]').forEach(function (b) {
    b.addEventListener('click', function () {
      var el = document.getElementById(b.getAttribute('data-copy-from'));
      copyText(el.value, function (ok) { copyMsg(ok, el); });
    });
  });

  // 상담 신청서
  var form = document.getElementById('consult');
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var err = document.getElementById('f-error');
      var name = form.elements.name.value.trim(), phone = form.elements.phone.value.trim();
      var msg = '';
      if (!name) msg = '이름을 입력해 주세요.';
      else if (phone.replace(/[^0-9]/g, '').length < 9) msg = '연락처를 숫자로 입력해 주세요. 예: 010-1234-5678';
      else if (!document.getElementById('f-agree').checked) msg = '개인정보 수집·이용에 동의해 주세요.';
      if (msg) { err.textContent = msg; err.hidden = false; return; }
      err.hidden = true;
      var topics = Array.prototype.map.call(form.querySelectorAll('input[name=topic]:checked'), function (c) { return c.value; });
      var lines = ['[보험 상담 신청]', '이름: ' + name, '연락처: ' + phone];
      if (form.elements.age.value) lines.push('나이대: ' + form.elements.age.value);
      if (topics.length) lines.push('관심 분야: ' + topics.join(', '));
      lines.push('연락 시간: ' + (form.elements.time.value || '상관없음'));
      if (form.elements.msg.value.trim()) lines.push('문의 내용: ' + form.elements.msg.value.trim());
      document.getElementById('done-text').value = lines.join(String.fromCharCode(10));
      document.getElementById('done').hidden = false;
      form.hidden = true;
      document.getElementById('done').scrollIntoView({ block: 'start' });
    });
    var send = document.getElementById('send-kakao');
    if (send) send.addEventListener('click', function () {
      var el = document.getElementById('done-text');
      copyText(el.value, function (ok) { copyMsg(ok, el); });
    });
  }

  // 검색(홈·메뉴 공용)
  var IDX = __INDEX__;
  function norm(s) { return (s || '').toLowerCase().replace(/\\s+/g, ''); }
  document.querySelectorAll('[data-search]').forEach(function (q) {
    var box = q.parentNode.querySelector('.results');
    if (!box) return;
    function render() {
      var v = norm(q.value);
      if (!v) { box.hidden = true; box.innerHTML = ''; return; }
      var hits = IDX.map(function (it) {
        var score = 0;
        if (norm(it.t).indexOf(v) >= 0) score += 3;
        if (norm(it.g).indexOf(v) >= 0) score += 2;
        if (norm(it.s).indexOf(v) >= 0) score += 1;
        return { it: it, score: score };
      }).filter(function (h) { return h.score > 0; })
        .sort(function (a, b) { return b.score - a.score; }).slice(0, 8);
      box.innerHTML = hits.length ? hits.map(function (h) {
        return '<a href="' + h.it.k + '.html">' + h.it.t + '<small>' + h.it.g + ' · ' + h.it.n + '</small></a>';
      }).join('') : '<div class="none">찾는 주제가 없습니다. 다른 단어로 검색해 보세요.</div>';
      box.hidden = false;
    }
    q.addEventListener('input', render);
    q.addEventListener('keydown', function (e) {
      if (e.key === 'Enter') { var a = box.querySelector('a'); if (a) { window.location.href = a.getAttribute('href'); } }
      if (e.key === 'Escape') { q.value = ''; render(); }
    });
    document.addEventListener('click', function (e) { if (!box.contains(e.target) && e.target !== q) { box.hidden = true; } });
  });
})();
"""
(OUT / "assets" / "site.js").write_text(js.replace("__INDEX__", json.dumps(index, ensure_ascii=False)), encoding="utf-8")

print("pages:", len(order), "chapters/appendix +", len(GROUPS), "categories + index/about")
