import google.auth


def get_gcp_token() -> str:
    try:
        creds = google.auth.default()[0]
    except Exception as e:
        raise e
    if not creds.token:
        try:
            creds.refresh(google.auth.transport.requests.Request())
        except Exception as e:
            raise e
    return creds.token
