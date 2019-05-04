import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import os
from scipy.misc import imsave
import skimage.io as io
import numpy as np


def save_img(data_pixel,
             _title=None,
             _path=None):
    try:
        os.stat(_path)
    except FileNotFoundError:
        os.makedirs(_path)
    file_name = os.path.join(_path, str(_title) + '.png')
    io.imsave(file_name, data_pixel)


def show_img(data_pixel,
             _title=None):
    io.imshow(data_pixel, cmap='gray')
    io.show()


def easy_show_image(data):
    # Строим график
    fig, ax = plt.subplots()
    plt.ion()
    for img in data:
        plt.imshow(img, cmap='gray')
        fig.canvas.draw()
    plt.ioff()
    plt.show()  # Добавлено что-бы открывало окно


def show_image(data_pixel,
               xy_contour=None,
               xy_ellipse=None,
               _title=None,
               _path=None,
               save=False,
               show_img=False):
    # Подготовка директории
    if save:
        if xy_contour is not None and xy_ellipse is not None:
            _path += '/with_con&ell'
        elif xy_contour is not None and xy_ellipse is None:
            _path += '/with_con'
        elif xy_contour is None and xy_ellipse is not None:
            _path += '/with_ell'
        # Если такой дирректории нет, создаем ее
        try:
            os.stat(_path)
        except FileNotFoundError:
            os.makedirs(_path)
    # Строим график
    fig, ax = plt.subplots()
    if _title:
        ax.set_title(str(_title), color='white', backgroundcolor='black')
    plt.imshow(data_pixel, cmap='gray')
    X, Y = ax.get_xlim(), ax.get_ylim()
    ax.set_xlim(X), ax.set_ylim(Y)
    plt.axis('off')
    if xy_contour is not None:
        ax.plot(xy_contour.T[1], xy_contour.T[0], c='r', linewidth=1.5)
    if xy_ellipse is not None:
        ax.plot(xy_ellipse.T[1], xy_ellipse.T[0], c='b', linewidth=1.5)
    if show_img:
        plt.show()
    if save:
        filename = str(_path) + '/' + str(_title) + '.png'
        plt.savefig(filename, facecolor='black', format='png', bbox_inches='tight', pad_inches=0)
    plt.close()


# Создание сдвоенной анимации и ее сохранение
def save_animation(data,
                     _title=None,
                     _path=None):
    class IMGLoader:
        ic = data

        def __call__(self, frame):
            return np.hstack([self.ic[frame]['oldData'], self.ic[frame]['newData']])

    img_load = IMGLoader()
    frm = range(len(data))
    img_collection = io.ImageCollection(frm, load_func=img_load)

    fig, ax = plt.subplots()
    show_img = plt.imshow(img_collection[0], cmap='gray')
    plt.axis('off')

    def update(i):
        show_img.set_data(img_collection[i])
        return show_img

    anim = FuncAnimation(fig, update, frames=frm, interval=10, repeat=True)

    # Подготовка директории
    try:
        os.stat(_path)
    except FileNotFoundError:
        os.makedirs(_path)

    filename = os.path.join(_path, _title + '.gif')
    anim.save(filename, writer='imagemagick', fps=30)
