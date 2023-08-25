from . import layers
from .utils import get_unit_size
from .bbox import get_center
from numpy import int
from typing import List
from typing import Tuple
from typing import Union
from numpy import int
from typing import Any
from typing import Callable
from typing import Optional


def filter_out_of_range_bbox(bboxes: Union[List[Tuple[int, int, int, int]], List[Tuple[int, int, int, int]]]) -> Union[List[Tuple[int, int, int, int]], List[Tuple[int, int, int, int]]]:
    zones = layers.get_layer('zones')
    max_x = zones[-1][-1]
    min_x = zones[0][0]

    valid_box = []
    for box in bboxes:
        cen_x = round((box[0]+box[2])/2)
        if (cen_x > max_x) or (cen_x < min_x):
            continue
        valid_box.append(box)
    return valid_box
 

def filter_out_small_area(bboxes: Union[List[Tuple[int, int, int, int]], List[Tuple[int, int, int, int]]], area_size: Optional[Any] = None, area_size_func: Optional[Callable] = None) -> Union[List[Tuple[int, int, int, int]], List[Tuple[int, int, int, int]]]:
    valid_box = []
    for box in bboxes:
        w = box[2] - box[0]
        h = box[3] - box[1]
        if area_size is not None:
            size = area_size
        else:
            unit_size = get_unit_size(*get_center(box))
            size = area_size_func(unit_size)
        if w * h > size:
            valid_box.append(box)
    return valid_box
