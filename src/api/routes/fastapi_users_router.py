# current_active_user = fastapi_users_router.current_user(active=True)
# current_active_superuser = fastapi_users_router.current_user(
#     active=True, superuser=True
# )


# def require_admin(user: User = Depends(current_active_user)):
#     if user.role != "admin":
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Not authorized",
#         )
#     return user
#
#
# def require_employee(user: User = Depends(current_active_user)):
#     if user.role != Role.EMPLOYEE:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Not authorized",
#         )
#     return user
