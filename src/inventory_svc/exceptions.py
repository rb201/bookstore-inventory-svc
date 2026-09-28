###
# Business Exceptions
###

class ItemByIdNotFound(Exception):
    """Exception raised when item not found by ID"""
    def __init__(self, status_code: int, item_id: str, detail: str):
        self.status_code = status_code
        self.item_id = item_id
        self.detail = detail

        self.msg = f"Item {item_id} not found. {detail}"

        super().__init__(self.msg)