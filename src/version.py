import os


def get_version():
    """The release tag baked into the image at build time (APP_VERSION)."""
    return os.getenv('APP_VERSION') or 'v0.0.0-dev'
