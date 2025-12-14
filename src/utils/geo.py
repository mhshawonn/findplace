from typing import List

class GeoUtils:
    @staticmethod
    def split_bbox(bbox: List[float], rows: int = 2, cols: int = 2) -> List[List[float]]:
        """
        Splits a bounding box into a grid of smaller boxes.
        bbox format: [south, north, west, east]
        """
        s, n, w, e = bbox
        
        lat_step = (n - s) / rows
        lon_step = (e - w) / cols
        
        sub_bboxes = []
        
        for r in range(rows):
            for c in range(cols):
                # Calculate sub-box
                # south = s + r * step
                # north = s + (r+1) * step
                sub_s = s + (r * lat_step)
                sub_n = s + ((r + 1) * lat_step)
                
                sub_w = w + (c * lon_step)
                sub_e = w + ((c + 1) * lon_step)
                
                sub_bboxes.append([sub_s, sub_n, sub_w, sub_e])
                
        return sub_bboxes

    @staticmethod
    def is_bbox_too_large(bbox: List[float], max_sq_degrees: float = 0.25) -> bool:
        """
        Heuristic to check if tiling is needed.
        0.5 deg * 0.5 deg = 0.25 sq deg (approx 50km x 50km)
        """
        s, n, w, e = bbox
        height = n - s
        width = e - w
        return (height * width) > max_sq_degrees
