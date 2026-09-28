from fastapi import FastAPI
from fastapi.responses import JSONResponse

class ItemByIdNotFound(Exception):
    """Exception raised when item not found by ID"""
    def __init__(self, item_id: str, detail: str, status_code: int = 404):
        self.status_code = status_code
        self.item_id = item_id
        self.detail = detail
        self.msg = f"Item {item_id} not found. {detail}"

        super().__init__(self.msg)

class ItemExists(Exception):
    """Exception raised when item is already existent"""
    def __init__(self, id: str, detail: str | dict, status_code: int = 422):
        self.id = str
        self.status_code = status_code
        self.detail = detail
        self.msg = f"Item {id} already exists. {detail}"

        super().__init__(self.msg)


class QuantityInvalid(Exception):
    """Exception raised when quantity received/sold is improper"""
    def __init__(self, item_id: str, detail: str | dict, status_code: int = 422):
        self.item_id = item_id
        self.detail = detail
        self.status_code = status_code
        self.msg = f"Invalid quantity. Can not update {item_id}. {detail}"

        super().__init__(self.msg)


class JsonServerRepoError(Exception):
    def __init__(self, detail: str):
        self.detail = detail
        self.msg = f"Repo error. {detail}"

        super().__init__(self.msg)


async def item_by_id_not_found_handler(request, err):
    return JSONResponse(
        status_code = err.status_code,
        content = {
            "error": "ITEM_BY_ID_NOT_FOUND",
            "msg": err.msg
        }
    )

async def item_exists_handler(request, err):
    return JSONResponse(
        status_code = err.status_code,
        content = {
            "error": "ITEM_EXISTS",
            "msg": err.msg
        }
    )

async def quantity_invalid_handler(request, err):
    return JSONResponse(
        status_code = err.status_code,
        content = {
            "error": "QUANTITY_INVALID",
            "msg": err.msg
        }
    )

async def json_server_repo_error_handler(req, err):
    return JSONResponse(
        status_code = 500,
        content = {
            "error": "REPO_ERROR",
            "detail": err.msg
        }
    )

EXCEPTION_HANDLERS = {
    ItemByIdNotFound: item_by_id_not_found_handler,
    ItemExists: item_exists_handler,
    QuantityInvalid: quantity_invalid_handler,
    JsonServerRepoError: json_server_repo_error_handler
}

def register_exception_handlers(app: FastAPI):
    for exception, handler in EXCEPTION_HANDLERS.items():
        app.add_exception_handler(exception, handler)
