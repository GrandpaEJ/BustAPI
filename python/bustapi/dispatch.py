"""
Request dispatch and wrapping logic for BustAPI.
Includes fast-path optimizations for request processing.
"""

import inspect
from functools import wraps
from typing import TYPE_CHECKING, Callable

from .http.request import Request, _request_ctx

if TYPE_CHECKING:
    from .app import BustAPI


def create_turbo_wrapper(handler: Callable) -> Callable:
    """
    Zero-overhead wrapper for simple handlers.

    Skips: Request creation, context, sessions, middleware, parameter extraction.
    Use for handlers that take no arguments and return dict/list/str.
    """

    @wraps(handler)
    def wrapper(rust_request, path_params=None):
        # path_params is passed when using PyTypedTurboHandler for caching
        # but we ignore it since handler takes no arguments
        result = handler()
        if isinstance(result, dict):
            return (result, 200, {"Content-Type": "application/json"})
        elif isinstance(result, list):
            return (result, 200, {"Content-Type": "application/json"})
        elif isinstance(result, str):
            return (result, 200, {"Content-Type": "text/html; charset=utf-8"})
        elif isinstance(result, tuple):
            return result
        else:
            return (str(result), 200, {})

    return wrapper


def create_typed_turbo_wrapper(handler: Callable, param_names: list) -> Callable:
    """
    Turbo wrapper for handlers with typed path parameters.

    Path parameters are extracted and converted in Rust for maximum performance.
    The handler receives params as keyword arguments.

    Args:
        handler: The user's handler function
        param_names: List of parameter names in order (e.g., ["id", "name"])

    Note:
        - No request object available (use regular @app.route for that)
        - No middleware, sessions, or auth support
        - Only path params, no query params yet
    """

    @wraps(handler)
    def wrapper(rust_request, path_params: dict):
        # path_params already parsed and typed by Rust (e.g., {"id": 123})
        try:
            result = handler(**path_params)
        except TypeError as e:
            # Handler signature mismatch
            return (
                {"error": f"Handler parameter mismatch: {e}"},
                500,
                {"Content-Type": "application/json"},
            )

        if isinstance(result, dict):
            return (result, 200, {"Content-Type": "application/json"})
        elif isinstance(result, list):
            return (result, 200, {"Content-Type": "application/json"})
        elif isinstance(result, str):
            return (result, 200, {"Content-Type": "text/html; charset=utf-8"})
        elif isinstance(result, tuple):
            return result
        else:
            return (str(result), 200, {})

    return wrapper


