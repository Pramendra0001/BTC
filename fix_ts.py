import os
import glob
import re

BASE_DIR = r"c:\Users\PRAMENDRA KUSHWAHA\Desktop\CODING\SIH 2026\BTC\frontend\src"

# Create global.d.ts
with open(os.path.join(BASE_DIR, "global.d.ts"), "w") as f:
    f.write("declare module 'react-cytoscapejs';\n")

# Remove unused imports
for filepath in glob.glob(os.path.join(BASE_DIR, "**", "*.tsx"), recursive=True):
    with open(filepath, "r") as f:
        content = f.read()
    
    # Remove `import React from 'react';`
    content = re.sub(r"import React from 'react';\n", "", content)
    
    # Replace Settings, Globe, etc in AppLayout if needed (Actually, Globe is used, Settings is not)
    if "AppLayout.tsx" in filepath:
        content = content.replace("Settings, ", "")
    
    # Replace Activity in DashboardPage
    if "DashboardPage.tsx" in filepath:
        content = content.replace(", Activity ", " ")

    with open(filepath, "w") as f:
        f.write(content)

# Fix format.ts
format_ts = os.path.join(BASE_DIR, "utils", "format.ts")
with open(format_ts, "r") as f:
    content = f.read()

content = content.replace("export const getEntityTypeIcon = (type: string) => null;", "export const getEntityTypeIcon = (_type: string) => null;")
with open(format_ts, "w") as f:
    f.write(content)

print("Fixed TS errors.")
