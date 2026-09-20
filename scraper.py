from datetime import datetime
from zoneinfo import ZoneInfo
import json
import os
from playwright.sync_api import sync_playwright

URL = 'https://www.mycorporate.co.il/?page=category&id=113'
JERUSALEM = ZoneInfo("Asia/Jerusalem")

def scrape_deal():
    deals = []
    banner_text = "בכל יום ראשון - מבצע חדש ומפתיע!"
    page_title = "Corporate SUNDAY"
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=['--no-sandbox','--disable-blink-features=AutomationControlled']
        )
        # === התיקון ל-21:00 - מזדהה כשעון ישראל ===
        context = browser.new_context(
            timezone_id='Asia/Jerusalem',
            locale='he-IL',
            geolocation={'latitude': 32.0853, 'longitude': 34.7818},
            permissions=['geolocation'],
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            extra_http_headers={'Accept-Language': 'he-IL,he;q=0.9,en;q=0.8'}
        )
        context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        page = context.new_page()

        try:
            page.goto(URL, wait_until='domcontentloaded', timeout=90000)
            page.wait_for_timeout(8000)
            try:
                page.wait_for_load_state('networkidle', timeout=15000)
            except:
                pass
            for _ in range(3):
                page.mouse.wheel(0, 2000)
                page.wait_for_timeout(1500)

            # DEBUG
            open("debug.html","w",encoding="utf-8").write(page.content())
            page.screenshot(path="debug.png", full_page=True)

            data = page.evaluate("""() => {
                const result = { title: '', banner: '', deals: [] };
                result.title = document.querySelector('h1')?.innerText.trim() || 'Corporate SUNDAY';
                const bodyText = document.body.innerText;
                const match = bodyText.match(/בכל יום ראשון[^\\n]{0,80}/);
                if (match) result.banner = match[0];
                const seen = new Set();
                // מחפש גם Benefit וגם כל כרטיס מוצר
                const links = document.querySelectorAll('a[href*="Benefit"], a[href*="benefit"],.product-item a,.deal-card a');
                links.forEach(a => {
                    if (!a.href || seen.has(a.href)) return;
                    seen.add(a.href);
                    const card = a.closest('div') || a.parentElement;
                    if (!card) return;
                    let t = (card.innerText.split('\\n').find(x=>x.trim().length>4) || a.innerText).trim();
                    let imgEl = card.querySelector('img');
                    let img = imgEl? (imgEl.src || imgEl.getAttribute('data-src') || '') : '';
                    if (t && t.length > 3 && t.length < 120 &&!t.includes('קטגוריות') &&!t.includes('סינון')) {
                        result.deals.push({title: t, image: img, link: a.href});
                    }
                });
                return result;
            }""")
            page_title = data.get('title') or page_title
            if data.get('banner'):
                banner_text = data['banner']
            seen_titles = set()
            for it in data.get('deals', []):
                t = it['title'].strip()
                if t and t not in seen_titles and len(t)>3:
                    seen_titles.add(t)
                    deals.append({'title': t, 'image': it['image'], 'link': it['link'], 'updated_at': datetime.now(JERUSALEM).strftime('%Y-%m-%d %H:%M:%S')})
        except Exception as e:
            print(f"Error: {e}")
        finally:
            browser.close()
    if not deals:
        deals = [{'title': banner_text, 'image': '', 'link': URL, 'updated_at': datetime.now(JERUSALEM).strftime('%Y-%m-%d %H:%M:%S'), 'is_banner': True, 'description': 'בכל יום ראשון עולה מבצע חדש ומפתיע לחברי מועדון Corporate. שווה לחזור ביום ראשון!'}]
    return deals, page_title

def build_html(deals, last_checked, url, page_title):
    cards_html = ""
    for d in deals:
        is_banner = d.get('is_banner')
        img_html = f'<img src="{d["image"]}" alt="">' if d.get('image') else ''
        desc_html = f'<div class="desc">{d["description"]}</div>' if d.get('description') else ''
        btn_text = 'למעבר לדף המבצעים' if is_banner else 'לפרטים והטבה'
        btn_class = 'btn banner-btn' if is_banner else 'btn'
        cards_html += f'<div class="deal-card {"banner-card" if is_banner else ""}">{img_html}<div class="deal-title">{d["title"]}</div>{desc_html}<a href="{d["link"]}" class="{btn_class}" target="_blank">{btn_text}</a></div>\n'
    html = f"""<!DOCTYPE html><html lang="he" dir="rtl"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>{page_title}</title><style>body{{font-family:system-ui,sans-serif;background:#f8f9fa;margin:0;padding:20px;direction:rtl}}.container{{max-width:600px;margin:0 auto;background:#fff;padding:20px;border-radius:12px;box-shadow:0 4px 12px rgba(0,0,0,0.1)}}h1{{color:#d63384;text-align:center}}.meta{{text-align:center;color:#666;margin-bottom:20px}}.deal-card{{border:1px solid #eee;border-radius:12px;padding:20px;margin-bottom:15px}}.deal-card img{{max-width:100%;border-radius:8px;margin-bottom:12px;display:block}}.deal-title{{font-weight:bold;font-size:1.2rem;margin-bottom:8px}}.desc{{color:#555;margin-bottom:12px}}.btn{{display:block;background:#000;color:#fff;padding:12px;border-radius:8px;text-align:center;text-decoration:none;font-weight:bold}}.banner-card{{background:linear-gradient(135deg,#fff0f5 0%,#ffe4ec 100%);border:2px solid #d63384}}.banner-btn{{background:#d63384}}</style></head><body><div class="container"><h1>🎁 {page_title}</h1><div class="meta">עדכון אחרון: {last_checked} (שעון ישראל)</div>{cards_html}<div style="text-align:center;margin-top:20px"><a href="{url}" target="_blank">🔗 לדף הרשמי</a></div></div></body></html>"""
    return html

if __name__ == '__main__':
    deals, title = scrape_deal()
    last = datetime.now(JERUSALEM).strftime('%Y-%m-%d %H:%M:%S')
    data = {'last_checked': last, 'deals': deals, 'title': title}
    with open('deal.json','w',encoding='utf-8') as f:
        json.dump(data,f,ensure_ascii=False,indent=2)
    with open('docs/deal.json','w',encoding='utf-8') as f:
        json.dump(data,f,ensure_ascii=False,indent=2)
    html = build_html(deals, last, URL, title)
    with open('index.html','w',encoding='utf-8') as f:
        f.write(html)
    with open('docs/index.html','w',encoding='utf-8') as f:
        f.write(html)
    print(f"Done - {len(deals)} items - {last}")
