from pydantic import BaseModel

class NewItem(BaseModel):
    title: str
    author: str
    genre: str
    price: float
    stock_quantity: int
    isbn: str 
    # history: list[dict]


class OrderItem(BaseModel):
    book_id: str
    title: str
    isbn: str
    price: float
    quantity: int
    subtotal: float


class InventoryReservationRequest(BaseModel):
    reservation_id: str
    items: list[OrderItem]