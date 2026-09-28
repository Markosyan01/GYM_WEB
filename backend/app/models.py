from sqlalchemy import String, Integer, ForeignKey, Text, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base


class Plan(Base):
    __tablename__ = "plans"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    price: Mapped[float] = mapped_column(Numeric(8, 2))
    features: Mapped[str] = mapped_column(Text)  # one feature per line


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    plan_id: Mapped[int | None] = mapped_column(ForeignKey("plans.id"), nullable=True)
    plan: Mapped[Plan | None] = relationship()


class Trainer(Base):
    __tablename__ = "trainers"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    specialty: Mapped[str] = mapped_column(String(100))
    bio: Mapped[str] = mapped_column(Text)
    image: Mapped[str] = mapped_column(String(300), default="")


class GymClass(Base):
    __tablename__ = "classes"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(Text)
    day: Mapped[str] = mapped_column(String(3))  # Mon..Sun
    start: Mapped[str] = mapped_column(String(5))  # HH:MM
    capacity: Mapped[int] = mapped_column(Integer)
    image: Mapped[str] = mapped_column(String(300), default="")
    trainer_id: Mapped[int] = mapped_column(ForeignKey("trainers.id"))
    trainer: Mapped[Trainer] = relationship()


class Booking(Base):
    __tablename__ = "bookings"
    __table_args__ = (UniqueConstraint("user_id", "class_id"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    class_id: Mapped[int] = mapped_column(ForeignKey("classes.id", ondelete="CASCADE"))


class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    category: Mapped[str] = mapped_column(String(40))
    description: Mapped[str] = mapped_column(Text)
    price: Mapped[float] = mapped_column(Numeric(8, 2))
    stock: Mapped[int] = mapped_column(Integer, default=0)
    image: Mapped[str] = mapped_column(String(300), default="")


class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    total: Mapped[float] = mapped_column(Numeric(10, 2))
    items: Mapped[list["OrderItem"]] = relationship(cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    qty: Mapped[int] = mapped_column(Integer)
    unit_price: Mapped[float] = mapped_column(Numeric(8, 2))
    product: Mapped[Product] = relationship()


class Facility(Base):
    __tablename__ = "facilities"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(Text)
    image: Mapped[str] = mapped_column(String(300), default="")


class Testimonial(Base):
    __tablename__ = "testimonials"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    detail: Mapped[str] = mapped_column(String(120))
    quote: Mapped[str] = mapped_column(Text)
    image: Mapped[str] = mapped_column(String(300), default="")


class Message(Base):
    __tablename__ = "messages"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255))
    body: Mapped[str] = mapped_column(Text)
