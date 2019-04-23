import matplotlib.pyplot as plt
import os
# import matplotlib.image as mpimg
# import numpy as np
# from matplotlib.patches import Ellipse


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




# ax.scatter(contours[ind_min].T[1], contours[ind_min].T[0], c=colors[0], s=1, marker='.')


# def show_image_with_ellips(img):
#     fig, ax = plt.subplots()
#     ax.imshow(img['newData'], interpolation='nearest', cmap=plt.cm.gray)
#     X, Y = ax.get_xlim(), ax.get_ylim()
#     ellipse_plot = Ellipse(xy=(img['Ellipse']['Xc'], img['Ellipse']['Yc']),
#                            width=2*img['Ellipse']['b'],
#                            height=2*img['Ellipse']['a'],
#                            angle=np.degrees(-img['Ellipse']['theta']),
#                            edgecolor='b',
#                            fc='None',
#                            lw=2)
#     ax.scatter(img['Ellipse']['XY'].T[1], img['Ellipse']['XY'].T[0])
#     ax.add_patch(ellipse_plot)
#     ax.set_xlim(X), ax.set_ylim(Y)
#     plt.title(str(img['Ellipse']['dev']) + ' ' + str(np.degrees(-img['Ellipse']['theta'])))
#     plt.show()


# ellipse_plot = Ellipse(xy=(image['Ellipse']['Xc'], image['Ellipse']['Yc']),
#                        width=2*image['Ellipse']['b'],
#                        height=2*image['Ellipse']['a'],
#                        angle=np.degrees(-image['Ellipse']['theta']),
#                        edgecolor='b',
#                        fc='None',
#                        lw=2)
#

# # Display the image and plot the contour
# fig, ax = plt.subplots()
# ax.imshow(image['Data'], interpolation='nearest', cmap=plt.cm.gray)
# #
# ax.plot(image['Contour'].T[1], image['Contour'].T[0], linewidth=2, c='r')
# # ax.plot(xy.T[0], xy.T[1], linewidth=2, c='b')
# ax.add_patch(ellipse_plot)
# # ax.step(contours[1].T[1], contours[1].T[0], linewidth=2, c='r')
# # X, Y = ax.get_xlim(), ax.get_ylim()
# # ax.set_xlim(X), ax.set_ylim(Y)
# plt.xlim(0, 500)
# plt.ylim(500, 0)
# plt.gca().set_aspect('equal', adjustable='box')
# plt.show()




# import matplotlib
#
# matplotlib.use("TkAgg")
# import numpy as np
# import matplotlib.pyplot as plt
# import matplotlib.animation as animation
#
# fig, ax = plt.subplots()
#
# x = np.arange(0, 2 * np.pi, 0.01)
# line, = ax.plot(x, np.sin(x))
#
#
# def animate(i):
#     line.set_ydata(np.sin(x + i / 10.0))  # update the data
#     return line,
#
#
# # Init only required for blitting to give a clean slate.
# def init():
#     line.set_ydata(np.ma.array(x, mask=True))
#     return line,
#
#
# ani = animation.FuncAnimation(fig, animate, np.arange(1, 20000), init_func=init,
#                               interval=25, blit=True)
# plt.show()
#
# # create animation using the animate() function
# myAnimation = animation.FuncAnimation(fig, animate, frames=np.arange(0.0, TWOPI, 0.1), \
#                                       interval=10, blit=True, repeat=True)
#
# plt.show()