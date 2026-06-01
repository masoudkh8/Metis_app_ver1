import os
import sys
import subprocess

# File paths
po_file = "translations/fa_IR/LC_MESSAGES/messages.po"
mo_file = "translations/fa_IR/LC_MESSAGES/messages.mo"

def compile_po_to_mo(po_path, mo_path):
    """
    Compile PO file to MO using Python standard library (no need to install gettext on system)
    This function uses the internal babel module for compilation if available,
    otherwise uses pure Python implementation.
    """
    if not os.path.exists(po_path):
        print(f"❌ File {po_path} not found.")
        return False

    try:
        # Create destination directory if it doesn't exist
        os.makedirs(os.path.dirname(mo_path), exist_ok=True)

        # Try to use babel if installed
        try:
            from babel.messages import pofile, mofile
            # Use babel for compilation
            catalog = pofile.read_po(open(po_path, 'rb'))
            mo_data = mofile.write_mo(catalog)
            with open(mo_path, 'wb') as f:
                f.write(mo_data)
            
            if os.path.exists(mo_path) and os.path.getsize(mo_path) > 0:
                print(f"✅ MO file successfully created (with Babel): {mo_path}")
                return True
        except ImportError:
            pass  # If babel is not installed, use alternative method
        except Exception as babel_error:
            print(f"⚠️ Error in Babel: {babel_error}, using alternative method...")

        # Alternative method: Read PO file and write binary MO manually
        # This is a simplified implementation
        import struct
        import hashlib
        
        translations = {}
        current_msgid = None
        current_msgstr = ""
        in_msgstr = False
        
        with open(po_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('msgid'):
                    if current_msgid is not None:
                        translations[current_msgid] = current_msgstr
                    current_msgid = line[6:].strip().strip('"')[1:-1] if len(line) > 7 else ""
                    current_msgstr = ""
                    in_msgstr = False
                elif line.startswith('msgstr'):
                    in_msgstr = True
                    current_msgstr = line[7:].strip().strip('"')[1:-1] if len(line) > 8 else ""
                elif in_msgstr and line.startswith('"') and line.endswith('"'):
                    current_msgstr += line[1:-1]
                elif line == '' or line.startswith('#'):
                    continue
        
        if current_msgid is not None:
            translations[current_msgid] = current_msgstr
        
        # Write MO file in simple binary format
        # MO file header
        magic = 0x950412de  # Magic number for MO files
        revision = 0
        num_strings = len(translations)
        
        # Calculate offsets
        header_size = 28  # Fixed header size
        key_table_offset = header_size
        value_table_offset = key_table_offset + (num_strings * 8)
        
        keys_data = []
        values_data = []
        current_offset = value_table_offset
        
        key_offsets = []
        value_offsets = []
        
        for key, value in sorted(translations.items()):
            if not key:  # Skip empty key
                continue
            
            key_bytes = key.encode('utf-8')
            value_bytes = value.encode('utf-8')
            
            keys_data.append(key_bytes)
            values_data.append(value_bytes)
            
            key_offsets.append((len(key_bytes), current_offset))
            current_offset += len(key_bytes)
            
            value_offsets.append((len(value_bytes), current_offset))
            current_offset += len(value_bytes)
        
        # Build binary
        binary_data = struct.pack('<I', magic)  # Magic
        binary_data += struct.pack('<I', revision)  # Revision
        binary_data += struct.pack('<I', num_strings)  # Number of strings
        binary_data += struct.pack('<I', key_table_offset)  # Key table offset
        binary_data += struct.pack('<I', value_table_offset)  # Value table offset
        binary_data += struct.pack('<I', 0)  # Hash table size (0 for simple)
        binary_data += struct.pack('<I', 0)  # Hash table offset
        
        # Key table (length, offset)
        for length, offset in key_offsets:
            binary_data += struct.pack('<I', length)
            binary_data += struct.pack('<I', offset)
        
        # Value table (length, offset)
        for length, offset in value_offsets:
            binary_data += struct.pack('<I', length)
            binary_data += struct.pack('<I', offset)
        
        # Key data
        for key_bytes in keys_data:
            binary_data += key_bytes
        
        # Value data
        for value_bytes in values_data:
            binary_data += value_bytes
        
        with open(mo_path, 'wb') as f:
            f.write(binary_data)
        
        if os.path.exists(mo_path) and os.path.getsize(mo_path) > 0:
            print(f"✅ MO file successfully created (pure Python method): {mo_path}")
            return True
        else:
            print("❌ MO file was not created or is empty.")
            return False
            
    except Exception as e:
        print(f"❌ Error during compilation: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print(f"🔄 Compiling {po_file} to {mo_file}...")
    success = compile_po_to_mo(po_file, mo_file)
    if not success:
        sys.exit(1)
