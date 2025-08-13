from dataclasses import dataclass
from typing import Optional
import enum

class Seasonality(enum.Enum):
    SUMMER = "Summer"
    WINTER = "Winter"
    ALL_SEASON = "All Season"

class TyreType(enum.Enum):
    CAR = "Car"
    FOUR_BY_FOUR = "4x4"
    VAN = "Van"

class Grade(enum.Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"

class SpeedRating(enum.Enum):
    L = "L"
    M = "M"
    N = "N"
    P = "P"
    Q = "Q"
    R = "R"
    S = "S"
    T = "T"
    U = "U"
    H = "H"
    V = "V"
    W = "W"
    Y = "Y"
    ZR = "ZR"

@dataclass
class Tyre:
    # Mandatory fields
    website: str
    brand: str
    name: str
    size: str
    price: float
    
    # Optional fields
    seasonality: Optional[Seasonality] = None
    type: Optional[TyreType] = None
    wet_grip: Optional[Grade] = None
    fuel_efficiency: Optional[Grade] = None
    speed_rating: Optional[SpeedRating] = None
    load_index: Optional[int] = None
    electric: Optional[bool] = None
    self_seal: Optional[bool] = None
    run_flat: Optional[bool] = None
    noise_reduction: Optional[bool] = None