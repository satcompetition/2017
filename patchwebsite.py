#!/usr/bin/env python3

import os
import re

def extract_categories_and_nav(index_php_path):
    with open(index_php_path, 'r', encoding='utf-8') as f:
        php = f.read()
    # Extract $cats array
    cats_match = re.search(r'\$cats\s*=\s*array\s*\((.*?)\);', php, re.DOTALL)
    cats = []
    if cats_match:
        cats = [c.strip().strip('"').strip("'") for c in cats_match.group(1).split(',')]
    # Extract navigation block
    nav_match = re.search(r'<div class="navigation">(.*?)</div>', php, re.DOTALL)
    nav_html = nav_match.group(1) if nav_match else ''
    return cats, nav_html

def generate_navigation_html(nav_html):
    # Replace PHP logic with static highlighting using id attributes
    nav_html = re.sub(
        r"<a href=\"index\.php(\?cat=([a-zA-Z0-9_]+))?\"[^\>]*\>(.*?)</a>",
        lambda m: f"<a href='{m.group(2) + '.html' if m.group(2) else 'index.html'}' id='{m.group(2) if m.group(2) else 'index'}'>{m.group(3)}</a>",
        nav_html
    )
    return nav_html

def get_dynamic_title(content, fallback):
    # Try to extract the first <h1> or <h2> as the title
    m = re.search(r'<h1[^>]*>(.*?)</h1>', content, re.IGNORECASE|re.DOTALL)
    if not m:
        m = re.search(r'<h2[^>]*>(.*?)</h2>', content, re.IGNORECASE|re.DOTALL)
    if m:
        return re.sub('<.*?>', '', m.group(1)).strip()  # Remove any tags inside
    return fallback

def patch_page(filename, nav_id):
    if not os.path.exists(filename):
        print(f"Skipping {filename} (not found)")
        return
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    # Remove any existing html/head/body tags
    content = re.sub(r'(?is)<!DOCTYPE.*?<body.*?>', '', content)
    content = re.sub(r'(?is)</body>.*?</html>', '', content)
    content = content.strip()
    # Fix internal links
    content = re.sub(r'index\\.php\\?cat=([a-zA-Z0-9_]+)', r'\1.html', content)
    # Dynamic title
    page_title = get_dynamic_title(content, nav_id.capitalize())
    # Build new HTML
    new_html = f'''<!DOCTYPE html>
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<title>{page_title} - SAT Competition</title>
<link rel="stylesheet" href="main.css" type="text/css">
<link rel="icon" type="image/x-icon" href="doge2.ico">
<script src="https://www.w3schools.com/lib/w3.js"></script>
<style>a#{nav_id} {{ color:#c20114; }}</style>
</head>
<body>
<div class="main">
  <div class="navigation" w3-include-html="navigation.html"></div>
  <script>w3.includeHTML();</script>
  <div class="content">
{content}
  </div>
</div>
</body>
</html>
'''
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(new_html)
    print(f"Patched {filename}")

def main():
    index_php = 'index.php'
    welcome_html = 'welcome.html'
    cats, nav_html = extract_categories_and_nav(index_php)
    # Generate navigation.html
    nav_out = generate_navigation_html(nav_html)
    with open('navigation.html', 'w', encoding='utf-8') as f:
        f.write(nav_out)
    print("Generated navigation.html")
    # Generate index.html from welcome.html
    with open(welcome_html, 'r', encoding='utf-8') as f:
        welcome_content = f.read()
    index_title = get_dynamic_title(welcome_content, "Overview")
    index_out = f"""<!DOCTYPE html>
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<title>{index_title} - SAT Competition</title>
<link rel="stylesheet" href="main.css" type="text/css">
<link rel="icon" type="image/x-icon" href="doge2.ico">
<script src="https://www.w3schools.com/lib/w3.js"></script>

<style>a#index {{ color:#c20114; }}</style>
</head>
<body>
<div class="main">
  <div class="navigation" w3-include-html="navigation.html"></div>
  <script>w3.includeHTML();</script>
  <div class="content">
    <h1>SAT Competition</h1>
{welcome_content}
  </div>
</div>
</body>
</html>
"""
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(index_out)
    print("Generated index.html")
    # Patch all other pages
    for cat in cats:
        fname = f"{cat}.html" if cat != 'welcome' else 'index.html'
        nav_id = cat if cat != 'welcome' else 'index'
        if fname == 'index.html':
            continue  # already generated
        patch_page(fname, nav_id)
        
def fix_all_html_links():
    html_files = [f for f in os.listdir('.') if f.endswith('.html')]
    for fname in html_files:
        with open(fname, 'r', encoding='utf-8') as f:
            content = f.read()
        # Replace all index.php?cat=... (with or without quotes) with ...html
        new_content = re.sub(
            r'index\.php\?cat=([a-zA-Z0-9_]+)',
            r'\1.html',
            content
        )
        if new_content != content:
            with open(fname, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Fixed links in {fname}")

if __name__ == '__main__':
    # main()
    fix_all_html_links()