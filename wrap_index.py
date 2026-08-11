# -*- coding: utf-8 -*-
# Builds a proper standalone HTML document (index.html) from the Artifact-format
# source (kcda-website.html), which intentionally has no <!DOCTYPE>/<html>/<head>/
# <body> wrapper (the Claude Artifact platform injects that itself). Vercel serves
# index.html directly with no such wrapper, so it needs its own real <head> with
# SEO/meta tags. Also embeds the real paper PDFs (real downloads only work on
# the standalone site - the Claude Artifact sandbox blocks them, so those copies
# stay on the mock download message by simply never getting a data-pdf attribute).
# Re-run this after every `cp kcda-website.html index.html` sync.

import base64
import re

with open('kcda-website.html', 'r', encoding='utf-8') as f:
    source = f.read()

title_start = source.find('<title>')
title_end = source.find('</title>') + len('</title>')
assert title_start == 0, "expected <title> to be the very first thing in the source"
title_tag = source[title_start:title_end]
title_text = source[title_start + len('<title>'):title_end - len('</title>')]
rest = source[title_end:]

# inject real PDF data URIs onto each paper's primary trigger element (the
# one with data-authors, which is unique to .paper-card-thumb-btn - the
# sibling .dl-btn shares data-title/data-meta but has no data-authors, so
# this pattern can't accidentally double-embed onto it)
PDF_FILES = {
    '협업역량이 공동 목표 달성에 미치는 영향: 다양한 구성원 간 역할 조율을 중심으로': '협업 능력.pdf',
    '기업 핵심인재 역량으로서 자기주도성과 실행력의 개념적 통합과 개발 방안': '자기주도성과_실행력_KCI.pdf',
    '기업 핵심인재 역량으로서 변화 적응력과 성장 가능성의 개념적 통합과 인적자원관리 방안': '변화_적응력과_성장_가능성_KCI.pdf',
    '직무 전문성의 구성요인과 개발 메커니즘에 관한 문헌고찰': '직무_전문성_KCI.pdf',
    '기업 핵심인재 역량으로서 문제 해결력의 개념적 구조와 인적자원관리 적용방안': '문제_해결력_KCI.pdf',
    '기업 핵심인재 역량으로서 의사소통 능력의 개념적 통합과 개발방안': '의사소통_능력_KCI.pdf',
}

pdf_pattern = re.compile(r'(data-title="([^"]+)" data-meta="[^"]+" data-authors="[^"]+" data-img1=")')

def inject_pdf(m):
    title = m.group(2)
    filename = PDF_FILES.get(title)
    if not filename:
        return m.group(0)
    with open(filename, 'rb') as pf:
        b64 = base64.b64encode(pf.read()).decode('ascii')
    return 'data-pdf="data:application/pdf;base64,' + b64 + '" ' + m.group(0)

rest, n = pdf_pattern.subn(inject_pdf, rest)
assert n == len(PDF_FILES), 'expected %d paper triggers, matched %d' % (len(PDF_FILES), n)
print('embedded', n, 'real PDFs')

# reuse the already-embedded KCDA logo as the favicon (small enough as a data URI)
logo_start = source.find('id="siteLogoImg" src="')
assert logo_start != -1
logo_start += len('id="siteLogoImg" src="')
logo_end = source.find('"', logo_start)
logo_data_uri = source[logo_start:logo_end]

description = "한국커리어디자인협회(KCDA)는 커리어멘토 자격인증, 청년교육, 연구사업을 운영하는 비영리 전문 협회입니다."

head = '''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
''' + title_tag + '''
<meta name="description" content="''' + description + '''">
<link rel="canonical" href="https://kcdalab.co.kr/">
<link rel="icon" type="image/png" href="''' + logo_data_uri + '''">
<meta property="og:type" content="website">
<meta property="og:locale" content="ko_KR">
<meta property="og:title" content="''' + title_text + '''">
<meta property="og:description" content="''' + description + '''">
<meta property="og:url" content="https://kcdalab.co.kr/">
<meta name="google-site-verification" content="ddbYlWb3xO07qf063BGyZkIS32VwQuT6KwKzh04W-k4" />
</head>
<body>
'''

document = head + rest + '\n</body>\n</html>\n'

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(document)

print('index.html wrapped. size:', len(document))
