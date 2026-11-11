import os
import glob

print("Checking codebase for ['status'] or potential key errors...")
for root, dirs, files in os.walk('.'):
    if 'build' in root or 'dist' in root or '.git' in root or '__pycache__' in root:
        continue
    for f in files:
        if f.endswith('.py'):
            p = os.path.join(root, f)
            with open(p, 'r', encoding='utf-8', errors='ignore') as fp:
                lines = fp.readlines()
            for idx, line in enumerate(lines):
                if "['status']" in line:
                    print(f"{p}:{idx+1} -> {line.strip()}")
