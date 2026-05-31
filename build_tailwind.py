#!/usr/bin/env python3
import subprocess
import sys
import os

def build_tailwind():
    """Build Tailwind CSS using npx"""
    try:
        # Check if node_modules exists
        if not os.path.exists('node_modules'):
            print("Installing npm packages...")
            subprocess.run(['npm', 'install'], check=True)
        
        # Build Tailwind CSS
        print("Building Tailwind CSS...")
        result = subprocess.run([
            'npx', 'tailwindcss',
            '-i', './static/css/input.css',
            '-o', './static/css/output.css',
            '--minify'
        ], check=True, capture_output=True, text=True)
        
        print(result.stdout)
        print("✓ Tailwind CSS built successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Error building Tailwind CSS: {e}")
        print(e.stderr)
        return False
    except FileNotFoundError:
        print("✗ npm/npx not found. Please install Node.js")
        return False

if __name__ == '__main__':
    success = build_tailwind()
    sys.exit(0 if success else 1)
