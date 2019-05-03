import core
import io_files
import imaging
import config
from os import path


# Обработка отдельного кадра
def processing_series(images):
    # Обработка каждого изображения
    for img in images:
        img['Contour'] = core.find_contour_brain(img['oldData'])  # Определяем границу мозга
        img['newData'] = core.delete_unnecessary_obj(img)  # Очищаем Data от объектов вне контура
        core.approximate_ellipse(img)  # Аппроксимация эллипсом
    med_ang = core.find_med_ang(images)  # Определение угла (в градусах) поворота всех срезов
    core.rotate_images(images, target_angle=med_ang)  # Поворот всех срезов на целевой угол


# Чтение dicom-файлов, обработка и запись их в формат JSON
def read_proc_write():
    template_dict = io_files.read_json_template(config.PATH_TEMPLATE_JSON)
    tree_files_di = io_files.get_tree_files(config.PATH_READ_DICOM, level_down=True)
    for root, item in tree_files_di.items():
        print(str.format('Начало  записи файла № {0}', path.split(root)[-1]))
        dict_series = io_files.form_dicom_to_dict(_path=root,
                                                  di_files=item,
                                                  tmp=template_dict)
        processing_series(dict_series['Data'])
        io_files.to_file_json(dict_series,
                              _path=config.PATH_DATA_JSON,
                              name=path.split(root)[-1])
        dict_series.clear()
        print(str.format('Завершена запись файла № {0}', path.split(root)[-1]))


# Считываем файл JOSN и сохраняем изображения
def read_json_save_img():
    tree_files_json = io_files.get_tree_files(config.PATH_DATA_JSON, ext='*.json')
    for root, item in tree_files_json.items():
        for file in item:
            print(str.format('Читаем файл {0}', file))
            path_read = path.join(root, file)
            path_write = path.join(config.PATH_DATA_IMG, file.split('.')[0])
            data = io_files.from_file_json(path_read)
            print(str.format('Записываем изображения из файла {0}', file))
            for img in data['Data']:
                title = img['Location']
                imaging.save_img(img['oldData'],
                                 _title=title,
                                 _path=path_write + '/old')
                imaging.save_img(img['newData'],
                                 _title=title,
                                 _path=path_write + '/new')


if __name__ == "__main__":
    print("Это пакет для обработки Dicom серий")
    # path_read = '../data/json/series1068.json'
    # ser = io_files.from_file_json(path_read)
    # print('Прочитал')
    # arr3d = []
    # # read_di = '../data/ready/1068/1.2.840.113704.1.111.5592.1473347038.20343.dcm'
    # # data = pydicom.dcmread(read_di).pixel_array
    # for img in ser['Data']:
    #     arr3d.append(img['oldData'])
    # print('3д-массив')
    # arr3d = np.array(arr3d)
    # new_arr3d = arr3d.transpose((1, 0, 2))
    # print('Транспонировал')
    # imaging.easy_show_image(arr3d)

