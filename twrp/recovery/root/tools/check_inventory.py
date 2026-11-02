#!/usr/bin/env python3

import os
import re
import sys

def main():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    readme_path = os.path.join(root_dir, 'README.md')

    if not os.path.exists(readme_path):
        print(f"Error: {readme_path} not found.")
        sys.exit(1)

    with open(readme_path, 'r') as f:
        readme_text = f.read()

    expected_files = set()

    # The prompt mentions:
    # "compare against the inventory the README declares (the original 18 files ... plus the follow-up libraries named in its DONE notes ... )"

    # 1. 18 files from the main inventory section
    match = re.search(r'# Key facts the inventory settled[^:]*:(.*?)(?:#   Also confirm)', readme_text, re.DOTALL)
    if match:
        block = match.group(1)
        paths = re.findall(r'#\s+(/[\w\.\-@/]+)', block)
        for p in paths:
            expected_files.add(p.split('/')[-1])

    # 2. 7 files FOLLOW-UP (small)
    match = re.search(r'# FOLLOW-UP \(small\):(.*?)# DONE[^:]*: all 7 pulled', readme_text, re.DOTALL)
    if match:
        block = match.group(1)
        for m in re.findall(r'[\w\.\-@]+\.so', block):
            expected_files.add(m)

    # 3. 4 files readelf on THEM
    match = re.search(r'readelf on THEM shows one more layer(.*?)# DONE[^:]*: all 4 pulled', readme_text, re.DOTALL)
    if match:
        block = match.group(1)
        for m in re.findall(r'[\w\.\-@]+\.so', block):
            expected_files.add(m)

    if not expected_files:
        print("Error: Could not parse expected files from README.md")
        sys.exit(1)

    actual_files = set()

    # Walk the recovery root and list every regular file
    for r, dirs, files in os.walk(root_dir):
        if os.path.basename(r) == 'tools':
            continue
        for f in files:
            actual_files.add(f)

    missing_files = expected_files - actual_files
    present_files = expected_files & actual_files
    not_in_readme = actual_files - expected_files

    # As per prompt, report files as present / missing / not-in-README

    print("--- INVENTORY CHECK ---")
    print(f"Present files: {len(present_files)}")
    for f in sorted(present_files):
        print(f"  {f}")

    print(f"\nNot in README: {len(not_in_readme)}")
    for f in sorted(not_in_readme):
        print(f"  {f}")

    has_errors = False

    print(f"\nMissing files: {len(missing_files)}")
    for f in sorted(missing_files):
        print(f"  {f}")
    if missing_files:
        has_errors = True

    print("\n--- .RC SERVICE REFERENCE CHECK ---")
    vendor_etc_init = os.path.join(root_dir, 'vendor', 'etc', 'init')
    if os.path.exists(vendor_etc_init):
        for root, _, files in os.walk(vendor_etc_init):
            for f in files:
                if f.endswith('.rc'):
                    rc_path = os.path.join(root, f)
                    with open(rc_path, 'r') as rc_file:
                        for line_num, line in enumerate(rc_file, 1):
                            line = line.strip()
                            if line.startswith('service '):
                                parts = line.split()
                                if len(parts) >= 3:
                                    service_name = parts[1]
                                    bin_path = parts[2]
                                    relative_bin = bin_path.lstrip('/')
                                    full_bin_path = os.path.join(root_dir, relative_bin)

                                    if not os.path.isfile(full_bin_path):
                                        print(f"DANGLING REFERENCE in {f}:{line_num}:")
                                        print(f"  Service '{service_name}' points to '{bin_path}' which does not exist in recovery root.")
                                        has_errors = True
                                    else:
                                        print(f"OK: {f} -> {bin_path}")

    if has_errors:
        print("\nCheck failed: Missing files or dangling references found.")
        sys.exit(1)
    else:
        print("\nCheck passed successfully.")
        sys.exit(0)

if __name__ == '__main__':
    main()
