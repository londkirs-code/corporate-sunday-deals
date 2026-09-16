from datetime import datetime
import json
from playwright.sync_api import sync_playwright

URL = 'https://www.mycorporate.co.il/?page=category&id=113'

def scrape_deal():
    deals = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        try:
            page.goto(URL, wait_until='networkidle', timeout=60000)
            page.wait_for_timeout(8000)
            for _ in range(3):
                page.mouse.wheel(0, 2000)
                page.wait_for_timeout(1500)
            items = page.evaluate("() => { const r=[]; const s=new Set(); document.querySelectorAll('a[href*=\"page=Benefit\"]').forEach(a=>{ if(s.has(a.href)) return; s.add(a.href); const c=a.closest('div'); if(!c) return; const tEl=c.querySelector('h2,h3,h4'); let t=tEl?tEl.innerText.trim():a.innerText.trim(); let img=c.querySelector('img')?c.querySelector('img').src:''; if(t && t.length>3 && t.length<120 && !t.includes('קטגוריות')) r.push({title:t,image:img,link:a.href}); }); return r; }")
            seen=set()
            for it in items:
                if it['title'] not in seen:
                    seen.add(it['title'])
                    deals.append({'title':it['title'],'image':it['image'],'link':it['link'],'updated_at':datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
        finally:
            browser.close()
    return deals

def build_html(deals, last_checked, url):
    cards=""
    if deals:
        for d in deals:
            img=f'<img src="{d["image"]}" alt="">' if d.get('image') else ''
            cards+=f'<div class="deal-card">{img}<div class="deal-title">{d["title"]}</div><a href="{d["link"]}" class="btn" target="_blank">לפרטים והטבה</a></div>\n'
    else:
        cards='<p style="text-align:center;color:#666;">לא נמצאו מבצעים</p>'
    return f"""<!DOCTYPE html><html lang="he" dir="rtl"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Corporate SUNDAY</title><style>body{{font-family:system-ui;background:#f8f9fa;margin:0;padding:20px;direction:rtl}}.container{{max-width:600px;margin:0 auto;background:#fff;padding:20px;border-radius:12px}}h1{{color:#d63384;text-align:center}}.meta{{text-align:center;color:#666;margin-bottom:20px}}.deal-card{{border:1px solid #eee;border-radius:8px;padding:15px;margin-bottom:15px}}.deal-card img{{max-width:100%;border-radius:6px;margin-bottom:10px;display:block}}.deal-title{{font-weight:bold;margin-bottom:10px}}.btn{{display:block;background:#000;color:#fff;padding:10px;border-radius:6px;text-align:center;text-decoration:none}}</style></head><body><div class="container"><h1>🎁 Corporate SUNDAY</h1><div class="meta">עדכון: {last_checked} | {len(deals)} הטבות</div>{cards}<div style="text-align:center;margin-top:20px"><a href="{url}" target="_blank">🔗 לדף הרשמי</a></div></div></body></html>"""

if __name__ == '__main__':
    deals=scrape_deal()
    last=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    data={'last_checked':last,'deals':deals}
    with open('deal.json','w',encoding='utf-8') as f:
        json.dump(data,f,ensure_ascii=False,indent=2)
    html=build_html(deals,last,URL)
    with open('index.html','w',encoding='utf-8') as f:
        f.write(html)
    print("Done")
