# import pytest
#
# from app.api.di.di import S3Service
# from app.api.di.di import URM
#
#
# @pytest.mark.parametrize(
#     "service_1, service_2",
#     [
#         (S3Service(), S3Service()),
#         (URM(), URM()),
#     ],
# )
# def test_singleton(service_1, service_2):
#     assert service_1 == service_2
#     assert id(service_1) == id(service_2)
