from minio import Minio


class StorageService:
    def __init__(self, settings):
        self.settings = settings
        self.client = None

    async def start(self):
        if self.settings.STORAGE_PROVIDER != "minio":
            raise Exception("Storage provider not supported")

        self.client = Minio(
            self.settings.MINIO_ENDPOINT,
            access_key=self.settings.MINIO_ACCESS_KEY,
            secret_key=self.settings.MINIO_SECRET_KEY,
            secure=self.settings.MINIO_SECURE,
        )

        found = self.client.bucket_exists(self.settings.STORAGE_BUCKET)

        if not found:
            self.client.make_bucket(self.settings.STORAGE_BUCKET)

    # 🔥 DESCARGAR (clave para workers)
    async def download_file(self, object_name: str, file_path: str):
        self.client.fget_object(
            self.settings.STORAGE_BUCKET,
            object_name,
            file_path,
        )
