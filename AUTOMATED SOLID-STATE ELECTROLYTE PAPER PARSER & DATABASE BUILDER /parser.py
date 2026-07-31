with open("parser.py", "w") as f:
    f.write(r'''
import os, re, zlib

class ScientificPDFParser:
    def __init__(self, prefer_docling: bool = True): pass
    def parse_pdf(self, pdf_path: str):
        with open(pdf_path, 'rb') as f: content = f.read()
        text_parts = []
        for s in re.findall(rb'stream[\r\n]+(.*?)[\r\n]+endstream', content, re.DOTALL):
            try:
                decompressed = zlib.decompress(s)
                for st in re.findall(rb'
\s*Tj', decompressed):
                    text_parts.append(st.decode('utf-8', errors='ignore'))
            except Exception: pass
        text = " ".join(text_parts)
        if not text.strip():
            text = re.sub(rb'[^a-zA-Z0-9\.\-\_\s]', b' ', content).decode('ascii', errors='ignore')
        return text[:100000], "PurePython"
''')

