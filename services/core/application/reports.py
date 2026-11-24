"""Reporting use cases."""

from services.core.infrastructure import archive, transfer_log


def find_transfers_by_owner(owner: str) -> list[dict]:
    return transfer_log.find_by_owner(owner)


def archive_statements(filename: str) -> int:
    return archive.archive_reports(filename)
