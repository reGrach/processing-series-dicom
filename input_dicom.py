import pydicom
import fnmatch
from os import path, walk

TEST_DATA = "../data/example"


# Получаем все файлы из указанной дирректории
# Если my_path не указана, то берутся файлы из директории TEST_DATA
def get_files(my_path=None, level_down=False):
    outer_dir = path.dirname(path.dirname(__file__))
    if my_path:
        if path.isabs(my_path):
            data_path = my_path
        else:
            data_path = path.join(outer_dir, 'data/' + my_path)
            if not path.isdir(data_path):
                print("Путь должен быть либо абсолютным, либо быть продолжением директории 'data'")
                return
    else:
        data_path = path.join(outer_dir, TEST_DATA)

    files = []
    for root, dirs, filenames in walk(data_path):
        for file in filenames:
            filename_filter1 = fnmatch.filter([path.join(root, file)], "*.dcm")
            if filename_filter1:
                files.append(path.join(root, file))
        if not level_down:
            break
    return files


# Переопределяем массив снимков
def sorted_images(arr_dict):
    new_arr_dict = []
    arr_dist = sorted([el['Location'] for el in arr_dict])
    for i in arr_dist:
        for el in arr_dict:
            if el['Location'] == i:
                new_arr_dict.append(el)
                break
    return new_arr_dict


# Импортируем серию в словарь (удобно хранить, меньше памяти занимает)
def create_dictionary(files=None):
    imagesAX = []
    imagesES = []
    series = {}
    if not files:
        files = get_files()

    for file in files:
        scan = pydicom.dcmread(file)
        if 'AXIAL' in scan[0x08, 0x08].value:
            imagesAX.append(
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
                }
            )
        elif 'LOCALIZER' in scan[0x08, 0x08].value:
            imagesES.append(
                {
                    'Number': scan[0x20, 0x13].value,
                    'Location': scan[0x20, 0x1041].value,
                    'Data': scan.pixel_array
                }
            )
        else:
            series.update(
                {
                    'CreationDate': scan[0x08, 0x2a].value.split('+')[0],
                    'Description': scan[0x08, 0x1030].value,
                    'SOP_Class': scan[0x08, 0x16].value,
                    'ImagesParameter': {
                        'PhotometricInterpretation': scan[0x28, 0x04].value,
                        'SizeImages': [scan[0x28, 0x10].value, scan[0x28, 0x11].value]
                    }
                }
            )
    series.update({'ImagesAxial': sorted_images(imagesAX), 'ImagesEs': imagesES})
    return series
