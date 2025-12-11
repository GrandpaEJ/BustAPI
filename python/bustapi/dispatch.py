"""
Request dispatch and wrapping logic for BustAPI.
Includes fast-path optimizations for request processing.
"""

from functools import wraps
from typing import TYPE_CHECKING, Callable

from .http.request import Request, _request_ctx

if TYPE_CHECKING:
    from .app import BustAPI


def create_sync_wrapper(app: "BustAPI", handler: Callable, rule: str) -> Callable:
    """Wrap handler with request context, middleware, and path param support."""

    @wraps(handler)
    def wrapper(rust_request):
        try:
            # Fast Path: Check optimizations
            # Note: accessing attributes on self is fast, but local vars are faster.
            # In a real "compile" step we would bake these, but for now dynamic checks
            # with early exits are improved.

            # Convert Rust request to Python Request object
            request = Request._from_rust_request(rust_request)
            request.app = app

            # Context is needed for proxies
            token = _request_ctx.set(request)

            # --- SESSION HANDLING ---
            # Only process sessions if we have a secret_key (implied valid interface)
            # and the interface isn't a NullSession (optimization)
            session = None
            if app.secret_key:
                session = app.session_interface.open_session(app, request)
                request.session = session

            # --- BEFORE REQUEST ---
            if app.before_request_funcs:
                for before_func in app.before_request_funcs:
                    result = before_func()
                    if result is not None:
                        response = app._make_response(result)
                        if session:
                            app.session_interface.save_session(app, session, response)
                        _request_ctx.reset(token)
                        return app._response_to_rust_format(response)

            # --- MIDDLEWARE REQUEST ---
            # Direct check on list length is faster than method call
            if app.middleware_manager.middlewares:
                mw_response = app.middleware_manager.process_request(request)
                if mw_response:
                    response = mw_response
                else:
                    args, kwargs = app._extract_path_params(rule, request.path)
                    # Extract and merge query parameters
                    query_kwargs = app._extract_query_params(rule, request)
                    kwargs.update(query_kwargs)
                    result = handler(**kwargs)
                    response = app._make_response(
                        result if not isinstance(result, tuple) else result[0]
                    )
                    if isinstance(result, tuple) and len(result) > 1:
                        # Re-wrap if tuple was expanded for make_response
                        # actually _make_response handles tuples, but the optimized line above
                        # tried to be clever. Let's revert to standard for correctness unless verified.
                        pass

                    # Wait, let's keep the original logic for result to response but optimized
                    if isinstance(result, tuple):
                        response = app._make_response(*result)
                    else:
                        response = app._make_response(result)
            else:
                # NO MIDDLEWARE PATH (FAST)
                # Optimization: Skip param extraction for static routes
                # (We know it matches because Rust router sent it here)
                if "<" not in rule:
                    result = handler()
                else:
                    args, kwargs = app._extract_path_params(rule, request.path)
                    # Extract and merge query parameters
                    query_kwargs = app._extract_query_params(rule, request)
                    kwargs.update(query_kwargs)
                    result = handler(**kwargs)

                # OPTIMIZATION: Bypass Response object creation for common types
                # Only if we don't need to save session or run after_request hooks
                if session is None and not app.after_request_funcs:
                    if isinstance(result, str):
                        return (result, 200, {})
                    elif isinstance(result, bytes):
                        return (result.decode("utf-8", "replace"), 200, {})
                    elif isinstance(result, dict):
                        import json

                        return (
                            json.dumps(result),
                            200,
                            {"Content-Type": "application/json"},
                        )

                # Fallback for other types or tuples
                if isinstance(result, tuple):
                    response = app._make_response(*result)
                else:
                    response = app._make_response(result)

            # --- MIDDLEWARE RESPONSE ---
            if app.middleware_manager.middlewares:
                response = app.middleware_manager.process_response(request, response)

            # --- AFTER REQUEST ---
            if app.after_request_funcs:
                for after_func in app.after_request_funcs:
                    response = after_func(response) or response

            # --- SAVE SESSION ---
            if session is not None:
                app.session_interface.save_session(app, session, response)

            # Convert to Rust format (inline optimizations possible here?)
            return app._response_to_rust_format(response)

        except Exception as e:
            error_response = app._handle_exception(e)
            return app._response_to_rust_format(error_response)
        finally:
            # Optimized teardown
            if app.teardown_request_funcs:
                for teardown_func in app.teardown_request_funcs:
                    try:
                        teardown_func(None)
                    except Exception:
                        pass

            # Context reset
            if "token" in locals():
                _request_ctx.reset(token)
            else:
                _request_ctx.set(None)

    return wrapper


