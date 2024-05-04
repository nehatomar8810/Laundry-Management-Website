from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional,List

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: str
    name: str 
    phone_num: str
    address:str

class UserOut(BaseModel):
    email: EmailStr
    created_at: datetime
    role: str
    
    class Config:
        from_attributes = True 

class UserLogin(BaseModel):
    email: EmailStr
    password: str     

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[str] = None 

class LaundryOrder(BaseModel):
    shop_id: int
    quantity: int
    washing_type: str
    price: float

class OrderHistory(BaseModel):
    id: int
    user_id: int
    quantity: int
    washing_type: str
    price: float
    payment_status: str

    class Config:
        from_attributes = True 

class OrderDetails(BaseModel):
    order_id: int
    customer_name: str
    items: str
    status: str

class OrderStatusUpdate(BaseModel):
    order_id: int
    status: str  

class RatingRequest(BaseModel):
    stars: int                 