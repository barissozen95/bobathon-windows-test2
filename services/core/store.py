"""Public store API (`store.reset()` is part of the test API, see ENGINEERING-HANDBOOK).

This name is an alias of `services.core.infrastructure.memory_store`: both resolve to the
same module object, so attribute writes here are seen by the application layer.
"""

import sys

from .infrastructure import memory_store

sys.modules[__name__] = memory_store
