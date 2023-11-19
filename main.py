# -*- coding: utf-8 -*-
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
}

categorized_files = {'images': [], 'audio': [], 'video': [], 'documents': [], 'archives': [], 'unknown': []}

known_extensions = set()
unknown_extensions = set()


def is_directory(path):
    if len(sys.argv) != 2:
        return False
    else:
        try:
            if path.is_dir():
                print(str(path) + 'is a directory.')
                return True
            else:
                print(str(path) + 'is not a directory or path is incorrect.')
        except Exception as e:
            print('An error occurred:' + str(e))
    return False


def normalize(str):
    new_name = ''
    for char in str:
        if char.isalnum():
            new_name += char.translate(TRANS)
        else:
            new_name += '_'
    return new_name


def sort(path):
    os.chdir(path)

    for name in folders.keys():
        if not os.path.exists(name):
            os.mkdir(name)

    for root, dirs, files in os.walk(path):
        if not 'images' in str(root) and not 'video' in str(root) and not 'documents' in str(root) and not 'audio' in str(root) and not 'archives' in str(root):
            for file in files:

                flag = True
                file_root, file_extension = os.path.splitext(file)

                for folder, extension in folders.items():
                    if file_extension in extension:
                        normalized_file_root = normalize(file_root)
                        new_file_name = '{}{}'.format(normalized_file_root, file_extension)
                        known_extensions.add(file_extension)
                        flag = False

                        if folder == 'archives':
                            is_unpacked = False
                            try:
                                shutil.unpack_archive(file, '{}'.format(normalized_file_root))
                                is_unpacked = True
                            except shutil.ReadError as e:
                                print('Error:' + str(e))
                            if is_unpacked:
                                categorized_files[folder].append(normalized_file_root)
                                shutil.move(normalized_file_root, os.path.join(folder, normalized_file_root))
                                os.remove(file)

                        else:
                            categorized_files[folder].append(new_file_name)
                            shutil.move(file, os.path.join(folder, new_file_name))

                if flag:
                    unknown_extensions.add(file_extension)
                    categorized_files['unknown'].append(file)

            for dir in dirs:
                if dir != 'images' and dir != 'video' and dir != 'archives' and dir != 'audio' and dir != 'documents':
                    try:
                        os.rmdir(dir)
                        print('Directory' + dir + 'has been removed successfully')
                    except OSError as error:
                        print('Directory' + dir + 'can not be removed')
                    if os.path.exists(dir):
                        normalized_dir = normalize(dir)
                        os.rename(dir, normalized_dir)
                        sort(os.path.join(root, normalized_dir))

            return os.chdir(os.path.dirname(root))



if __name__ == '__main__':
    path = Path(sys.argv[1])
    flag = is_directory(path)
    if not flag:
        sys.exit(1)

    sort(path)

    for type, files in categorized_files.items():
        print('Список файлів в категорії' + type + ': ' + str(files))

    print('Перелік усіх відомих скрипту розширень, які зустрічаються в цільовій папці: ' + str(known_extensions))
    print('Перелік всіх розширень, які скрипту невідомі: ' + str(unknown_extensions))