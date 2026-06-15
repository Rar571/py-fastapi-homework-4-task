from fastapi import APIRouter, HTTPException, Depends, UploadFile, Request, File
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import get_s3_storage_client, get_jwt_auth_manager
from database import UserProfileModel, UserModel, get_db
from exceptions import TokenExpiredError, InvalidTokenError
from schemas.profiles import ProfileCreateSchema
from security.http import get_token
from storages import S3StorageInterface

router = APIRouter()


@router.post("/users/{user_id}/profile", response_model=ProfileCreateSchema)
async def create_user_profile(
                              user_id: int,
                              user_data: ProfileCreateSchema,
                              db: AsyncSession = Depends(get_db),
                              token: str = Depends(get_token),
                              avatar: UploadFile = File(None),
                              jwt_manager = Depends(get_jwt_auth_manager),
                              s3_client: S3StorageInterface = Depends(get_s3_storage_client)
):
    try:
        payload = jwt_manager.decode_access_token(token)
    except (TokenExpiredError, InvalidTokenError):
        raise HTTPException(status_code=401, detail="Token has expired.")
    token_user_id = payload.get("sub")
    result = await db.execute(select(UserModel).where(
        UserModel.id == user_id
    ))
    user = result.scalar_one_or_none()
    if token_user_id != user_id and user.group.name != "admin":
        raise HTTPException(status_code=403, detail="You don't have permission to edit this profile.")
    if not user:
        raise HTTPException(status_code=401, detail="User not found or not active.")
    if not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or not active.")
    result_profile = await db.execute(select(UserProfileModel).where(
        UserProfileModel.user_id == token_user_id
    ))
    profile = result_profile.scalar_one_or_none()
    if profile:
        raise HTTPException(status_code=400, detail="User already has a profile.")
    avatar_url = None
    try:
        if avatar:
            avatar_filename = f"{user_id}_avatar.jpg"
            await s3_client.upload_file(
                avatar_filename,
                avatar.file.read()
            )
            avatar_url = f"http://minio-theater/avatars/{avatar_filename}"
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to upload avatar. Please try again later.")
    new_profile = UserProfileModel(
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        gender=user_data.gender,
        date_of_birth=user_data.date_of_birth,
        info=user_data.info,
        avatar=avatar_url
    )
    db.add(new_profile)
    await db.commit()
    await db.refresh(new_profile)
    return new_profile
