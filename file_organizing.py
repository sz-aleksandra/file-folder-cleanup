import json
import argparse
import os
import shutil
import hashlib

def read_config(filepath):
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except:
        print("Configuration file doesn't exist. Creating default configuration file...")
        default_config = {
    		"file_attributes": "rw-r--r--",
    		"troublesome_characters": ":\".;*?$#`|\\",
    		"character_substitute": "_",
    		"temporary_file_extensions": "*˜, *.tmp"
		}
        with open(filepath, 'w') as f:
            json.dump(default_config, f, indent=4)
        return default_config

def parse_config(config):
    file_attributes = config["file_attributes"]
    troublesome_characters = [char for char in config["troublesome_characters"]]
    character_substitute = config["character_substitute"]
    temporary_file_extensions = config["temporary_file_extensions"].split(',')

    standardized_file_attributes = ""
    for group in (file_attributes[i:i+3] for i in range(0, len(file_attributes), 3)):
        attribute_sum = 0
        for char in group:
            if char == "r":
                attribute_sum += 4
            elif char == "w":
                attribute_sum += 2
            elif char == "x":
                attribute_sum += 1
        standardized_file_attributes += str(attribute_sum)
    file_attributes = int(standardized_file_attributes, 8)

    return file_attributes, troublesome_characters, character_substitute, temporary_file_extensions

def parse_command_line_arguments():
    parser = argparse.ArgumentParser(description="Organize and tidy up files in directories.")
    
    parser.add_argument("configuration", help="Choose configuration file")
    parser.add_argument("main_directory", help="Choose main directory")
    parser.add_argument("directories", help="Choose other directories to include", nargs="+")
    parser.add_argument("--move_or_copy", choices=["do_nothing", "move", "copy"], default="do_nothing", help="Decide to move or copy files from other directories to main", required=False)
    parser.add_argument('--identical', choices=["do_nothing", "ask", "apply_to_all"], default="do_nothing", help='Find files with identical content', required=False)
    parser.add_argument('--empty', choices=["do_nothing", "ask", "apply_to_all"], default="do_nothing", help='Find empty files', required=False)
    parser.add_argument('--samename', choices=["do_nothing", "ask", "apply_to_all"], default="do_nothing", help='Find files with identical content', required=False)
    parser.add_argument('--temporary', choices=["do_nothing", "ask", "apply_to_all"], default="do_nothing", help='Find files with identical content', required=False)
    parser.add_argument('--unusual_attributes', choices=["do_nothing", "ask", "apply_to_all"], default="do_nothing", help='Find files with identical content', required=False)
    parser.add_argument('--troublesome_characters', choices=["do_nothing", "ask", "apply_to_all"], default="do_nothing", help='Find files with identical content', required=False)

    return parser.parse_args()

def choose_action(options):
    while True:
        choice = input(f"{options} ({'Y/n'}): ").lower()
        if choice in ("y", "yes"):
            return True
        if choice in ("n", "no"):
            return False
        
def move_to_main(main_directory, other_directories):
    for directory in other_directories:
        for root, _, files in os.walk(directory):
            for file in files:
                source_path = os.path.join(root, file)
                target_path = os.path.join(main_directory, file)
                print(f"Moving {source_path} to {target_path}")
                shutil.move(source_path, target_path)

def copy_to_main(main_directory, other_directories):
    for directory in other_directories:
        for root, _, files in os.walk(directory):
            for file in files:
                source_path = os.path.join(root, file)
                target_path = os.path.join(main_directory, file)
                print(f"Copying {source_path} to {target_path}")
                shutil.copy(source_path, target_path)

def leave_old_identical(main_directory, other_directories, apply_to_all=False):
    directories = [main_directory] + other_directories
    file_hash_map = {}
    for directory in directories:
        for root, _, files in os.walk(directory):
            for file in files:
                filepath = os.path.join(root, file)
                with open(filepath, 'rb') as f:
                    file_hash = hashlib.md5(f.read()).hexdigest()
                file_mtime = os.path.getmtime(filepath)
                if file_hash in file_hash_map:
                    old_filepath, old_mtime = file_hash_map[file_hash]
                    if file_mtime < old_mtime:
                        if not apply_to_all:
                            if choose_action(f"Delete newer file {old_filepath}?"):
                                print(f"Leaving older file: {filepath}, deleting: {old_filepath}")
                                os.remove(old_filepath)
                        else:
                            print(f"Leaving older file: {filepath}, deleting: {old_filepath}")
                            os.remove(old_filepath)
                    else:
                        file_hash_map[file_hash] = (filepath, file_mtime)
                        if not apply_to_all:
                            if choose_action(f"Delete newer file {filepath}?"):
                                print(f"Leaving older file: {old_filepath}, deleting: {filepath}")
                                os.remove(filepath)
                        else:
                            print(f"Leaving older file: {old_filepath}, deleting: {filepath}")
                            os.remove(filepath)
                else:
                    file_hash_map[file_hash] = (filepath, file_mtime)

