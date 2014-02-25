"""Implements some generally useful utilities"""

import numpy as np
from scipy import ndimage


def rotation_matrix_2d(angle):
    """Returns a rotation matrix of the given angle


    Parameters
    ----------

    angle : {float}
        Angle in radians for counterclockwise rotation
"""

    rot = np.array([[np.cos(angle), -np.sin(angle)],
                    [np.sin(angle), np.cos(angle)]])

    return rot


def convolve(img_or_imgs, fil):
    if img_or_imgs.ndim == 3:
        fil = fil[np.newaxis, :, :]

    return ndimage.convolve(img_or_imgs, fil, mode='wrap')


def fft_convolve(img_or_imgs, fil_or_fils):
    fft_fil = np.fft.fftn(fil_or_fils, axes=[-2, -1])
    if img_or_imgs.ndim == 3:
        fft_fil = fft_fil[np.newaxis, ...]
    if fil_or_fils.ndim == 3:
        if img_or_imgs.ndim == 3:
            img_or_imgs = img_or_imgs[:, np.newaxis, :, :]
        elif img_or_imgs.ndim == 2:
            img_or_imgs = img_or_imgs[np.newaxis, :, :]

    fft_img_or_imgs = np.fft.fftn(img_or_imgs, axes=[-2, -1])

    filtered = fft_img_or_imgs * fft_fil

    return np.fft.ifftn(filtered, axes=[-2, -1])


def evaluate_path(img, filter_bank, *args):
    if len(args) == 0:
        return img
    else:
        pretransformed = evaluate_path(img, filter_bank, *args[:-1])

        j, l = args[-1]
        fil = filter_bank['psi'][j][l]

        filtered = fft_convolve(pretransformed, fil)
        return np.abs(filtered)


def filter_panel(filter_bank, renormalize_l2=False, fov=None):

    filters = np.fft.fftshift(
        np.array(filter_bank['psi']['fil_list']),
        axes=[1, 2])
    if renormalize_l2:
        filter_norms = np.sqrt(
            (np.abs(filters.reshape(len(filters), -1)) ** 2).sum(axis=1))
        filters /= filter_norms[:, np.newaxis, np.newaxis]
    if fov is None:
        fov = (slice(0, None), slice(0, None))
    full_slice = [slice(None)] + list(fov)
    filters = filters[full_slice]
    L = filter_bank["L"]
    J = filter_bank["J"]

    panel = filters.reshape(
        J, L, filters.shape[1], filters.shape[2]
        ).transpose(0, 2, 1, 3).reshape(J * filters.shape[1], -1)

    return panel


def show_filters(filter_bank, renormalize_l2=False, fov=None):
    panel = filter_panel(filter_bank, fov=fov, 
                         renormalize_l2=renormalize_l2)
    re = np.real(panel)
    im = np.imag(panel)
    import pylab as pl
    pl.subplot(1, 2, 1)
    pl.imshow(re, interpolation="nearest")
    pl.subplot(1, 2, 2)
    pl.imshow(im, interpolation="nearest")


if __name__ == "__main__":
    # test fftconvolve
    from scipy.misc import lena
    lena = lena() / 256.
    imgs = np.array([lena, lena[:, ::-1]])

    fils = np.zeros(imgs.shape)

    fils[0][0, 0] = 1
    fils[0][-1, 0] = -1
    fils[1][0, 0] = 1
    fils[1][0, -1] = -1

    conv22 = fft_convolve(imgs, fils)
    conv12 = fft_convolve(imgs[0], fils)
    conv21 = fft_convolve(imgs, fils[0])
    conv11 = fft_convolve(imgs[0], fils[0])