def create_sync_wrapper(app: "BustAPI", handler: Callable, rule: str) -> Callable:
    """Wrap handler with request context, middleware, and path param support."""

    # Inspect handler signature to filter kwargs later
    try:
        sig = inspect.signature(handler)
        has_kwargs = any(
            p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values()
        )
        expected_args = set(sig.parameters.keys())
    except (ValueError, TypeError):
        # Fallback for builtins or weird callables
        has_kwargs = True
        expected_args = set()

    @wraps(handler)
    def wrapper(rust_request, path_params=None):
        """Synchronous wrapper for route handlers.

        Args:
            rust_request: The Rust request object
            path_params: Pre-extracted path params from Rust (optional, for performance)
        """
        try:
            # 1. Context and Request Initialization (Fast Path)
            request = Request._from_rust_request(rust_request)
            request.app = app
            token = _request_ctx.set(request)

            # 2. Session Initialization
            session = None
            if app.secret_key:
                session = app.session_interface.open_session(app, request)
                request.session = session

            # 3. Before Request Hooks
            if app.before_request_funcs:
                for before_func in app.before_request_funcs:
                    res = before_func()
                    if res is not None:
                        response = app._make_response(res)
                        if session:
                            app.session_interface.save_session(app, session, response)
                        _request_ctx.reset(token)
                        return app._response_to_rust_format(response)

            # 4. Main Request Processing (Branching based on Middleware presence)
            if app.middleware_manager.middlewares:
                # PATH WITH MIDDLEWARE
                mw_response = app.middleware_manager.process_request(request)
                if mw_response:
                    response = mw_response
                else:
                    # Parameter Extraction - use Rust-extracted params if available
                    if path_params is not None:
                        kwargs = dict(path_params)  # Use Rust-extracted params (FAST)
                        # Still need to validate against Path constraints
                        kwargs = app._validate_path_params(rule, request.method, kwargs)
                    else:
                        args, kwargs = app._extract_path_params(
                            rule, request.method, request.path
                        )
                    kwargs.update(app._extract_query_params(rule, request))
                    if request.method in ("POST", "PUT", "PATCH"):
                        kwargs.update(app._extract_body_params(rule, request))

                    dep_kwargs, dep_cache = app._resolve_dependencies(
                        rule, request.method, kwargs
                    )
                    kwargs.update(dep_kwargs)

                    # Auto-inject from query for compatibility
                    for name in expected_args:
                        if name not in kwargs and name in request.args:
                            kwargs[name] = request.args.get(name)

                    call_kwargs = (
                        kwargs
                        if has_kwargs
                        else {k: v for k, v in kwargs.items() if k in expected_args}
                    )

                    try:
                        result = handler(**call_kwargs)
                    finally:
                        if dep_cache:
                            dep_cache.cleanup_sync()

                    response = (
                        app._make_response(result)
                        if not isinstance(result, tuple)
                        else app._make_response(*result)
                    )
            else:
                # PATH WITHOUT MIDDLEWARE (ULTRA-FAST)
                if "<" not in rule and not expected_args and path_params is None:
                    result = handler()
                    dep_cache = None
                else:
                    # Use Rust-extracted params if available
                    if path_params is not None:
                        kwargs = dict(path_params)  # FAST PATH - Rust-extracted
                        # Still need to validate against Path constraints
                        kwargs = app._validate_path_params(rule, request.method, kwargs)
                    elif "<" not in rule:
                        kwargs = {}
                    else:
                        args, kwargs = app._extract_path_params(
                            rule, request.method, request.path
                        )

                    kwargs.update(app._extract_query_params(rule, request))
                    if request.method in ("POST", "PUT", "PATCH"):
                        kwargs.update(app._extract_body_params(rule, request))
                    dep_kwargs, dep_cache = app._resolve_dependencies(
                        rule, request.method, kwargs
                    )
                    kwargs.update(dep_kwargs)

                    for name in expected_args:
                        if name not in kwargs and name in request.args:
                            kwargs[name] = request.args.get(name)

                    call_kwargs = (
                        kwargs
                        if has_kwargs
                        else {k: v for k, v in kwargs.items() if k in expected_args}
                    )

                    try:
                        result = handler(**call_kwargs)
                    finally:
                        if dep_cache:
                            dep_cache.cleanup_sync()

                # Optimization: Skip Response object if possible
                if session is None and not app.after_request_funcs:
                    if isinstance(result, (dict, list, str, bytes)):
                        # Pass directly to Rust. JSON serialization handled by Rust if dict/list.
                        ct = (
                            "application/json"
                            if isinstance(result, (dict, list))
                            else (
                                "text/html"
                                if isinstance(result, str)
                                else "application/octet-stream"
                            )
                        )
                        return (result, 200, {"Content-Type": ct})

                response = (
                    app._make_response(result)
                    if not isinstance(result, tuple)
                    else app._make_response(*result)
                )

            # 5. Pipeline Cleanup and Hooks
            if app.middleware_manager.middlewares:
                response = app.middleware_manager.process_response(request, response)
            if app.after_request_funcs:
                for after_func in app.after_request_funcs:
                    response = after_func(response) or response
            if session is not None:
                app.session_interface.save_session(app, session, response)

            return app._response_to_rust_format(response)

        except Exception as e:
            return app._response_to_rust_format(app._handle_exception(e))
        finally:
            if app.teardown_request_funcs:
                for f in app.teardown_request_funcs:
                    try:
                        f(None)
                    except:
                        pass
            _request_ctx.reset(token)

    return wrapper


