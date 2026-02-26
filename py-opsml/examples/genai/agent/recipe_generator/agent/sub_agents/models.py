from pydantic import BaseModel
from typing import List, Optional


class Ingredient(BaseModel):
    name: str
    quantity: str
    unit: str


class Rating(BaseModel):
    score: int
    reason: str


class Recipe(BaseModel):
    name: str
    ingredients: List[Ingredient]
    directions: List[str]
    prep_time_minutes: int
    servings: int
    rating: Optional[Rating] = None
