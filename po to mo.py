import os
import sys
from babel.messages import pofile, mofile

po_file = "translations/fa_IR/LC_MESSAGES/messages.po"
mo_file = "translations/fa_IR/LC_MESSAGES/messages.mo"

def compile_po_to_mo(po_path, mo_path):
    if not os.path.exists(po_path):
        print(f"❌ File not found: {po_path}")
        return False

    try:
        # اطمینان از وجود دایرکتوری مقصد
        os.makedirs(os.path.dirname(mo_path), exist_ok=True)

        # خواندن فایل PO
        with open(po_path, "rb") as f:
            catalog = pofile.read_po(f)

        # نوشتن فایل MO با فرمت استاندارد GNU gettext
        with open(mo_path, "wb") as f:
            mofile.write_mo(f, catalog)

        if os.path.exists(mo_path) and os.path.getsize(mo_path) > 0:
            print(f"✅ MO file successfully created: {mo_path}")
            print(f"📊 Stats: {len(catalog)} strings translated.")
            return True
        else:
            print("❌ MO file was not created or is empty.")
            return False

    except Exception as e:
        print(f"❌ Compilation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print(f"🔄 Compiling {po_file} → {mo_file}...")
    success = compile_po_to_mo(po_file, mo_file)
    sys.exit(0 if success else 1)