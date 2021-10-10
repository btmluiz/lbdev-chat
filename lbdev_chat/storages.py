from storages.backends.gcloud import GoogleCloudStorage


class StaticGoogleCloudStorage(GoogleCloudStorage):
    def __init__(self, location="static", **settings):
        super().__init__(location=location, **settings)


class MediaGoogleCloudStorage(GoogleCloudStorage):
    def __init__(self, location="media", **settings):
        super().__init__(location=location, **settings)

