from fastapi import Request

from common.services.s3_service import S3Service


def get_s3_service(request: Request) -> S3Service:
    """
    Dependency to get the S3 service instance from the request state.
    This allows for easy access to the S3 service in route handlers.
    Inited in the main app.
    """
    return request.app.state.s3
