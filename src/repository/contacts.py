from typing import List
from sqlalchemy import and_
from sqlalchemy.orm import Session
from src.database.models import Contact, User
from datetime import date, datetime, timedelta
from src.schemas import ContactEmail, ContactModel, ResponseContactModel


async def create_contact(
    contact: ContactModel, user: User, db: Session
) -> ContactModel:
    new_contact = Contact(
        name=contact.name,
        lastname=contact.lastname,
        email=contact.email,
        phone=contact.phone,
        born_date=contact.born_date,
        description=contact.description,
        user=user,
    )
    db.add(new_contact)
    db.commit()
    db.refresh(new_contact)

    return new_contact


async def get_contacts(user: User, db: Session) -> List[ResponseContactModel]:

    return db.query(Contact).filter(Contact.user_id == user.id).all()


async def get_contact(contact_id: int, user: User, db: Session) -> ContactModel:
    return (
        db.query(Contact)
        .filter(and_(Contact.id == contact_id, Contact.user_id == user.id))
        .first()
    )


async def update_contact(
    contact_id: int,
    user: User,
    db: Session,
    name,
    lastname,
    email,
    phone,
    born_date,
    description,
) -> ContactModel:
    target_contact = (
        db.query(Contact)
        .filter(and_(Contact.id == contact_id, Contact.user_id == user.id))
        .first()
    )
    if name:
        target_contact.name = name
    if lastname:
        target_contact.lastname = lastname
    if email:
        target_contact.email = email
    if phone:
        target_contact.phone = phone
    if born_date:
        target_contact.born_date = born_date
    if description:
        target_contact.description = description

    db.commit()
    return target_contact


async def delete_contact(contact_id, user: User, db: Session) -> Contact | None:
    item = (
        db.query(Contact)
        .filter(and_(Contact.id == contact_id, Contact.user_id == user.id))
        .first()
    )
    if item:
        db.delete(item)
        db.commit()
    return


async def search_data(
    user: User, db: Session, name: str, lastname: str, email: str
) -> ContactModel | None:

    if name:
        return (
            db.query(Contact)
            .filter(and_(Contact.name == name, Contact.user_id == user.id))
            .first()
        )
    if lastname:
        return (
            db.query(Contact)
            .filter(and_(Contact.lastname == lastname, Contact.user_id == user.id))
            .first()
        )
    if email:
        return (
            db.query(Contact)
            .filter(and_(Contact.email == email, Contact.user_id == user.id))
            .first()
        )


async def birthday_to_week(user: User, db: Session) -> List[ContactModel] | None:
    users = db.query(Contact).filter(Contact.user_id == user.id).all()
    week = date.today() + timedelta(days=6)
    happy_users = []
    for user in users:
        bday = datetime(
            date.today().year,
            user.born_date.month,
            user.born_date.day,
        ).date()

        if date.today() <= bday <= week:
            happy_users.append(user)

    return happy_users
