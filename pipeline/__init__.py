try:
    from importlib.metadata import PackageNotFoundError, version
except ImportError:  # pragma: no cover
    # Python < 3.8 fallback when backport is available.
    try:
        from importlib_metadata import PackageNotFoundError, version
    except ImportError:  # pragma: no cover
        PackageNotFoundError = Exception

        def version(_name):
            raise PackageNotFoundError

try:
    __version__ = version("django-pipeline")
except PackageNotFoundError:
    # package is not installed
    __version__ = None
