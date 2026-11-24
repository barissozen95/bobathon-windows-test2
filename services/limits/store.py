"""Public store API; alias of `services.limits.infrastructure.memory_store` (same module object)."""

import sys

from .infrastructure import memory_store

sys.modules[__name__] = memory_store
