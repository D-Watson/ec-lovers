
class ErrorCode:
    SUCCESS = (200, "success")
    PARAM_ERR = (2000, "param error")
    DB_ERR = (2001, "db error")

    REDIS_KEY_NOT_EXISTS = (2005, "[redis] key not exists.")
    REDIS_ERR = (2008, "[redis] system err")
    COS_UPLOAD_ERR = (2002, "tencent cos upload file error.")
    COS_DOWNLOAD_ERR = (2003, "tencent cos download error.")

    # image generate error
    IMAGE_GENERATE_ERR = (2004, "doubao image generate error.")

    # auth error
    PASSWORD_ERR = (2006, "user password wrong.")
    TOKEN_EXPIRED = (2007, "auth token expired.")

    # email
    EMAIL_TOKEN_ERR = (2009, "email token error.")

    # user
    USER_NOT_FOUND = (3001, "user not found.")

    @classmethod
    def get_message(cls, code: int) -> str:
        for attr in dir(cls):
            value = getattr(cls, attr)
            if isinstance(value, tuple) and len(value) == 2 and value[0] == code:
                return value[1]
        return "未知错误"

    @classmethod
    def get_code_and_msg(cls, attr_name: str) -> tuple[int, str]:
        value = getattr(cls, attr_name, None)
        if isinstance(value, tuple) and len(value) == 2:
            return value
        raise AttributeError(f"错误码 {attr_name} 未定义")


class ServiceError(Exception):
    def __init__(self, code: ErrorCode):
        self.err_code, self.err_msg = code
        super(ServiceError, self).__init__(f"Error Code: {self.err_code}, Message: {self.err_msg}")

    def __str__(self):
        return f"Error Code: {self.err_code}, Message: {self.err_msg}"
