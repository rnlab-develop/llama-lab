import google.auth
import google.auth.transport.requests


def get_gcp_token() -> str:
    try:
        print("*****************GETTING CREDS")
        creds = google.auth.default()[0]
        print("*****************IS THIS VALID", creds.valid)
    except Exception as e:
        raise e
    if not creds.token or not creds.valid:
        print("refreshing the token!!")
        try:
            creds.refresh(google.auth.transport.requests.Request())
        except Exception as e:
            raise e
    return creds.token
