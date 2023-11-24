import os
import shutil
import sys
from pathlib import Path

CYRILLIC_SYMBOLS = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ"
TRANSLATION = ("a", "b", "v", "g", "d", "e", "e", "j", "z", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u", "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu", "ya", "je", "i", "ji", "g")

TRANS = {}

for c, l in zip(CYRILLIC_SYMBOLS, TRANSLATION):
    TRANS[ord(c)] = l
    TRANS[ord(c.upper())] = l.upper()


folders = {
    'images': ('.jpeg', '.png', '.jpg', '.svg'),
    'video': ('.avi', '.mp4', '.mov', '.mkv'),
    'documents': ('.doc', '.docx', '.txt', '.pdf', '.xlsx', '.pptx'),
    'audio': ('.mp3', '.ogg', '.wav', '.amr'),
    'archives': ('.zip', '.gz', '.tar'),
    'unknown': set(),
}

categorized_files = {'images': [], 'audio': [], 'video': [], 'documents': [], 'archives': [], 'unknown': []}

known_extensions = set()


def is_directory(path):
    if len(sys.argv) != 2:
        return False
    else:
        try:
            if os.path.exists(path):
                print(f'{path} exists!')
                if path.is_dir():
                    print(f'{path} is a directory')
                    return True
                else:
                    print(f'{path} is not a directory')
                    return False
            else:
                print(f'{path} is not exist!')
        except Exception as e:
            print(f'An error occurred: {e}')
    return False


def normalize(str):
    new_name = ''
    for char in str:
        if char.isalnum():
            new_name += char.translate(TRANS)
        else:
            new_name += '_'
    return new_name


def move_files(source, destination):
    for root, dirs, files in os.walk(source):

        for name in folders.keys():
            if name in dirs:
                dirs.remove(name)

        for file in files:
            source_path = os.path.join(root, file)
            destination_path = os.path.join(destination, file)
            shutil.move(source_path, destination_path)

        for dir in dirs:
            full_dir_path = os.path.join(root, dir)
            move_files(full_dir_path, destination)
            try:
                os.rmdir(full_dir_path)
            except OSError as e:
                print(f"Failed to remove directory {full_dir_path}: {e}")


def sort(path):
    for root, dirs, files in os.walk(path):
        for name in folders.keys():
            if name in dirs:
                dirs.remove(name)
        for file in files:

            file_root, file_extension = os.path.splitext(file)

            if any(char.isupper for char in file_extension):
                file_extension_edited = file_extension.lower()
            else:
                file_extension_edited = file_extension

            normalized_file_root = normalize(file_root)
            new_file_name = f'{normalized_file_root}{file_extension}'

            is_unknown = False

            for folder, extencions in folders.items():
                if folder == 'unknown':
                    folders[folder].add(file_extension_edited)

                if file_extension_edited in extencions:
                    if folder == 'archives':
                        try:
                            shutil.unpack_archive(file, f'{normalized_file_root}')
                            os.remove(file)
                            file = normalized_file_root
                        except shutil.ReadError as e:
                            print(f"Error: {e}")

                    if not is_unknown:
                        known_extensions.add(file_extension_edited)

                    categorized_files[folder].append(new_file_name)
                    shutil.move(os.path.join(root, file), os.path.join(os.path.join(root, folder), new_file_name))
                    break


if __name__ == '__main__':
    path = Path(sys.argv[1])
    flag = is_directory(path)
    if not flag:
        sys.exit(1)

    os.chdir(path)

    move_files(path, path)

    for name in folders.keys():
        if not os.path.exists(name):
            os.mkdir(name)

    sort(path)

    for type, files in categorized_files.items():
        print(f'Список файлів в категорії {type}: {files}')

    print(f'Перелік усіх відомих скрипту розширень, які зустрічаються в цільовій папці: {known_extensions}')
    print(f'Перелік всіх розширень, які скрипту невідомі: {folders["unknown"]}')