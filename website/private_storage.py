from django.conf import settings
from django.core.files.storage import FileSystemStorage


class FlightMatchStorage(FileSystemStorage):
    """Uploads are outside MEDIA_ROOT and have no public URL."""

    def __init__(self):
        super().__init__(location=settings.BASE_DIR / 'private_uploads', base_url=None)

    def url(self, name):
        raise ValueError('Flight match documents are not public.')


flight_match_storage = FlightMatchStorage()
