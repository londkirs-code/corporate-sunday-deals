from datetime import datetime
import json
import os
from bs4 import BeautifulSoup
import requests

URL = 'https://www.mycorporate.co.il/?page=category&id=113'

def scrape_deal():
  headers = {
      'User-Agent': (
          'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,'
          ' like Gecko) Chrome/120.0.0.0 Safari/537.36'
      )
  }
  try:
    response = requests.get(URL, headers=headers, timeout=15)
    response.raise_for_status()
  except Exception as e:
    print(f'Error fetching page: {e}')
    return []

  soup = BeautifulSoup(response.text, 'html.parser')
  deals = []

  cards = soup.find_all(
      ['div', 'article', 'li', 'a'],
      class_=lambda x: x
      and any(
          c in str(x).lower() for c in ['card', 'item', 'product', 'deal', 'box']
      ),
  )

  if not cards:
    cards = soup.find_all('a', href=True)

  for card in cards:
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
