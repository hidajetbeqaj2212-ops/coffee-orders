#!/usr/bin/env python3
"""Builds a single-file test page from prototype/pos.html (demo data, nothing installed).
Receipts open as an on-screen preview instead of printing. Usage: python3 tools/build-demo.py [out.html]"""
import sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
out = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'dist' / 'xbar-demo.html'
s = (ROOT / 'prototype' / 'pos.html').read_text()

PRINT = "setTimeout(()=>{ try{ window.print(); }catch(e){} },60);"
if s.count(PRINT) != 2:
    sys.exit('print calls not found')
s = s.replace(PRINT, "setTimeout(showReceipt,60);")

DEMO_CSS = """
/* test page: receipt preview instead of printing */
.rcpt-sheet{max-width:380px}
.rcpt{width:min(300px,100%); margin:4px auto 0; padding:16px 14px 18px; background:#fff; color:#000; font:13px/1.35 Arial,sans-serif; box-shadow:0 1px 0 #e3e3e0, 0 10px 30px rgba(18,18,18,.14); border-radius:4px}
.rcpt img{width:150px; display:block; margin:0 auto 8px}
.rcpt .pc{text-align:center; font-size:12px}
.rcpt hr{border:0; border-top:1px dashed #000; margin:7px 0}
.rcpt .pr{display:flex; justify-content:space-between; gap:10px}
.rcpt .pt{font-size:16px; font-weight:700}
.rcpt .nf{margin-top:5px; font-size:11px}
.rcpt-h{display:flex; justify-content:space-between; align-items:baseline; gap:12px; margin-bottom:12px}
.rcpt-h h2{font-size:20px; font-weight:800}
.rcpt-h span{color:var(--mute); font-weight:600; font-size:14px}
"""
s = s.replace('</style>', DEMO_CSS + '</style>', 1)

DEMO_JS = """
function showReceipt(){
  const el=document.getElementById('prt'); if(!el||!el.innerHTML.trim()) return;
  modal(`<div class="rcpt-h"><h2>Fatura</h2><span>Në lokal del nga printeri</span></div><div class="rcpt">${el.innerHTML}</div>
    <div class="btns" style="margin-top:16px"><button class="btn pri full" data-close>Mbyll</button></div>`,'rcpt-sheet');
}
"""
anchor = 'function modal(h,cls){'
if anchor not in s:
    sys.exit('modal() not found')
s = s.replace(anchor, DEMO_JS + anchor, 1)

# viewport for opening the file directly on a phone (the Artifact page adds its own)
s = s.replace('<title>', '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n<title>', 1)

out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(s)
print('wrote', out, len(s), 'bytes')
