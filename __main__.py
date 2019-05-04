import core
import io_files
import config
import imaging
import logging


# Обработка отдельного кадра
def processing_series(images):
    # Обработка каждого изображения
    for img in images:
        img['Contour'] = core.find_contour_brain(img['oldData'])
        img['newData'] = core.delete_unnecessary_obj(img)
        img['Ellipse'] = core.approximate_ellipse(img['Contour'])
    return core.find_med_ang(images)


def get_from_dicom(root_dir, files, flag_poc, flag_anim):
    name_dir = root_dir.split('/')[-1]
    print(str.format('Start processing series {0}', name_dir))
    dict_series = io_files.form_dicom_to_dict(_path=root_dir,
                                              di_files=files,
                                              tmp_dir=config.PATH_TEMPLATE_JSON)
    if flag_poc:
        dict_series['Angle of rotation'] = processing_series(dict_series['Data'])

    if flag_anim:
        imaging.save_animation(dict_series['Data'],
                               _title=name_dir,
                               _path=config.PATH_DATA_ANI)
        print(str.format('Save series {0} in GIF', name_dir))

    io_files.save_to_file(dict_series,
                          _path=config.PATH_DATA_JSON,
                          name=name_dir)
    print(str.format('Save series {0} in JSON', name_dir))


# Чтение dicom-файлов, обработка и запись их в формат JSON
def enumeration_dicom(proc=False, anim=False):
    tree_files_di = io_files.get_tree_files(config.PATH_READ_DICOM, level_down=True)
    logger = logging.getLogger("psd")
    logger.setLevel(logging.INFO)
    # create the logging file handler
    fh = logging.FileHandler("psd.log")
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    # add handler to logger object
    logger.addHandler(fh)
    # Считываем файлы
    for root, item in tree_files_di.items():
        logger.info(str.format('Start processing series from {0}', root))
        get_from_dicom(root_dir=root,
                       files=item,
                       flag_poc=proc,
                       flag_anim=anim)


def get_from_json(proc=False, anim=False):
    tree_files_json = io_files.get_tree_files(config.PATH_DATA_JSON, ext='*.json')
    for root, item in tree_files_json.items():
        for file in item:
            series = io_files.load_from_files(name=file,
                                              _path=config.PATH_DATA_JSON)
            print(str.format('Обработка файла {0}', file))

            if proc:
                series['Angle of rotation'] = processing_series(series['Data'])

            io_files.save_to_file(series,
                                  _path=config.PATH_DATA_JSON,
                                  name=file)
            if anim:
                print(str.format('Файл {0} анимирован', file))
                imaging.save_animation(series['Data'],
                                       _title=file,
                                       _path=config.PATH_DATA_ANI)
            series.clear()


if __name__ == "__main__":
    print('run main')
    enumeration_dicom(proc=True, anim=True)
