from enum import Enum


class DatabaseTables(str, Enum):
    """
    Enum for database table names.
    """

    USUARIOS = "usuarios"
    FILE_REGISTRY = "file_registry"
    WORKER_JOBS = "worker_example_jobs"
