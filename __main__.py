import core
import io_files
import imaging
import config
from os import path


def processing_series(images):
    # Обработка каждого изображения
    for img in images:
        img['Contour'] = core.find_contour_brain(img['oldData'])    # Определяем границу мозга
        core.delete_unnecessary_obj(img, show=False)                # Очищаем Data от объектов вне контура
        core.approximate_ellipse(img)                               # Аппроксимация эллипсом
    med_ang = core.find_med_ang(images)                             # Определение угла (в градусах) поворота всех срезов
    core.rotate_images(images, target_angle=med_ang)                # Поворот всех срезов на целевой угол


if __name__ == "__main__":
    template_dict = io_files.read_json_template(config.PATH_TEMPLATE_JSON)
    tree_files = io_files.get_tree_files(config.PATH_READ_DICOM, level_down=True)
    for root, item in tree_files.items():
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
