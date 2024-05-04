from fastapi import FastAPI,status,HTTPException,Depends,Path
from .database import get_db,engine
from sqlalchemy.orm import Session
from . import schemas,tablesmodel,utils,oAuth2
from fastapi.middleware.cors import CORSMiddleware
from typing import List

app = FastAPI()

#origins = ["www.youtube.com", "www.google.com"]
origins=["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

tablesmodel.Base.metadata.create_all(bind = engine)

@app.get("/")
def root():
    return {"message" : "Welcome to my API...."}

""" {
    "email": "neha@gmail.com",
    "password": "password",
    "name": "Neha Tomar", 
    "address": "sector 13",
    "phone_num": "1234567893",
    "role": "customer"
} """
@app.post("/signup", response_model=schemas.UserOut)
async def create_user(user:schemas.UserCreate, db: Session = Depends(get_db)):
    
    user_found = db.query(tablesmodel.User).filter(tablesmodel.User.email==user.email).first()

    if user_found:
       raise HTTPException(status_code=status.HTTP_302_FOUND, detail="Email already exists")
    
    hashed_password = utils.hash(user.password)
    user.password = hashed_password

    new_user = tablesmodel.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    utils.send_email(user.email)
    return new_user  

""" {
    "email": "neha@gmail.com",
    "password": "password"
} """
@app.post("/login")
async def loginPage(user_credentials:schemas.UserLogin ,db: Session = Depends(get_db)):

    user = db.query(tablesmodel.User).filter(tablesmodel.User.email==user_credentials.email).first()

    if not user:
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Credentials")
    
    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Credentials")
    
    access_token = oAuth2.create_access_token(data={"user_id": user.id})
    return {"access_token": access_token, "token_type": "Bearer"}

#Route to place an order
@app.post("/order", response_model=schemas.LaundryOrder)
async def place_order(order: schemas.LaundryOrder, current_user: tablesmodel.User = Depends(oAuth2.get_current_user), db: Session = Depends(get_db)):
    if not current_user:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="Unauthorized User")
    
    db_order = tablesmodel.Order(
        shop_id=order.shop_id,
        quantity=order.quantity,
        washing_type=order.washing_type,
        price=order.price,
        owner_id = current_user.id
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

#Route to history of orders
@app.get("/order/history", response_model=List[schemas.OrderHistory])
async def get_order_history(current_user: tablesmodel.User = Depends(oAuth2.get_current_user), db: Session = Depends(get_db)):

    if not current_user:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="Unauthorized User")
    
    orders = db.query(tablesmodel.Order).filter(tablesmodel.Order.owner_id == current_user.id).all()
    if orders is None:
        raise HTTPException(status_code=404, detail="No Order is place till now")
    
    return orders

#Route to Update payment of service provided
@app.put("/updatepaymentstatus")
def update_fee_details(db: Session = Depends(get_db), current_user: tablesmodel.User = Depends(oAuth2.get_current_user)):

    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized User")
    
    payment_status = db.query(tablesmodel.Order).filter(tablesmodel.Order.owner_id == current_user.id).first()

    if payment_status is None:
        raise HTTPException(status_code=404, detail="Payment details not found")

    payment_status.payment_status = "Paid"

    db.commit()
    db.refresh(payment_status)
    return payment_status

#Route for service provider to view order details
@app.get('/washing_orders', response_model=list[dict])
def get_washing_orders(db: Session = Depends(get_db)):
    washing_orders = db.query(tablesmodel.Order).filter_by(order_status='null').all()
    
    orders_data = []
    for order in washing_orders:
        order_data = {
            'Order ID': order.id,
            'Address': tablesmodel.User.address,
        }
        orders_data.append(order_data)
    
    return orders_data

# Route for service provider to update order status
@app.patch("/orders/{order_id}")
async def update_order_status(order_id: int, order_status: str = Path(..., title="Order Status", description="New order status"), db: Session = Depends(get_db)):

    valid_statuses = ["pending", "confirmed", "shipped", "delivered", "cancelled"]

    if order_status.lower() not in valid_statuses:
        raise HTTPException(status_code=400, detail="Invalid order status")
    
    order_details = db.query(tablesmodel.Order).filter(tablesmodel.Order.owner_id == order_id).first()
    if not order_details:
        raise HTTPException(status_code=404, detail="Order details not found")
    
    order_details.order_status = order_status.lower()
    db.commit()
    
    return {"message": "Order status updated successfully"}

#Route to give rating
@app.post("/rate")
async def rate(rating: schemas.RatingRequest, current_user: tablesmodel.User = Depends(oAuth2.get_current_user), db: Session = Depends(get_db)):

    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized User")
    
    if rating.stars < 1 or rating.stars > 5:
        raise HTTPException(status_code=400, detail="Invalid rating value. Must be between 1 and 5.")
    
    db_rating = tablesmodel.Rating(owner_id = current_user.id, stars = rating.stars)
    db.add(db_rating)
    db.commit()
    db.refresh(db_rating)

    return db_rating
