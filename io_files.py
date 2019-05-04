import pydicom
import fnmatch
import json
import numpy as np
from os import path, walk, makedirs, stat



def simple_read_json(name, _path):
    _filename = path.join(_path, name)
    with open(_filename, 'r', encoding='utf-8') as file:
        result = json.load(file)
    return result

# Счтитываем образец JSON
def read_json_template(_filename):
    with open(_filename, 'r', encoding='utf-8') as file:
        _dict = json.load(file)
    return _dict


# Чтение ключевых слов
def read_keywords(root):
    filename = root + '.txt'
    if path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as file:
            return file.readline().split(',')
    else:
        return ""


# Запись словаря в файловую систему
def save_to_file(input_dict, _path, name):
    # Имя JSON файла
    if '.json' in name:
        json_name = name
        name_dir = name.split('.')[0].replace('series', '')
    else:
        name_dir = name
        json_name = 'series' + name + '.json'

    # Подготовка дирректорий
    dirs = {'main': str(_path),
            'oldData': str(_path) + str(name_dir) + '/oldData',
            'newData': str(_path) + str(name_dir) + '/newData',
            'Ellipse': str(_path) + str(name_dir) + '/Ellipse',
            'Contour': str(_path) + str(name_dir) + '/Contour',
            }
    for item in dirs.keys():
        try:
            stat(dirs[item])
        except FileNotFoundError:
            makedirs(dirs[item])

    for img in input_dict['Data']:
        _npy = str(img['Number']) + '.npy'

        np.save(path.join(dirs['oldData'], _npy), img['oldData'])
        img['oldData'] = path.join(dirs['oldData'], _npy)
        np.save(path.join(dirs['newData'], _npy), img['newData'])
        img['newData'] = path.join(dirs['newData'], _npy)
        np.save(path.join(dirs['Ellipse'], _npy), img['Ellipse']['XY'])
        img['Ellipse']['XY'] = path.join(dirs['Ellipse'], _npy)
        np.save(path.join(dirs['Contour'], _npy), img['Contour'])
        img['Contour'] = path.join(dirs['Contour'], _npy)

    filename = path.join(dirs['main'], json_name)
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(input_dict, file)


# Запись словаря в файловую систему
def load_from_files(name, _path):
    if '..' in _path:
        beg = 0
    else:
        beg = 1
    # Имя JSON файла
    if '.json' not in name:
        name = 'series' + name + '.json'

    _filename = path.join(_path, name)
    with open(_filename, 'r', encoding='utf-8') as file:
        result = json.load(file)

    for img in result['Data']:
        img.update({'oldData': np.load(str(img['oldData'])[beg:])})
        img.update({'newData': np.load(img['newData'][beg:])})
        img.update({'Contour': np.load(img['Contour'][beg:])})
        img['Ellipse']['XY'] = np.load(img['Ellipse']['XY'][beg:])
    return result


# Получаем все файлы из указанной дирректории
# Если my_path не указана, то берутся файлы из директории TEST_DATA
def get_tree_files(my_path, ext='*.dcm', level_down=False):
    if not path.exists(my_path):
        raise FileNotFoundError("Указанный путь не существует!")
    tree = {}
    for root, dirs, filenames in walk(my_path):
        if level_down:
            if root == my_path:
                continue
        tree.update({root: fnmatch.filter(filenames, ext)})
    return tree


# Переопределяем массив снимков
def sorted_images(arr_pixdata):
    new_arr_dict = []
    arr_dist = sorted([el['Location'] for el in arr_pixdata])
    for i in arr_dist:
        for el in arr_pixdata:
            if el['Location'] == i:
                new_arr_dict.append(el)
                break
    return new_arr_dict


# Импортируем серию в словарь (удобно хранить)
def form_dicom_to_dict(_path, di_files, tmp_dir):
    series = read_json_template(tmp_dir)
    series['Key'] = read_keywords(_path)
    fl_for_info = pydicom.dcmread(path.join(_path, di_files[0]))
    pixel_data = []
    for el in fl_for_info:
        if el.name in series:
            series[el.name] = str(el.value)
    for name in di_files:
        _filename = path.join(_path, name)
        scan = pydicom.dcmread(_filename)
        pixel_data.append(
            {
                'Number': scan[0x20, 0x13].value,
                'Location': scan[0x20, 0x1041].value,
                'oldData': scan.pixel_array,
                'newData': [],
                'Contour': [],
                'Ellipse': {
                    'XY': [],
                    'Xc': 0,
                    'Yc': 0,
                    'a': 0,
                    'b': 0,
                    'theta': 0,
                    'dev': 0
                }
            })
    series['Data'] = sorted_images(pixel_data)
    return series

