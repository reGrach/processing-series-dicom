import json
import numpy as np
from skimage import measure, transform


# Наложение маски на DICOM-img, чтобы вывести на экран
def modify_voi_lut(matrix,
                   window=[80, 40],
                   photometric_interpretation='MONOCHROME2',
                   function='LINEAR_EXACT',
                   lut_min=0,
                   lut_max=255):
    if np.isreal(matrix).sum() != matrix.size:
        raise ValueError

    # currently only support 8-bit colors
    if lut_max != 255:
        raise ValueError

    if matrix.dtype != np.float64:
        matrix = matrix.astype(np.float64)

    if photometric_interpretation == 'MONOCHROME2':
        window[0] = window[0] + 1024

    # LUT-specific array scaling
    # width >= 1 (DICOM standard)
    wc, ww = np.float64(window[0]), np.float64(max(1, window[1]))
    lut_range = np.float64(lut_max) - lut_min
    # Вычисление границ
    minval = wc - 0.5 * ww
    maxval = wc + 0.5 * ww
    if function == 'LINEAR_EXACT':
        min_mask = (minval >= matrix)
        to_scale = (matrix > minval) & (matrix < maxval)
        max_mask = (matrix >= maxval)
        if min_mask.any():
            matrix[min_mask] = lut_min
        if to_scale.any():
            matrix[to_scale] = ((matrix[to_scale] - (wc - 0.5)) / (ww - 1.0) + 0.5) * lut_range + lut_min
            # matrix[to_scale] = ((matrix[to_scale] - wc) / ww) * lut_range + lut_min
        if max_mask.any():
            matrix[max_mask] = lut_max
    elif function == 'SIGMOID':
        matrix = matrix.max() / (1 + np.exp(-4 * (matrix - wc) / ww))

    return np.rint(matrix).astype(np.uint8)


# Определение ключевого контура для исследования (по коре головного мозга)
def find_contour_brain(img):
    contours = measure.find_contours(modify_voi_lut(img, [-500, 2]), 0.5)
    ind_min = 0
    min_dev = 1000
    for ind in range(len(contours)):
        if len(contours[ind]) < 300:
            continue
        dev_xy = np.abs(np.mean(contours[ind].T[0]) - np.shape(img)[0] / 2) + \
                 np.abs(np.mean(contours[ind].T[1]) - np.shape(img)[1] / 2)
        if ind == 0:
            min_dev = dev_xy
        if dev_xy < min_dev:
            min_dev = dev_xy
            ind_min = ind
    return np.round(contours[ind_min]).astype(int)


# Удаление сторонних объектов и артефактов (вне области головного мозга)
def delete_unnecessary_obj(img):
    bit_img = measure.grid_points_in_poly((512, 512), img['Contour'])
    matrix = np.zeros((512, 512))
    if bit_img.any():
        matrix[bit_img] = img['oldData'].astype(np.float64)[bit_img]
    # img['newData'] = np.rint(matrix).astype(np.uint16)
    return np.rint(matrix).astype(np.uint16)


# Аппроксимация контура эллипсом и запись в словарь параметров эллипса
def approximate_ellipse(contour):
    ellipse = measure.EllipseModel()
    ellipse_dict = {'XY': [], 'Xc': 0, 'Yc': 0, 'a': 0, 'b': 0, 'theta': 0, 'dev': 0}
    if ellipse.estimate(contour):
        ellipse_dict.update({'XY': ellipse.predict_xy(np.linspace(0, 2 * np.pi, 1000), params=ellipse.params)})
        ellipse_dict.update({'Xc': float(ellipse.params[1])})
        ellipse_dict.update({'Yc': float(ellipse.params[0])})
        ellipse_dict.update({'a': float(ellipse.params[2])})
        ellipse_dict.update({'b': float(ellipse.params[3])})
        ellipse_dict.update({'theta': float(ellipse.params[4])})
        # Вычисление ошибки
        residuals_array = ellipse.residuals(contour)
        calc_dev = float(np.sqrt(np.sum((residuals_array ** 2) / len(residuals_array))))
        ellipse_dict.update({'dev': calc_dev})
    else:
        print('Проблема с эллипсом')
    return ellipse_dict


# Поиск медианы из массива углов наклона эллипса
def find_med_ang(list_img):
    list_ang = []
    for img in list_img:
        ang = np.degrees(-img['Ellipse']['theta'])
        if img['Ellipse']['dev'] > 10:
            continue

        if np.abs(ang) > 90:
            if ang > 0:
                ang = ang - 90
            else:
                ang = ang + 90
        list_ang.append(ang)
    return np.median(list_ang)


# Поворот матрицы пикселей
def rotate_images(images, target_angle=None):
    if not target_angle:
        target_angle = find_med_ang(images)
    for img in images:
        cntr = (img['Ellipse']['Xc'], img['Ellipse']['Yc'])
        rotated_img = transform.rotate(img['newData'],
                                       target_angle,
                                       center=cntr,
                                       preserve_range=True)
        img['newData'] = np.rint(rotated_img).astype(np.uint16)
