# validate\_metadata\_files.py (YAML version)

# ------------------------------------------

# Purpose:

# Check that all metadata YAML files in prompts/03-metadata/ contain required fields.

# Goals:

# - Ensure presence of required keys in production-ready metadata

# - Prevent broken registry entries or prompt mismatches

# Use Cases:

# - Used in CI to validate YAML completeness before deployment

import os
import yaml

REQUIRED\_KEYS = \[
"description",
"production\_prompt",
"metadata\_file",
"current\_version\_prod",
"current\_version\_dev"
]

# Validate a single YAML metadata file

# -------------------------------------

def validate\_metadata\_file(file\_path):
with open(file\_path, "r", encoding="utf-8") as f:
data = yaml.safe\_load(f)
for key in REQUIRED\_KEYS:
if key not in data:
print(f"❌ Missing '{key}' in {file\_path}")
return False
return True

# Validate all .yaml files in prompts/03-metadata/

# -------------------------------------------------

def main():
directory = os.path.join("prompts", "03-metadata")
all\_passed = True
for filename in os.listdir(directory):
if filename.endswith(".yaml"):
path = os.path.join(directory, filename)
if not validate\_metadata\_file(path):
all\_passed = False
if all\_passed:
print("✅ All metadata YAML files valid.")
else:
print("❌ Metadata validation failed.")

if **name** == "**main**":
main()
