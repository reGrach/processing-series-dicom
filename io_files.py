import pydicom
import fnmatch
import json
import numpy as np
import os
from os import path, walk


# Счтитываем образец JSON
def read_json_template(_filename):
    with open(_filename, 'r', encoding='utf-8') as file:
        _dict = json.load(file)
    return _dict


def write_to_json(_filename):
    with open(_filename, 'r', encoding='utf-8') as file:
        _dict = json.load(file)
    return _dict


def read_keywords(root):
    filename = root + '.txt'
    if path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as file:
            return file.readline().split(',')
    else:
        return ""


# Запись словаря в json файл
def to_file_json(input_dict, _path=None, name=None):
    if name is None:
        name = 'series' + str(input_dict['Study ID']) + ".json"
    else:
        name = 'series' + name + '.json'
    filename = ''
    for img in input_dict['Data']:
        if isinstance(img['oldData'], np.ndarray):
            img['oldData'] = img['oldData'].tolist()
        if isinstance(img['newData'], np.ndarray):
            img['newData'] = img['newData'].tolist()
        if isinstance(img['Ellipse']['XY'], np.ndarray):
            img['Ellipse']['XY'] = img['Ellipse']['XY'].tolist()
        if isinstance(img['Contour'], np.ndarray):
            img['Contour'] = img['Contour'].tolist()
    if _path:
        filename = str(_path) + '/'
        try:
            os.stat(_path)
        except FileNotFoundError:
            os.makedirs(_path)
    filename += name
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(input_dict, file)


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


# Чтение данных из файла JSON
def from_file_json(_filename):
    with open(_filename, 'r', encoding='utf-8') as file:
        series = json.load(file)
    for img in series['Data']:
        img['oldData'] = np.array(img['oldData'])
        img['newData'] = np.array(img['newData'])
        img['Ellipse']['XY'] = np.array(img['Ellipse']['XY'])
        img['Contour'] = np.array(img['Contour'])
    return series


# Импортируем серию в словарь (удобно хранить, меньше памяти занимает)
def form_dicom_to_dict(_path, di_files, tmp, path_wrt=None):
    series = tmp.copy()
    series['Key'] = read_keywords(_path)
    fl_for_info = pydicom.dcmread(path.join(_path, di_files[0]))
    pixel_data = []
    for el in fl_for_info:
        if el.name in series:
            series[el.name] = el.value
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
    if path_wrt is not None:
        to_file_json(series, path_wrt, name=path.split(_path)[-1])
    return series

