#!/usr/bin/env python3
"""Test WeasyPrint with OTF font."""

from weasyprint import HTML, CSS

html_content = '''<!DOCTYPE html>
<html>
<head>
<style>
@font-face {
    font-family: 'SourceHanSans';
    src: url('/usr/share/fonts/SourceHanSans/SourceHanSansSC-Normal.otf');
}
body {
    font-family: 'SourceHanSans', sans-serif;
    font-size: 12pt;
}
h1 {
    color: #1a365d;
    border-bottom: 2px solid #3182ce;
}
</style>
</head>
<body>
<h1>中文测试</h1>
<p>这是一个测试文档，使用 WeasyPrint 和 OTF 字体生成 PDF。</p>
<p>English text also works correctly.</p>
</body>
</html>'''

html = HTML(string=html_content, base_url='/')
html.write_pdf('/tmp/test_weasyprint.pdf')
print('PDF generated successfully!')

import os
size = os.path.getsize('/tmp/test_weasyprint.pdf')
print(f'PDF size: {size} bytes')