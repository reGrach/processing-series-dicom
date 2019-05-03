import core
import io_files
import config


# Обработка отдельного кадра
def processing_series(images):
    # Обработка каждого изображения
    for img in images:
        img.update({'Contour': core.find_contour_brain(img['oldData'])})
        img.update({'newData': core.delete_unnecessary_obj(img)})
        img.update({'Ellipse': core.approximate_ellipse(img['Contour'])})
    med_ang = core.find_med_ang(images)
    core.rotate_images(images, target_angle=med_ang)


# Чтение dicom-файлов, обработка и запись их в формат JSON
def get_from_dicom(proc=False):
    template_dict = io_files.read_json_template(config.PATH_TEMPLATE_JSON)
    tree_files_di = io_files.get_tree_files(config.PATH_READ_DICOM, level_down=True)
    to_wrt = config.PATH_DATA_JSON
    # Считываем файлы
    for root, item in tree_files_di.items():
        name_dir = root.split('/')[-1]
        print(str.format('Начало  записи файла № {0}', name_dir))
        dict_series = io_files.form_dicom_to_dict(_path=root,
                                                  di_files=item,
                                                  tmp=template_dict,
                                                  path_wrt=None if proc else to_wrt)
        if proc:
            processing_series(dict_series['Data'])
            io_files.save_to_file(dict_series,
                                  _path=config.PATH_DATA_JSON,
                                  name=name_dir)
        dict_series.clear()
        print(str.format('Завершена запись файла № {0}', name_dir))


def get_from_json(proc=False, name=None):
    tree_files_json = io_files.get_tree_files(config.PATH_DATA_JSON, ext='*.json')
    for root, item in tree_files_json.items():
        for file in item:
            series = io_files.load_from_files(name=file,
                                              _path=config.PATH_DATA_JSON)
            print(str.format('Обработка файла {0}', file))
            if proc:
                processing_series(series['Data'])
            io_files.save_to_file(series,
                                  _path=config.PATH_DATA_JSON,
                                  name=file)
            series.clear()


if __name__ == "__main__":
    print('run main')

