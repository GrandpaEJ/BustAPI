"""
FastAPI compatibility layer for BustAPI.
Provides Header, Cookie, Form, File, and BackgroundTasks.
"""

from typing import Any, Callable, Dict, List, Optional, Pattern, Union

from .params import Body, Query


# Re-use Query logic for Header and Cookie as they are string-based
class Header(Query):
    """
    Header parameter validator.
    """

    def __init__(
        self,
        default: Any = ...,
        *,
        alias: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        convert_underscores: bool = True,
        **kwargs,
    ):
        super().__init__(
            default=default, alias=alias, title=title, description=description, **kwargs
        )
        self.convert_underscores = convert_underscores


class Cookie(Query):
    """
    Cookie parameter validator.
    """

    pass


class Form(Body):
    """
    Form parameter validator.
    """

    def __init__(
        self,
        default: Any = ...,
        *,
        media_type: str = "application/x-www-form-urlencoded",
        **kwargs,
    ):
        super().__init__(default=default, media_type=media_type, **kwargs)


class File(Form):
    """
    File parameter validator.
    """

    def __init__(
        self, default: Any = ..., *, media_type: str = "multipart/form-data", **kwargs
    ):
        super().__init__(default=default, media_type=media_type, **kwargs)


class UploadFile:
    """
    Wrapper for uploaded files to look like Starlette/FastAPI UploadFile.
    """

    def __init__(self, filename: str, content_type: str, file_obj: Any):
        self.filename = filename
        self.content_type = content_type
        self.file = file_obj
        self._headers = None

    @property
    def headers(self):
        if self._headers is None:
            self._headers = {
                "content-type": self.content_type,
                "content-disposition": (
                    f'form-data; name="file"; filename="{self.filename}"'
                ),
            }
        return self._headers

    async def read(self, size: int = -1) -> bytes:
        return self.file.read(size)

    async def seek(self, offset: int) -> None:
        self.file.seek(offset)

    async def close(self) -> None:
        self.file.close()


class BackgroundTasks:
    """
    Background task manager.
    """

    def __init__(self, tasks: Optional[List[Any]] = None):
        self.tasks: List[tuple] = []
        if tasks:
            for task in tasks:
                self.tasks.append((task, (), {}))

    def add_task(self, func: Callable, *args: Any, **kwargs: Any) -> None:
        """
        Add a task to be run in the background.
        """
        self.tasks.append((func, args, kwargs))

    async def __call__(self) -> None:
        """
        Execute all tasks.
        """
        for func, args, kwargs in self.tasks:
            try:
                if callable(func):
                    import inspect

                    if inspect.iscoroutinefunction(func):
                        await func(*args, **kwargs)
                    else:
                        func(*args, **kwargs)
            except Exception as e:
                # Log error but don't stop other tasks
                print(f"Error in background task: {e}")
