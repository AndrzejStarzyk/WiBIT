from typing import Union


class Region:
    def __init__(self, name: str, lat: float, lon: float, country: str = None):
        self.name: str = name
        self.country: Union[None, str] = country
        self.lat: float = lat
        self.lon: float = lon

    def get_country_region(self):
        country = ''
        if self.country is not None:
            country = self.country.lower()
        return f"{country}-{self.name.lower()}"
