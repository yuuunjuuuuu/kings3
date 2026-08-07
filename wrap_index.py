# -*- coding: utf-8 -*-
# Builds a proper standalone HTML document (index.html) from the Artifact-format
# source (kcda-website.html), which intentionally has no <!DOCTYPE>/<html>/<head>/
# <body> wrapper (the Claude Artifact platform injects that itself). Vercel serves
# index.html directly with no such wrapper, so it needs its own real <head> with
# SEO/meta tags. Re-run this after every `cp kcda-website.html index.html` sync.

with open('kcda-website.html', 'r', encoding='utf-8') as f:
    source = f.read()

title_start = source.find('<title>')
title_end = source.find('</title>') + len('</title>')
assert title_start == 0, "expected <title> to be the very first thing in the source"
title_tag = source[title_start:title_end]
title_text = source[title_start + len('<title>'):title_end - len('</title>')]
rest = source[title_end:]

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
