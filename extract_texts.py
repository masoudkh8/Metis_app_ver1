#!/usr/bin/env python
"""
Extract all English texts from HTML and Python files for translation
"""
import os
import re
from pathlib import Path

def extract_text_from_html(html_file):
    """Extract visible texts from HTML file"""
    texts = []
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract text between tags
    pattern = r'>([^<>\n{}]+?)<'
    matches = re.findall(pattern, content)
    
    for match in matches:
        text = match.strip()
        # Filter short texts, variables, and codes
        if (len(text) > 2 and 
            not text.startswith('{') and 
            not text.endswith('}') and
            not text.startswith('%') and
            not text.endswith('%') and
            not text.isdigit() and
            len(text) < 200):
            texts.append(text)
    
    return texts

def extract_flash_messages(py_file):
    """Extract flash messages from Python files"""
    messages = []
    with open(py_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all flash() calls
    pattern = r'flash\([\'"]([^\'"]+)[\'"]'
    matches = re.findall(pattern, content)
    
    for match in matches:
        if match.strip() and not match.startswith('{'):
            messages.append(match.strip())
    
    return messages

def main():
    workspace = '/workspace'
    templates_dir = os.path.join(workspace, 'templates')
    routes_dir = os.path.join(workspace, 'routes')
    
    all_texts = {}
    
    # Extract from templates
    print("=== Extracting text from templates ===\n")
    for root, dirs, files in os.walk(templates_dir):
        for file in files:
            if file.endswith('.html'):
                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, workspace)
                texts = extract_text_from_html(filepath)
                if texts:
                    all_texts[rel_path] = texts
                    print(f"\n{rel_path}:")
                    for text in texts[:10]:  # Show first 10
                        print(f"  - {text}")
                    if len(texts) > 10:
                        print(f"  ... and {len(texts) - 10} more texts")
    
    # Extract flash messages
    print("\n\n=== Extracting flash messages from routes ===\n")
    flash_messages = []
    for root, dirs, files in os.walk(routes_dir):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, workspace)
                messages = extract_flash_messages(filepath)
                if messages:
                    flash_messages.extend(messages)
                    print(f"\n{rel_path}:")
                    for msg in messages[:5]:
                        print(f"  - {msg}")
    
    # Save to file
    output_file = os.path.join(workspace, 'texts_to_translate.txt')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("Extracted texts for translation to Persian\n")
        f.write("=" * 50 + "\n\n")
        
        for filepath, texts in all_texts.items():
            f.write(f"\n### {filepath} ###\n")
            for text in texts:
                f.write(f"{text}\n")
        
        f.write("\n\n### Flash Messages ###\n")
        for msg in set(flash_messages):
            f.write(f"{msg}\n")
    
    print(f"\n\n✅ All texts saved to {output_file}.")

if __name__ == '__main__':
    main()
