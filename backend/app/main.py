import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, func
from sqlalchemy.exc import OperationalError, IntegrityError
from sqlalchemy.orm import Session
from . import models as m, schemas as s
from .database import engine, Base, get_db, SessionLocal
from .auth import hash_pw, verify_pw, make_token, current_user, optional_user
from .seed import seed
from .extras import router as extras_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    for _ in range(30):
        try:
            Base.metadata.create_all(engine)
            break
        except OperationalError:
            time.sleep(2)
    with SessionLocal() as db:
        seed(db)
    yield


app = FastAPI(title="Iron Yard Gym API", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000", "http://localhost:5173"],
                   allow_methods=["*"], allow_headers=["*"])


app.include_router(extras_router)


def plan_out(p: m.Plan | None):
    if not p:
        return None
    return s.PlanOut(id=p.id, name=p.name, price=float(p.price), features=p.features.split("\n"))


def user_out(u: m.User):
    return s.UserOut(id=u.id, name=u.name, email=u.email, plan=plan_out(u.plan))


def class_out(db: Session, c: m.GymClass, uid: int | None):
    booked = db.scalar(select(func.count()).select_from(m.Booking).where(m.Booking.class_id == c.id))
    joined = bool(uid and db.scalar(select(m.Booking.id).where(m.Booking.class_id == c.id, m.Booking.user_id == uid)))
    return s.ClassOut(id=c.id, title=c.title, description=c.description, day=c.day, start=c.start,
                      trainer=c.trainer.name, capacity=c.capacity, booked=booked, joined=joined, image=c.image)


@app.get("/api/health")
def health():
    return {"ok": True}


@app.post("/api/auth/register", response_model=s.TokenOut, status_code=201)
def register(body: s.RegisterIn, db: Session = Depends(get_db)):
    email = body.email.lower()
    if db.scalar(select(m.User.id).where(m.User.email == email)):
        raise HTTPException(409, "That email is already registered")
    u = m.User(name=body.name.strip(), email=email, password_hash=hash_pw(body.password))
    db.add(u)
    db.commit()
    return {"token": make_token(u.id)}


@app.post("/api/auth/login", response_model=s.TokenOut)
def login(body: s.LoginIn, db: Session = Depends(get_db)):
    u = db.scalar(select(m.User).where(m.User.email == body.email.lower()))
    if not u or not verify_pw(body.password, u.password_hash):
        raise HTTPException(401, "Email or password is incorrect")
    return {"token": make_token(u.id)}


@app.get("/api/me", response_model=s.UserOut)
def me(u: m.User = Depends(current_user)):
    return user_out(u)


@app.get("/api/plans", response_model=list[s.PlanOut])
def plans(db: Session = Depends(get_db)):
    return [plan_out(p) for p in db.scalars(select(m.Plan).order_by(m.Plan.price))]


@app.post("/api/me/plan/{plan_id}", response_model=s.UserOut)
def choose_plan(plan_id: int, u: m.User = Depends(current_user), db: Session = Depends(get_db)):
    if not db.get(m.Plan, plan_id):
        raise HTTPException(404, "Plan not found")
    u.plan_id = plan_id
    db.commit()
    db.refresh(u)
    return user_out(u)


@app.get("/api/trainers", response_model=list[s.TrainerOut])
def trainers(db: Session = Depends(get_db)):
    return db.scalars(select(m.Trainer)).all()


@app.get("/api/classes", response_model=list[s.ClassOut])
def classes(u: m.User | None = Depends(optional_user), db: Session = Depends(get_db)):
    rows = db.scalars(select(m.GymClass).order_by(m.GymClass.start)).all()
    return [class_out(db, c, u.id if u else None) for c in rows]


@app.get("/api/me/bookings", response_model=list[s.ClassOut])
def my_bookings(u: m.User = Depends(current_user), db: Session = Depends(get_db)):
    rows = db.scalars(select(m.GymClass).join(m.Booking).where(m.Booking.user_id == u.id)).all()
    return [class_out(db, c, u.id) for c in rows]


@app.post("/api/classes/{class_id}/book", response_model=s.ClassOut)
def book(class_id: int, u: m.User = Depends(current_user), db: Session = Depends(get_db)):
    c = db.get(m.GymClass, class_id, with_for_update=True)  # lock row so capacity holds under load
    if not c:
        raise HTTPException(404, "Class not found")
    if not u.plan_id or u.plan.price < 49:
        raise HTTPException(403, "Booking classes needs the Floor + Classes plan or higher")
    taken = db.scalar(select(func.count()).select_from(m.Booking).where(m.Booking.class_id == c.id))
    if taken >= c.capacity:
        raise HTTPException(409, "This class is full")
    db.add(m.Booking(user_id=u.id, class_id=c.id))
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "You are already booked in")
    return class_out(db, c, u.id)


@app.delete("/api/classes/{class_id}/book", status_code=204)
def cancel(class_id: int, u: m.User = Depends(current_user), db: Session = Depends(get_db)):
    b = db.scalar(select(m.Booking).where(m.Booking.class_id == class_id, m.Booking.user_id == u.id))
    if b:
        db.delete(b)
        db.commit()
    return Response(status_code=204)