def leave_new_samename(main_directory, other_directories, apply_to_all=False):
    directories = [main_directory] + other_directories
    file_name_map = {}
    for directory in directories:
        for root, _, files in os.walk(directory):
            for file in files:
                filepath = os.path.join(root, file)
                file_mtime = os.path.getmtime(filepath)
                if file in file_name_map:
                    old_filepath, old_mtime = file_name_map[file]
                    if file_mtime > old_mtime:
                        if not apply_to_all:
                            if choose_action(f"Delete older file {old_filepath}?"):
                                print(f"Leaving newer file: {filepath}, deleting: {old_filepath}")
                                os.remove(old_filepath)
                        else:
                            print(f"Leaving newer file: {filepath}, deleting: {old_filepath}")
                            os.remove(old_filepath)
                    else:
                        if not apply_to_all:
                            if choose_action(f"Delete older file {filepath}?"):
                                print(f"Leaving newer file: {old_filepath}, deleting: {filepath}")
                                os.remove(filepath)
                        else:
                            print(f"Leaving newer file: {old_filepath}, deleting: {filepath}")
                            os.remove(filepath)
                else:
                    file_name_map[file] = (filepath, file_mtime)

def delete_empty(main_directory, other_directories, apply_to_all=False):
    directories = [main_directory] + other_directories
    for directory in directories:
        for root, _, files in os.walk(directory):
            for file in files:
                filepath = os.path.join(root, file)
                if os.path.isfile(filepath) and os.path.getsize(filepath) == 0:
                    if not apply_to_all:
                        if choose_action(f"Delete empty file {filepath}?"):
                            print(f"Deleting empty file: {filepath}")
                            os.remove(filepath)
                    else:
                        print(f"Deleting empty file: {filepath}")
                        os.remove(filepath)

def delete_temporary(main_directory, other_directories, temporary_files_extensions, apply_to_all=False):
    directories = [main_directory] + other_directories
    for directory in directories:
        for root, _, files in os.walk(directory):
            for file in files:
                if any(file.endswith(ext.strip().lstrip("*")) for ext in temporary_files_extensions):
                    filepath = os.path.join(root, file)
                    if not apply_to_all:
                        if choose_action(f"Delete temporary file {filepath}?"):
                            os.remove(filepath)
                    else:
                        os.remove(filepath)

def change_unusual_attributes(main_directory, other_directories, file_attributes, apply_to_all=False):
    directories = [main_directory] + other_directories
    for directory in directories:
        for root, _, files in os.walk(directory):
            for file in files:
                filepath = os.path.join(root, file)
                if os.path.isfile(filepath):
                    current_attributes = oct(os.stat(filepath).st_mode)[-3:]
                    required_attributes = oct(file_attributes)[-3:]
                    if current_attributes != required_attributes:
                        if not apply_to_all:
                            if choose_action(f"Change attributes for: {filepath}?"):
                                print(f"Changing attributes for: {filepath} to {oct(file_attributes)}")
                                os.chmod(filepath, file_attributes)
                        else:
                            print(f"Changing attributes for: {filepath} to {oct(file_attributes)}")
                            os.chmod(filepath, file_attributes)

def change_troublesome_characters(main_directory, other_directories, troublesome_characters, character_substitute, apply_to_all=False):
    directories = [main_directory] + other_directories
    for directory in directories:
        for root, _, files in os.walk(directory):
            for file in files:
                name, extension = os.path.splitext(file)
                if any(char in name for char in troublesome_characters):
                    if not apply_to_all:
                        old_path = os.path.join(root, file)
                        new_name = ''.join(character_substitute if char in troublesome_characters else char for char in name)
                        new_path = os.path.join(root, new_name + extension)
                        if choose_action(f"Rename {old_path}?"):
                            print(f"Renaming {old_path} to {new_path}")
                            os.rename(old_path, new_path)
                    else:
                        print(f"Renaming {old_path} to {new_path}")
                        os.rename(old_path, new_path)

def main():
    args = parse_command_line_arguments()

    main_directory = args.main_directory
    other_directories = args.directories
    configuration = args.configuration

    config = read_config(configuration)
    file_attributes, troublesome_characters, character_substitute, temporary_file_extensions = parse_config(config)

    if args.move_or_copy == 'move':
        move_to_main(main_directory, other_directories)
    if args.move_or_copy == 'copy':
        copy_to_main(main_directory, other_directories)
    if args.identical != 'do_nothing':
        leave_old_identical(main_directory, other_directories, args.empty == 'apply_to_all')
    if args.empty != 'do_nothing':
        delete_empty(main_directory, other_directories, args.empty == 'apply_to_all')
    if args.samename != 'do_nothing':
        leave_new_samename(main_directory, other_directories, args.empty == 'apply_to_all')
    if args.temporary != 'do_nothing':
        delete_temporary(main_directory, other_directories, temporary_file_extensions, args.empty == 'apply_to_all')
    if args.unusual_attributes != 'do_nothing':
        change_unusual_attributes(main_directory, other_directories, file_attributes, args.empty == 'apply_to_all')
    if args.troublesome_characters != 'do_nothing':
        change_troublesome_characters(main_directory, other_directories, troublesome_characters, character_substitute, args.empty == 'apply_to_all')

if __name__ == "__main__":
    main()
