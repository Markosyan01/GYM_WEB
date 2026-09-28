from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.orm import Session
from . import models as m
from .auth import current_user
from .database import get_db

router = APIRouter(prefix="/api")


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    category: str
    description: str
    price: float
    stock: int
    image: str


class FacilityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    description: str
    image: str


class TestimonialOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    detail: str
    quote: str
    image: str


class ContactIn(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    body: str = Field(min_length=5, max_length=2000)


class CartLine(BaseModel):
    product_id: int
    qty: int = Field(ge=1, le=20)


class OrderIn(BaseModel):
    items: list[CartLine] = Field(min_length=1)


class OrderOut(BaseModel):
    id: int
    total: float
    lines: list[str]


@router.get("/products", response_model=list[ProductOut])
def products(category: str | None = None, db: Session = Depends(get_db)):
    q = select(m.Product).order_by(m.Product.category, m.Product.name)
    if category:
        q = q.where(m.Product.category == category)
    return db.scalars(q).all()


@router.get("/facilities", response_model=list[FacilityOut])
def facilities(db: Session = Depends(get_db)):
    return db.scalars(select(m.Facility)).all()


@router.get("/testimonials", response_model=list[TestimonialOut])
def testimonials(db: Session = Depends(get_db)):
    return db.scalars(select(m.Testimonial)).all()


@router.post("/contact", status_code=201)
def contact(body: ContactIn, db: Session = Depends(get_db)):
    db.add(m.Message(name=body.name, email=body.email, body=body.body))
    db.commit()
    return {"ok": True}


def order_out(o: m.Order):
    return OrderOut(id=o.id, total=float(o.total), lines=[f"{i.qty} x {i.product.name}" for i in o.items])


@router.post("/orders", response_model=OrderOut, status_code=201)
def create_order(body: OrderIn, u: m.User = Depends(current_user), db: Session = Depends(get_db)):
    order = m.Order(user_id=u.id, total=0)
    total = 0.0
    for line in body.items:
        p = db.get(m.Product, line.product_id, with_for_update=True)
        if not p:
            raise HTTPException(404, "A product in your cart no longer exists")
        if p.stock < line.qty:
            raise HTTPException(409, f"Only {p.stock} of {p.name} left in stock")
        p.stock -= line.qty
        total += float(p.price) * line.qty
        order.items.append(m.OrderItem(product_id=p.id, qty=line.qty, unit_price=p.price))
    order.total = round(total, 2)
    db.add(order)
    db.commit()
    db.refresh(order)
    return order_out(order)


@router.get("/me/orders", response_model=list[OrderOut])
def my_orders(u: m.User = Depends(current_user), db: Session = Depends(get_db)):
    rows = db.scalars(select(m.Order).where(m.Order.user_id == u.id).order_by(m.Order.id.desc())).all()
    return [order_out(o) for o in rows]
