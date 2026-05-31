# debug_structure.py
import os
import importlib.util

print("=" * 50)
print("🔍 Checking project structure")
print("=" * 50)

# List of Python files in root
py_files = [f for f in os.listdir('.') if f.endswith('.py')]
print(f"\n📄 Available .py files: {py_files}")

# Check each file
for file in py_files:
    module_name = file[:-3]  # Remove .py
    try:
        spec = importlib.util.spec_from_file_location(module_name, file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Check for common Flask variables
        flask_vars = ['app', 'application', 'flask_app']
        found = [var for var in flask_vars if hasattr(module, var)]
        
        if found:
            print(f"\n✅ File {file}:")
            print(f"   Variables found: {found}")
            
            # Check variable type
            for var in found:
                obj = getattr(module, var)
                print(f"   {var} type: {type(obj).__name__}")
                
    except Exception as e:
        print(f"\n❌ File {file}: Error - {e}")

print("\n" + "=" * 50)
