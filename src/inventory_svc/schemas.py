from pydantic import BaseModel

class NewItem(BaseModel):
    title: str
    author: str
    genre: str
    price: float
    stock_quantity: int
    isbn: str 
    # history: list[dict]