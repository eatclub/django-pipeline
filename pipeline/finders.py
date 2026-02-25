from itertools import chain
from os.path import normpath

from django.contrib.staticfiles.finders import \
    AppDirectoriesFinder as DjangoAppDirectoriesFinder
from django.contrib.staticfiles.finders import BaseFinder, BaseStorageFinder
from django.contrib.staticfiles.finders import \
    FileSystemFinder as DjangoFileSystemFinder
from django.contrib.staticfiles.finders import find
from django.contrib.staticfiles.storage import staticfiles_storage
from django.utils._os import safe_join

from pipeline.conf import settings


def _call_find_compat(find_callable, path, find_all):
    """Call Django staticfiles find APIs across all/find_all renames."""
    try:
        return find_callable(path, find_all=find_all)
    except TypeError:
        return find_callable(path, all=find_all)


class PipelineFinder(BaseStorageFinder):
    storage = staticfiles_storage

    def find(self, path, all=False, find_all=None):
        # Django 5.2 renamed 'all' parameter to 'find_all'
        if find_all is not None:
            all = find_all
        if not settings.PIPELINE_ENABLED:
            return _call_find_compat(super(PipelineFinder, self).find, path, all)
        else:
            return []

    def list(self, ignore_patterns):
        return []


class ManifestFinder(BaseFinder):
    def find(self, path, all=False, find_all=None):
        """
        Looks for files in PIPELINE.STYLESHEETS and PIPELINE.JAVASCRIPT
        """
        # Django 5.2 renamed 'all' parameter to 'find_all'
        if find_all is not None:
            all = find_all
        matches = []
        for elem in chain(settings.STYLESHEETS.values(), settings.JAVASCRIPT.values()):
            if normpath(elem["output_filename"]) == normpath(path):
                match = safe_join(settings.PIPELINE_ROOT, path)
                if not all:
                    return match
                matches.append(match)
        return matches

    def list(self, *args):
        return []


class CachedFileFinder(BaseFinder):
    def find(self, path, all=False, find_all=None):
        """
        Work out the uncached name of the file and look that up instead
        """
        # Django 5.2 renamed 'all' parameter to 'find_all'
        if find_all is not None:
            all = find_all
        try:
            start, _, extn = path.rsplit(".", 2)
        except ValueError:
            return []
        path = ".".join((start, extn))
        return _call_find_compat(find, path, all) or []

    def list(self, *args):
        return []


class PatternFilterMixin(object):
    ignore_patterns = []

    def get_ignored_patterns(self):
        return list(set(self.ignore_patterns))

    def list(self, ignore_patterns):
        if ignore_patterns:
            ignore_patterns = ignore_patterns + self.get_ignored_patterns()
        return super(PatternFilterMixin, self).list(ignore_patterns)


class AppDirectoriesFinder(PatternFilterMixin, DjangoAppDirectoriesFinder):
    """
    Like AppDirectoriesFinder, but doesn't return any additional ignored
    patterns.

    This allows us to concentrate/compress our components without dragging
    the raw versions in via collectstatic.
    """

    ignore_patterns = [
        "*.js",
        "*.css",
        "*.less",
        "*.scss",
        "*.styl",
    ]


class FileSystemFinder(PatternFilterMixin, DjangoFileSystemFinder):
    """
    Like FileSystemFinder, but doesn't return any additional ignored patterns

    This allows us to concentrate/compress our components without dragging
    the raw versions in too.
    """

    ignore_patterns = [
        "*.js",
        "*.css",
        "*.less",
        "*.scss",
        "*.styl",
        "*.sh",
        "*.html",
        "*.md",
        "*.markdown",
        "*.php",
        "*.txt",
        "README*",
        "LICENSE*",
        "*examples*",
        "*test*",
        "*bin*",
        "*samples*",
        "*docs*",
        "*build*",
        "*demo*",
        "Makefile*",
        "Gemfile*",
        "node_modules",
    ]