def create_async_wrapper(app: "BustAPI", handler: Callable, rule: str) -> Callable:
    """Wrap asynchronous handler; executed synchronously via asyncio.run for now."""

    # Inspect handler signature to filter kwargs later
    try:
        sig = inspect.signature(handler)
        has_kwargs = any(
            p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values()
        )
        expected_args = set(sig.parameters.keys())
    except (ValueError, TypeError):
        # Fallback for builtins or weird callables
        has_kwargs = True
        expected_args = set()

    @wraps(handler)
    async def wrapper(rust_request):
        try:
            request = Request._from_rust_request(rust_request)
            request.app = app
            token = _request_ctx.set(request)

            session = None
            if app.secret_key:
                session = app.session_interface.open_session(app, request)
                request.session = session

            if app.before_request_funcs:
                for before_func in app.before_request_funcs:
                    res = before_func()
                    if res is not None:
                        response = app._make_response(res)
                        if session:
                            app.session_interface.save_session(app, session, response)
                        _request_ctx.reset(token)
                        return app._response_to_rust_format(response)

            if app.middleware_manager.middlewares:
                mw_response = app.middleware_manager.process_request(request)
                if mw_response:
                    response = mw_response
                else:
                    args, kwargs = app._extract_path_params(
                        rule, request.method, request.path
                    )
                    kwargs.update(app._extract_query_params(rule, request))
                    if request.method in ("POST", "PUT", "PATCH"):
                        kwargs.update(app._extract_body_params(rule, request))

                    dep_kwargs, dep_cache = await app._resolve_dependencies_async(
                        rule, request.method, kwargs
                    )
                    kwargs.update(dep_kwargs)

                    for name in expected_args:
                        if name not in kwargs and name in request.args:
                            kwargs[name] = request.args.get(name)

                    call_kwargs = (
                        kwargs
                        if has_kwargs
                        else {k: v for k, v in kwargs.items() if k in expected_args}
                    )

                    try:
                        result = await handler(**call_kwargs)
                    finally:
                        if dep_cache:
                            await dep_cache.cleanup()

                    response = (
                        app._make_response(result)
                        if not isinstance(result, tuple)
                        else app._make_response(*result)
                    )
            else:
                if "<" not in rule and not expected_args:
                    result = await handler()
                    dep_cache = None
                else:
                    if "<" not in rule:
                        kwargs = app._extract_query_params(rule, request)
                        if request.method in ("POST", "PUT", "PATCH"):
                            kwargs.update(app._extract_body_params(rule, request))
                        dep_kwargs, dep_cache = await app._resolve_dependencies_async(
                            rule, request.method, kwargs
                        )
                        kwargs.update(dep_kwargs)
                    else:
                        args, kwargs = app._extract_path_params(
                            rule, request.method, request.path
                        )
                        kwargs.update(app._extract_query_params(rule, request))
                        if request.method in ("POST", "PUT", "PATCH"):
                            kwargs.update(app._extract_body_params(rule, request))
                        dep_kwargs, dep_cache = await app._resolve_dependencies_async(
                            rule, request.method, kwargs
                        )
                        kwargs.update(dep_kwargs)

                    for name in expected_args:
                        if name not in kwargs and name in request.args:
                            kwargs[name] = request.args.get(name)

                    call_kwargs = (
                        kwargs
                        if has_kwargs
                        else {k: v for k, v in kwargs.items() if k in expected_args}
                    )

                    try:
                        result = await handler(**call_kwargs)
                    finally:
                        if dep_cache:
                            await dep_cache.cleanup()

                if session is None and not app.after_request_funcs:
                    if isinstance(result, (dict, list, str, bytes)):
                        ct = (
                            "application/json"
                            if isinstance(result, (dict, list))
                            else (
                                "text/html"
                                if isinstance(result, str)
                                else "application/octet-stream"
                            )
                        )
                        return (result, 200, {"Content-Type": ct})

                response = (
                    app._make_response(result)
                    if not isinstance(result, tuple)
                    else app._make_response(*result)
                )

            if app.middleware_manager.middlewares:
                response = app.middleware_manager.process_response(request, response)
            if app.after_request_funcs:
                for after_func in app.after_request_funcs:
                    response = after_func(response) or response
            if session is not None:
                app.session_interface.save_session(app, session, response)

            return app._response_to_rust_format(response)

        except Exception as e:
            return app._response_to_rust_format(app._handle_exception(e))
        finally:
            if app.teardown_request_funcs:
                for f in app.teardown_request_funcs:
                    try:
                        f(None)
                    except:
                        pass
            _request_ctx.reset(token)

    return wrapper
