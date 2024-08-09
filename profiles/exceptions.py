from rest_framework.exceptions import APIException


class ProfileNotFound(APIException):
    status_code = 404
    default_detail = "The requested profile does not exist"

class NotYorProfile(APIException):
    status_code = 403
    default_detail = "You can't edit a profile that does't belong to you"