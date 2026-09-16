from datetime import datetime
import json
from playwright.sync_api import sync_playwright

URL = 'https://www.mycorporate.co.il/?page=category&id=113'

def scrape_deal():
    deals = []
    print(f"Scraping {URL} with real browser...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page.goto(URL, wait_until='networkidle', timeout=60000)
        page.wait_for_timeout(8000)

        for _ in range(4):
            page.mouse.wheel(0, 2500)
            page.wait_for_timeout(1500)

        items = page.evaluate("""() => {
            const results = [];
            const seenLinks = new Set();
            document.querySelectorAll('a[href*="page=Benefit"]').forEach(a => {
                const href = a.href;
                if (seenLinks.has(href)) return;
                seenLinks.add(href);
                const card = a.closest('div');
                if (!card) return;
                const titleEl = card.querySelector('h2, h3, h4, [class*="title"], [class*="name"]');
                let title = titleEl ? titleEl.innerText.trim() : a.innerText.trim();
                let img = card.querySelector('img') ? card.querySelector('img').src : '';
                if (title && title.length > 3 && title.length < 120 && !title.includes('קטגוריות')) {
                    results.push({title: title, image: img, link: href});
                }
            });
            return results;
        }""")

        unique = {}
        for item in items:
            if item['title'] not in unique:
                unique[item['title']] = item
        
        for title, d in unique.items():
            deals.append({
                'title': d['title'],
                'image': d['image'],
                'link': d['link'],
                'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })

        print(f"Found {len(deals)} deals")
        browser.close()
    return deals

if __name__ == '__main__':
    deals = scrape_deal()
    data = {
        'last_checked': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'deals': deals,
    }

    with open('deal.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    cards_html = ""
    if deals:
        for d in deals:
            img_tag = f'<img src="{d["image"]}" alt="">' if d["image"] else ''
            cards_html += f"""
            <div class="deal-card">
                {img_tag}
                <div class="deal-title">{d['title']}</div>
                <a href="{d['link']}" class="btn" target="_blank">לפרטים והטבה</a>
            </div>"""
    else:
        cards_html = '<p style="text-align:center;color:#666;">לא נמצאו מבצעים, נסה להריץ שוב</p>'

    html_content = f"""<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Corporate SUNDAY</title>
    <style>
        body {{ font-family: system-ui, sans-serif; background: #f8f9fa; margin: 0; padding: 20px; direction: rtl; }}
        .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 20px; border-radius: 12px; }}
        h1 {{ color: #d63384; text-align: center; }}
        .meta {{ text-align: center; color: #666; font-size: 0.9rem; margin-bottom: 20px; }}
        .deal-card {{ border: 1px solid #eee; border-radius: 8px; padding: 15px; margin-bottom: 15px; }}
        .deal-card img {{ max-width: 100%; border-radius: 6px; margin-bottom: 10px; }}
        .deal-title {{ font-weight: bold; margin-bottom: 10px; }}
        .btn {{ display: block; background: #000; color: #fff; padding: 10px; border-radius: 6px; text-align: center; text-decoration: none; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎁 Corporate SUNDAY</h1>
        <div class="meta">עדכון: {data['last_checked']} | {len(deals)} הטבות</div>
        {cards_html}
        <div style="text-align:center;margin-top:20px;"><a href="{URL}" target="_blank">🔗 לדף הרשמי</a></div>
    </div>
</body>
</html>"""

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)e for card in cards:
    title_elem = card.find(['h2', 'h3', 'h4', 'span', 'p'])
    title = title_elem.get_text(strip=True) if title_elem else ''

    img_elem = card.find('img')
    img_url = ''
    if img_elem:
      img_url = img_elem.get('src') or img_elem.get('data-src') or ''
      if img_url and not img_url.startswith('http'):
        img_url = 'https://www.mycorporate.co.il' + (
            img_url if img_url.startswith('/') else '/' + img_url
        )

    link_elem = card if card.name == 'a' else card.find('a', href=True)
    link = ''
    if link_elem:
      href = link_elem.get('href', '')
      if href:
        if not href.startswith('http'):
          link = 'https://www.mycorporate.co.il' + (
              href if href.startswith('/') else '/' + href
          )
        else:
          link = href

    if title and len(title) > 3:
      deals.append(
          {
              'title': title,
              'image': img_url,
              'link': link,
              'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
          }
      )

  seen = set()
  unique_deals = []
  for d in deals:
    if d['title'] not in seen:
      seen.add(d['title'])
      unique_deals.append(d)

  return unique_deals

if __name__ == '__main__':
  deals = scrape_deal()
  data = {
      'last_checked': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
      'deals': deals,
  }

  with open('deal.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

  html_content = f"""<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Corporate SUNDAY - בדיקת מבצעים</title>
    <style>
        body {{ font-family: system-ui, -apple-system, sans-serif; background: #f8f9fa; color: #333; margin: 0; padding: 20px; direction: rtl; }}
        .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
        h1 {{ color: #d63384; text-align: center; font-size: 1.8rem; }}
        .meta {{ text-align: center; color: #666; font-size: 0.9rem; margin-bottom: 20px; }}
        .deal-card {{ border: 1px solid #eee; border-radius: 8px; padding: 15px; margin-bottom: 15px; background: #fff; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }}
        .deal-card img {{ max-width: 100%; border-radius: 6px; height: auto; display: block; margin-bottom: 10px; }}
        .deal-title {{ font-size: 1.2rem; font-weight: bold; margin-bottom: 10px; color: #222; }}
        .btn {{ display: inline-block; background: #000; color: #fff; padding: 10px 20px; border-radius: 6px; text-decoration: none; font-weight: bold; text-align: center; width: 100%; box-sizing: border-box; }}
        .btn:hover {{ background: #333; }}
        .source-link {{ text-align: center; margin-top: 20px; }}
        .source-link a {{ color: #0d6efd; text-decoration: none; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎁 Corporate SUNDAY</h1>
        <div class="meta">עדכון אחרון: {data['last_checked']}</div>
        <div id="deals-list">
"""

  if deals:
    for d in deals:
      html_content += f"""
            <div class="deal-card">
                {'<img src="' + d['image'] + '" alt="Deal Image">' if d['image'] else ''}
                <div class="deal-title">{d['title']}</div>
                {'<a href="' + d['link'] + '" class="btn" target="_blank">לפרטים והטבה</a>' if d['link'] else ''}
            </div>
"""
  else:
    html_content += """
            <p style="text-align: center; color: #666;">לא נמצאו מבצעים כרגע. ניתן לגשת לאתר הרשמי:</p>
"""

  html_content += f"""
        </div>
        <div class="source-link">
            <a href="{URL}" target="_blank">🔗 מעבר ישיר לדף המבצעים הרשמי</a>
        </div>
    </div>
</body>
</html>
"""

  with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

  print(
      f'Scraped {len(deals)} items successfully and updated deal.json & index.html'
  )
