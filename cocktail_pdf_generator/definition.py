from typing import List, TypedDict


class RecipeData(TypedDict, total=False):
    title: str
    ingredients: List[str]
    steps: List[str]
    image_path: str | None
    glass: str | None