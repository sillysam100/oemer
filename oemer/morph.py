
import numpy as np
import cv2
from numpy import ndarray
from typing import Tuple


def get_kernel(kernel: Tuple[int, int]) -> ndarray:
    if isinstance(kernel, tuple):
        # It's kernel shape
        kernel = np.ones(kernel, dtype=np.uint8)
    return kernel


def morph_open(img: ndarray, kernel: Tuple[int, int]) -> ndarray:
    ker = get_kernel(kernel)
    return cv2.morphologyEx(img.astype(np.uint8), cv2.MORPH_OPEN, ker)


def morph_close(img: ndarray, kernel: Tuple[int, int]) -> ndarray:
    ker = get_kernel(kernel)
    return cv2.morphologyEx(img.astype(np.uint8), cv2.MORPH_CLOSE, ker)


def morph_hit_miss(img, kernel):
    ker = get_kernel(kernel)
    return cv2.morphologyEx(img.astype(np.uint8), cv2.MORPH_HITMISS, ker)

