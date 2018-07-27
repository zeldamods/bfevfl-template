#!/usr/bin/env python3

from pathlib import Path
import re

Path('../bfevfl_processed').mkdir(exist_ok=True)

# POINTER<pointed_type, pointer_type> name;
# POINTER<pointed_type> name;
simple_pointer_with_param_regex = re.compile(r"POINTER<(.*)\((.*)\)> (\w+)(\s?<.*>)?;")
simple_pointer_to_array_regex = re.compile(r"POINTER<(.*)\[(.*)\]> (\w+)(\s?<.*>)?;")
simple_pointer_regex = re.compile(r"POINTER<(.*)> (\w+)(\s?<.*>)?;")
pointer_regex = re.compile(r"POINTER<(.*), (.*)> (\w+)(\s?<.*>)?;")
for file_path in Path('.').glob('*.bt'):
    with file_path.open('r') as f, Path('../bfevfl_processed/' + file_path.name).open('w') as processed_f:
        for line_num, line in enumerate(f):
            var_name = f'temp_LINE_{line_num}_pos'
            def generate_repl(pointed_type, array, pointer_type, name, options):
                return f'{pointer_type} {name}_offset <format=hex, hidden=true>;' \
                       f'if ({name}_offset != 0) {{' \
                       f'const local uint64 {var_name} <hidden=true> = FTell();' \
                       f'FSeek({name}_offset);' \
                       f'{pointed_type} {name}{array}{options};' \
                       f'FSeek({var_name});' \
                       f'}}'

            new_line = line
            new_line = simple_pointer_with_param_regex.sub(generate_repl('\\1', '(\\2)', 'uint64', '\\3', '\\4'), new_line)
            new_line = simple_pointer_to_array_regex.sub(generate_repl('\\1', '[\\2]', 'uint64', '\\3', '\\4'), new_line)
            new_line = pointer_regex.sub(generate_repl('\\1', '', '\\2', '\\3', '\\4'), new_line)
            new_line = simple_pointer_regex.sub(generate_repl('\\1', '', 'uint64', '\\2', '\\3'), new_line)
            processed_f.write(new_line)
