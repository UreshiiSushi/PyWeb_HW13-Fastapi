from typing import List

from fastapi import APIRouter, HTTPException, Depends, status, Path, Query
from sqlalchemy.orm import Session
from src.services.auth import auth_service
from src.database.db import get_db
from src.database.models import User
from src.schemas import ContactModel, ResponseContactModel, ContactEmail
from src.repository import contacts as repository_contacts
from fastapi_limiter.depends import RateLimiter

router = APIRouter(prefix="/contacts", tags=["contacts"])


# Create a new contact
@router.post(
    "/",
    response_model=ResponseContactModel,
    status_code=status.HTTP_201_CREATED,
    description="No more than 10 requests per minute",
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def create_new_contact(
    contact: ContactModel,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):

    return await repository_contacts.create_contact(contact, current_user, db)


@router.get(
    "/",
    response_model=list[ResponseContactModel],
    description="No more than 10 requests per minute",
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def get_all_contacts(
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):

    return await repository_contacts.get_contacts(current_user, db)


# Get one contact with the specific ID
@router.get(
    "/{contact_id}",
    response_model=ResponseContactModel,
    description="No more than 10 requests per minute",
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def read_contact(
    contact_id: int = Path(description="The ID of the contsct to get", gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    contact = await repository_contacts.get_contact(contact_id, current_user, db)

    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return contact


# Update exist contact
@router.patch(
    "/{contact_id}",
    response_model=ResponseContactModel,
    description="No more than 10 requests per minute",
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def update_contact(
    contact_id: int = Path(description="The ID of the contsct to get", gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
    name: str = None,
    lastname: str = None,
    email: str = None,
    phone: str = None,
    born_date: str = None,
    description: str = None,
):
    target_contact = await repository_contacts.update_contact(
        contact_id,
        current_user,
        db,
        name,
        lastname,
        email,
        phone,
        born_date,
        description,
    )
    if target_contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return target_contact


# Delete contact
@router.delete(
    "/{contact_id}",
    response_model=ResponseContactModel,
    description="No more than 10 requests per minute",
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def delete_contact(
    contact_id: int = Path(description="The ID of the contsct to get", gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    contact = await repository_contacts.delete_contact(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )

    return {"message": "Contact Deleted Succesfully"}


# Search for an email, name or lastname
@router.get(
    "/search/",
    response_model=ResponseContactModel,
    description="No more than 10 requests per minute",
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def search_contact(
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
    name: str = Query(None),
    lastname: str = Query(None),
    email: str = Query(None),
):
    search_result = await repository_contacts.search_data(
        current_user, db, name, lastname, email
    )
    if search_result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )

    return search_result


# Get birthdays for next 7 days
@router.get(
    "/birthdays/",
    description="No more than 10 requests per minute",
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def get_birthday_week(
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    happy_users = await repository_contacts.birthday_to_week(current_user, db)
    if happy_users is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contacts not found"
        )

    return happy_users
