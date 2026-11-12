import os
import re

errors_found = []
for root, dirs, files in os.walk('ui'):
    for f in files:
        if f.endswith('.py'):
            p = os.path.join(root, f)
            with open(p, 'r', encoding='utf-8', errors='ignore') as fp:
                txt = fp.read()
                # Check for float font size
                float_fonts = re.findall(r'CTkFont\([^)]*size\s*=\s*\d+\.\d+', txt)
                if float_fonts:
                    errors_found.append((p, 'Float font size', float_fonts))
                # Check for border_color="transparent"
                trans_borders = re.findall(r'border_color\s*=\s*[\"\']transparent[\"\']', txt)
                if trans_borders:
                    errors_found.append((p, 'transparent border_color', trans_borders))

print('Scan complete!')
if not errors_found:
    print('ZERO float fonts and ZERO transparent borders found across entire ui directory!')
else:
    for e in errors_found:
        print('ISSUE:', e)
