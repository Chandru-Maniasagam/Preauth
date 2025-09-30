#!/usr/bin/env python3
"""
Check Flask routes
"""

from app.main import app

print("Flask Routes:")
print("=" * 50)
for rule in app.url_map.iter_rules():
    print(f"  {rule.rule} -> {rule.endpoint}")
    print(f"    Methods: {rule.methods}")
    print()

print(f"Total routes: {len(list(app.url_map.iter_rules()))}")
