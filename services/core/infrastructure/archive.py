"""Statement archiving: packs the reports directory into a .tgz without invoking a shell."""

import os
import tarfile

from services.core import config
from services.core.domain.errors import ValidationFailed

REPORTS_DIR = "reports"


def archive_reports(filename: str) -> int:
    """Write <ARCHIVE_DIR>/<filename>.tgz.

    `filename` is validated at the API layer (no path separators, no `..`); the resolved
    target is checked again here so a bypass cannot escape ARCHIVE_DIR.
    """
    archive_dir = os.path.realpath(config.ARCHIVE_DIR)
    target = os.path.realpath(os.path.join(archive_dir, f"{filename}.tgz"))
    if os.path.dirname(target) != archive_dir:
        raise ValidationFailed("Geçersiz dosya adı")
    with tarfile.open(target, "w:gz") as tar:
        tar.add(REPORTS_DIR)
    return 0
