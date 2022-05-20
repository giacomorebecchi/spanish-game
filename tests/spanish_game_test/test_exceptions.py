from spanish_game.exceptions import InquiryException


def test_inquiry_exception():
    def helper():
        raise InquiryException({"a": "b"}, "Test exception")

    try:
        helper()
    except InquiryException as e:
        assert e.answers == {"a": "b"}
        assert e.message == "Test exception"
        assert e.__repr__() == "InquiryException('Test exception')"