def create_async_wrapper(app: "BustAPI", handler: Callable, rule: str) -> Callable:
    """Wrap asynchronous handler; executed synchronously via asyncio.run for now."""

    @wraps(handler)
    async def wrapper(rust_request):
        try:
            # Convert Rust request to Python Request object
            request = Request._from_rust_request(rust_request)
            request.app = app

            token = _request_ctx.set(request)

            # Open Session
            session = None
            if app.secret_key:
                session = app.session_interface.open_session(app, request)
                request.session = session

            # Run before request handlers
            if app.before_request_funcs:
                for before_func in app.before_request_funcs:
                    result = before_func()
                    if result is not None:
                        response = app._make_response(result)
                        if session:
                            app.session_interface.save_session(app, session, response)
                        _request_ctx.reset(token)
                        return app._response_to_rust_format(response)

            # Middleware: Process Request
            if app.middleware_manager.middlewares:
                mw_response = app.middleware_manager.process_request(request)
                if mw_response:
                    response = mw_response
                else:
                    # Extract path params
                    args, kwargs = app._extract_path_params(rule, request.path)
                    # Extract and merge query parameters
                    query_kwargs = app._extract_query_params(rule, request)
                    kwargs.update(query_kwargs)
                    result = await handler(**kwargs)

                    if isinstance(result, tuple):
                        response = app._make_response(*result)
                    else:
                        response = app._make_response(result)
            else:
                # NO MIDDLEWARE PATH (FAST)
                if "<" not in rule:
                    result = await handler()
                else:
                    args, kwargs = app._extract_path_params(rule, request.path)
                    # Extract and merge query parameters
                    query_kwargs = app._extract_query_params(rule, request)
                    kwargs.update(query_kwargs)
                    result = await handler(**kwargs)

                # OPTIMIZATION: Bypass Response object creation for common types
                # Only if we don't need to save session or run after_request hooks
                if session is None and not app.after_request_funcs:
                    if isinstance(result, str):
                        return (result, 200, {})
                    elif isinstance(result, bytes):
                        return (result.decode("utf-8", "replace"), 200, {})
                    elif isinstance(result, dict):
                        import json

                        return (
                            json.dumps(result),
                            200,
                            {"Content-Type": "application/json"},
                        )

                # Fallback for other types or tuples
                if isinstance(result, tuple):
                    response = app._make_response(*result)
                else:
                    response = app._make_response(result)

            # Middleware: Process Response
            if app.middleware_manager.middlewares:
                response = app.middleware_manager.process_response(request, response)

            # Run after request handlers
            if app.after_request_funcs:
                for after_func in app.after_request_funcs:
                    response = after_func(response) or response

            # Save Session
            if session is not None:
                app.session_interface.save_session(app, session, response)

            # Convert Python Response to dict/tuple for Rust
            return app._response_to_rust_format(response)

        except Exception as e:
            # Handle errors
            error_response = app._handle_exception(e)
            return app._response_to_rust_format(error_response)
        finally:
            # Teardown handlers
            if app.teardown_request_funcs:
                for teardown_func in app.teardown_request_funcs:
                    try:
                        teardown_func(None)
                    except Exception:
                        pass

            if "token" in locals():
                _request_ctx.reset(token)
            else:
                _request_ctx.set(None)

    return wrapper
