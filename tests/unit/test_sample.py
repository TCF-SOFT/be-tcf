from src.utils.case_converter import camel_case_to_snake_case


def test_camel_case_to_snake_case_examples():
    assert camel_case_to_snake_case("SomeSDK") == "some_sdk"
    assert camel_case_to_snake_case("RServoDrive") == "r_servo_drive"
    assert camel_case_to_snake_case("SDKDemo") == "sdk_demo"
