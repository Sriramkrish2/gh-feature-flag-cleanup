#!/usr/bin/env python3

import sys
import re

def is_test_file(filename):
    return 'test' in filename.lower() or filename.lower().endswith(('_spec.py', '_test.py', '_spec.js', '_test.js', 'test.java'))

def process_file(lines, flag):
    """
    Removes usage of the feature flag, preserving the rest of the logic where possible.
    For 'if <flag>:' or 'if (<flag>)' or similar, keeps the 'else' branch if present, otherwise removes the check and keeps the body.
    """
    output = []
    skip = False
    indent_stack = []
    i = 0
    while i < len(lines):
        line = lines[i]
        # Detect if/elif/else/switch/case with flag
        flag_if = re.search(rf'\bif\b.*\b{re.escape(flag)}\b', line)
        flag_elif = re.search(rf'\belif\b.*\b{re.escape(flag)}\b', line)
        flag_else = re.search(r'^\s*else\b', line)
        flag_switch = re.search(rf'\bswitch\b.*\b{re.escape(flag)}\b', line)
        flag_case = re.search(rf'\bcase\b.*\b{re.escape(flag)}\b', line)
        flag_in_line = flag in line

        # Handle if/elif with flag
        if flag_if or flag_elif or flag_switch or flag_case:
            # Try to find corresponding else block
            indent = len(line) - len(line.lstrip())
            j = i + 1
            found_else = False
            else_start = None
            # Find else at same indentation
            while j < len(lines):
                next_line = lines[j]
                next_indent = len(next_line) - len(next_line.lstrip())
                if re.match(r'^\s*else\b', next_line) and next_indent == indent:
                    found_else = True
                    else_start = j
                    break
                # End block if indentation decreases
                if next_indent < indent and next_line.strip():
                    break
                j += 1
            if found_else:
                # Keep the else block, skip the if block
                # Find end of else block
                k = else_start + 1
                else_indent = len(lines[else_start]) - len(lines[else_start].lstrip())
                while k < len(lines):
                    curr_indent = len(lines[k]) - len(lines[k].lstrip())
                    if curr_indent <= else_indent and lines[k].strip():
                        break
                    output.append(lines[k])
                    k += 1
                i = k
            else:
                # No else: remove the if/elif line, but keep the body
                i += 1
                while i < len(lines):
                    curr_line = lines[i]
                    curr_indent = len(curr_line) - len(curr_line.lstrip())
                    if curr_indent <= indent and curr_line.strip():
                        break
                    output.append(curr_line)
                    i += 1
        elif is_test_file(sys.argv[1]) and flag_in_line:
            # For test files, comment out lines with the flag
            output.append("# [flag cleanup] " + line)
            i += 1
        elif flag_in_line:
            # Remove lines with the flag reference
            i += 1
        else:
            output.append(line)
            i += 1
    return output

def main():
    if len(sys.argv) < 3:
        print("Usage: cleanup_agent.py <file> <flag>")
        sys.exit(1)

    file = sys.argv[1]
    flag = sys.argv[2]

    with open(file, "r") as f:
        lines = f.readlines()

    new_lines = process_file(lines, flag)

    with open(file, "w") as f:
        f.writelines(new_lines)

if __name__ == "__main__":
    main()
