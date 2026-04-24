"""
Dependency injection system for BustAPI (FastAPI-compatible).
"""

import inspect
from functools import wraps
from typing import Any, Callable, Dict, Optional


class Depends:
    """
    Dependency injection marker (FastAPI-compatible).

    Use to inject dependencies into route handlers. Supports:
    - Simple callables
    - Generator-based dependencies (with cleanup via yield)
    - Async dependencies
    - Nested dependencies
    - Per-request caching

    Example:
        def get_db():
            db = Database()
            try:
                yield db
            finally:
                db.close()

        def get_current_user(token: str = Query(...)):
            if token == "secret":
                return {"id": 1, "name": "Alice"}
            abort(401, "Invalid token")

        @app.route("/profile")
        def get_profile(
            user = Depends(get_current_user),
            db = Depends(get_db)
        ):
            return {"user": user, "data": db.query("...")}

    Args:
        dependency: Callable that returns the dependency value
        use_cache: Cache the dependency value per request (default: True)
    """

    def __init__(self, dependency: Callable, use_cache: bool = True):
        self.dependency = dependency
        self.use_cache = use_cache
        self.is_generator = inspect.isgeneratorfunction(dependency)
        self.is_async_generator = inspect.isasyncgenfunction(dependency)
        self.is_coroutine = inspect.iscoroutinefunction(dependency)

    def __call__(self):
        """Make Depends callable for compatibility."""
        return self.dependency()

    def __repr__(self) -> str:
        dep_name = getattr(self.dependency, "__name__", str(self.dependency))
        return f"Depends({dep_name})"


class DependencyCache:
    """
    Per-request cache for resolved dependencies.

    Stores both dependency values and generators for cleanup.
    """

    def __init__(self):
        self.values: Dict[Callable, Any] = {}
        self.generators: Dict[Callable, Any] = {}

    def get(self, dependency: Callable) -> Optional[Any]:
        """Get cached dependency value."""
        return self.values.get(dependency)

    def set(self, dependency: Callable, value: Any):
        """Cache dependency value."""
        self.values[dependency] = value

    def add_generator(self, dependency: Callable, generator: Any):
        """Store generator for cleanup."""
        self.generators[dependency] = generator

    async def cleanup(self):
        """Cleanup all generators (call next/close)."""
        for gen in self.generators.values():
            try:
                if inspect.isasyncgen(gen):
                    try:
                        await gen.__anext__()
                    except StopAsyncIteration:
                        pass
                elif inspect.isgenerator(gen):
                    try:
                        next(gen)
                    except StopIteration:
                        pass
            except Exception:
                pass  # Ignore cleanup errors

    def cleanup_sync(self):
        """Cleanup all generators synchronously."""
        for gen in self.generators.values():
            try:
                if inspect.isgenerator(gen):
                    try:
                        next(gen)
                    except StopIteration:
                        pass
            except Exception:
                pass  # Ignore cleanup errors


async def resolve_dependency(
    depends: Depends, cache: DependencyCache, resolved_params: Dict[str, Any]
) -> Any:
    """
    Resolve a dependency, using cache if enabled.

    Args:
        depends: Depends instance to resolve
        cache: Dependency cache for this request
        resolved_params: Already resolved parameters (for nested deps)

    Returns:
        Resolved dependency value
    """
    # Check cache first
    if depends.use_cache:
        cached = cache.get(depends.dependency)
        if cached is not None:
            return cached

    # Resolve nested dependencies
    sig = inspect.signature(depends.dependency)
    dep_kwargs = {}

    for param_name, param in sig.parameters.items():
        if isinstance(param.default, Depends):
            # Nested dependency
            dep_kwargs[param_name] = await resolve_dependency(
                param.default, cache, resolved_params
            )
        elif param_name in resolved_params:
            # Use already resolved parameter (e.g., Query, Path)
            dep_kwargs[param_name] = resolved_params[param_name]

    # Call the dependency
    if depends.is_async_generator:
        gen = depends.dependency(**dep_kwargs)
        value = await gen.__anext__()
        cache.add_generator(depends.dependency, gen)
    elif depends.is_generator:
        gen = depends.dependency(**dep_kwargs)
        value = next(gen)
        cache.add_generator(depends.dependency, gen)
    elif depends.is_coroutine:
        value = await depends.dependency(**dep_kwargs)
    else:
        value = depends.dependency(**dep_kwargs)

    # Cache if enabled
    if depends.use_cache:
        cache.set(depends.dependency, value)

    return value


def resolve_dependency_sync(
    depends: Depends, cache: DependencyCache, resolved_params: Dict[str, Any]
) -> Any:
    """
    Resolve a dependency synchronously.

    Args:
        depends: Depends instance to resolve
        cache: Dependency cache for this request
        resolved_params: Already resolved parameters

    Returns:
        Resolved dependency value
    """
    # Check cache first
    if depends.use_cache:
        cached = cache.get(depends.dependency)
        if cached is not None:
            return cached

    # Resolve nested dependencies
    sig = inspect.signature(depends.dependency)
    dep_kwargs = {}

    for param_name, param in sig.parameters.items():
        if isinstance(param.default, Depends):
            # Nested dependency
            dep_kwargs[param_name] = resolve_dependency_sync(
                param.default, cache, resolved_params
            )
        elif param_name in resolved_params:
            # Use already resolved parameter
            dep_kwargs[param_name] = resolved_params[param_name]

    # Call the dependency (sync only)
    if depends.is_generator:
        gen = depends.dependency(**dep_kwargs)
        value = next(gen)
        cache.add_generator(depends.dependency, gen)
    else:
        value = depends.dependency(**dep_kwargs)

    # Cache if enabled
    if depends.use_cache:
        cache.set(depends.dependency, value)

    return value


__all__ = [
    "Depends",
    "DependencyCache",
    "resolve_dependency",
    "resolve_dependency_sync",
]
