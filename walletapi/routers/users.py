from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from typing import Annotated, Dict

from models.user import User, RegisteredUser, ChangedPassword, UpdatedUser
from models.dbmodels import DBUser

import deps
import models

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=User)
def get_me(current_user: User = Depends(deps.get_current_user)) -> User:
    return current_user


@router.get("/{user_id}", response_model=User)
async def get(
    user_id: str,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: User = Depends(deps.get_current_user),
) -> User:

    user = await session.get(DBUser, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found this user",
        )
    return user


@router.post("/create", response_model=User)
async def create(
    user_info: RegisteredUser,
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> User:

    result = await session.exec(
        select(DBUser).where(DBUser.username == user_info.username)
    )

    user = result.one_or_none()

    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This username is exists.",
        )

    user = DBUser.from_orm(user_info)
    await user.set_password(user_info.password)
    await session.add(user)
    await session.commit()

    return user


@router.put("/{user_id}/change_password", response_model=User)
async def change_password(
    user_id: str,
    password_update: ChangedPassword,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: User = Depends(deps.get_current_user),
) -> Dict[str, str]:

    user = await session.get(DBUser, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found this user",
        )

    if not user.verify_password(password_update.current_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
        )

    await user.set_password(password_update.new_password)
    await session.add(user)
    await session.commit()
    
    return {"message": "Password changed successfully"}


@router.put("/{user_id}/update", response_model=User)
async def update(
    request: Request,
    user_id: str,
    user_update: UpdatedUser,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: User = Depends(deps.get_current_user),
) -> User:

    user = await session.get(DBUser, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found this user",
        )

    if not user.verify_password(user_update.current_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
        )

    set_dict = user_update.dict(exclude_unset=True, exclude={'current_password'})
    for key, value in set_dict.items():
        setattr(user, key, value)

    await session.add(user)
    await session.commit()
    await session.refresh(user)

    return user