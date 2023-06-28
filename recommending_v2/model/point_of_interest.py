from typing import List


class PointOfInterest:
    def __init__(self, xid: str, name: str, lon: float, lat: float, kinds: List[str]):
        self.xid: str = xid
        self.name: str = name
        self.lat: float = lat
        self.lon: float = lon
        self.kinds: List[str] = kinds

    def __str__(self):
        res = f"xid: {self.xid}, name: {self.name}, lat: {self.lat}, lon: {self.lon}, kinds: "
        for kind in self.kinds:
            res += kind + ", "
        return res[0:-2]

