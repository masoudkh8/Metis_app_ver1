#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
استخراج تمام متن‌های انگلیسی از پروژه و به‌روزرسانی فایل PO برای ترجمه
"""
import re
import os
from datetime import datetime

def extract_texts_from_html(filepath):
    """Extract visible texts from HTML file"""
    texts = []
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # استخراج متن بین تگ‌ها (بدون متغیرهای Jinja2)
    pattern = r'>([^<>{}%]+?)<'
    matches = re.findall(pattern, content)
    
    for match in matches:
        text = match.strip()
        if (len(text) > 1 and 
            len(text) < 300 and
            not text.startswith('{') and 
            not text.endswith('}') and
            not text.startswith('%') and
            not text.endswith('%') and
            not text.replace(' ', '').replace('-', '').isdigit()):
            texts.append(text)
    
    return texts

def extract_flash_messages(filepath):
    """Extract flash messages from Python file"""
    messages = []
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # پیدا کردن تمام flash() ها
    patterns = [
        r'flash\([\'"]([^\'"]+)[\'"]',
        r"flash\([\"']([^\"']+)[\"']",
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, content)
        for match in matches:
            if match.strip():
                messages.append(match.strip())
    
    return messages

def extract_all_texts(workspace):
    """Extract all texts from project"""
    all_texts = {}
    
    # استخراج از تمپلیت‌ها
    templates_dir = os.path.join(workspace, 'templates')
    print("=== Extracting texts from templates ===")
    for root, dirs, files in os.walk(templates_dir):
        for file in files:
            if file.endswith('.html'):
                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, workspace)
                texts = extract_texts_from_html(filepath)
                if texts:
                    if rel_path not in all_texts:
                        all_texts[rel_path] = []
                    all_texts[rel_path].extend(texts)
                    print(f"  ✓ {rel_path}: {len(texts)} texts")
    
    # Extract flash messages from routes
    routes_dir = os.path.join(workspace, 'routes')
    print("\n=== Extracting flash messages from routes ===")
    flash_messages = {}
    for root, dirs, files in os.walk(routes_dir):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, workspace)
                messages = extract_flash_messages(filepath)
                if messages:
                    if rel_path not in flash_messages:
                        flash_messages[rel_path] = []
                    flash_messages[rel_path].extend(messages)
                    print(f"  ✓ {rel_path}: {len(messages)} messages")
    
    # استخراج از app.py
    app_file = os.path.join(workspace, 'app.py')
    if os.path.exists(app_file):
        messages = extract_flash_messages(app_file)
        if messages:
            flash_messages['app.py'] = messages
            print(f"  ✓ app.py: {len(messages)} messages")
    
    return all_texts, flash_messages

def update_po_file(po_file, all_texts, flash_messages):
    """Update PO file with new texts"""
    
    # خواندن فایل PO فعلی
    existing_msgids = set()
    if os.path.exists(po_file):
        with open(po_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # پیدا کردن تمام msgidهای موجود
            pattern = r'^msgid "(.*?)"$'
            matches = re.findall(pattern, content, re.MULTILINE)
            existing_msgids = set(matches)
    
    # جمع‌آوری تمام متن‌های یکتا
    all_unique_texts = set()
    for filepath, texts in all_texts.items():
        all_unique_texts.update(texts)
    
    for filepath, messages in flash_messages.items():
        all_unique_texts.update(messages)
    
    print(f"\n=== Statistics ===")
    print(f"Existing texts in PO: {len(existing_msgids)}")
    print(f"Total extracted texts: {len(all_unique_texts)}")
    
    # پیدا کردن متن‌های جدید
    new_texts = all_unique_texts - existing_msgids
    print(f"New texts requiring translation: {len(new_texts)}")
    
    if new_texts:
        print(f"\n=== Adding {len(new_texts)} new texts to PO file ===")
        
        with open(po_file, 'a', encoding='utf-8') as f:
            f.write(f"\n# Added on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            for text in sorted(new_texts):
                # فرار دادن کاراکترهای خاص
                escaped_text = text.replace('\\', '\\\\').replace('"', '\\"')
                f.write(f'\n#: templates/\nmsgid "{escaped_text}"\n')
                f.write('msgstr ""\n')
        
        print("✓ New texts successfully added")
    else:
        print("✓ No new texts found")
    
    return len(new_texts)

def main():
    workspace = '/workspace'
    po_file = os.path.join(workspace, 'translations', 'fa', 'LC_MESSAGES', 'messages.po')
    
    print("🔍 Starting text extraction from project...\n")
    
    # استخراج تمام متن‌ها
    all_texts, flash_messages = extract_all_texts(workspace)
    
    # به‌روزرسانی فایل PO
    new_count = update_po_file(po_file, all_texts, flash_messages)
    
    print(f"\n✅ Process completed!")
    print(f"   {new_count} new texts added to PO file")
    print(f"   File: {po_file}")
    print("\n📝 Now you can:")
    print("   1. Edit the PO file and enter translations")
    print("   2. Run the following command to build the MO file:")
    print("      msgfmt -o translations/fa/LC_MESSAGES/messages.mo translations/fa/LC_MESSAGES/messages.po")

if __name__ == '__main__':
    main()
