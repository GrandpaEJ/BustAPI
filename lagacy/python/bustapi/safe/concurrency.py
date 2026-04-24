"""
Concurrency helpers.
"""

import asyncio
from typing import Any, Awaitable


def py(coro: Awaitable[Any]) -> asyncio.Task:
    """
    Spawn a background task (fire-and-forget), similar to 'go func()'.

    Args:
        coro: The coroutine to run properly.

    Returns:
        The created asyncio.Task
    """
    task = asyncio.create_task(coro)

    # Ideally we should attach a done callback to log exceptions
    # so they aren't swallowed silently.
    def _handle_result(t: asyncio.Task):
        try:
            t.result()
        except asyncio.CancelledError:
            pass
        except Exception as e:
            # We can use the app logger if available, or just print
            print(f"❌ Background task failed: {e}")

    task.add_done_callback(_handle_result)
    return task
