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

    @staticmethod
    def default():
        return Recipe(
            name="",
            ingredients=[],
            directions=[],
            prep_time_minutes=0,
            servings=0,
            rating=None,
        )


class VegetarianValidation(BaseModel):
    is_vegetarian: bool
    reason: str
    non_vegetarian_ingredients: List[str]


class PracticalValidation(BaseModel):
    is_practical: bool
    reason: str
