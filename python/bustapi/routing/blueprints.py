"""
Blueprint support for BustAPI - Flask-compatible blueprints
"""

from typing import Any, Callable, Dict, List, Optional, Tuple, Union


class Blueprint:
    """
    Flask-compatible blueprint for organizing routes.

    Blueprints allow you to organize related routes and other functionality
    into reusable components that can be registered with an application.

    Example:
        bp = Blueprint('api', __name__, url_prefix='/api')

        @bp.route('/users')
        def get_users():
            return {'users': []}

        app.register_blueprint(bp)
    """

    def __init__(
        self,
        name: str,
        import_name: str,
        static_folder: Optional[str] = None,
        static_url_path: Optional[str] = None,
        template_folder: Optional[str] = None,
        url_prefix: Optional[str] = None,
        subdomain: Optional[str] = None,
        url_defaults: Optional[Dict[str, Any]] = None,
        root_path: Optional[str] = None,
        cli_group: Optional[str] = None,
    ):
        """
        Initialize blueprint.

        Args:
            name: Blueprint name
            import_name: Import name (usually __name__)
            static_folder: Static files folder
            static_url_path: Static files URL path
            template_folder: Template folder
            url_prefix: URL prefix for all routes
            subdomain: Subdomain for blueprint
            url_defaults: Default values for URL parameters
            root_path: Root path
            cli_group: CLI group name
        """
        self.name = name
        self.import_name = import_name
        self.static_folder = static_folder
        self.static_url_path = static_url_path
        self.template_folder = template_folder
        self.url_prefix = url_prefix
        self.subdomain = subdomain
        self.url_defaults = url_defaults or {}
        self.root_path = root_path
        self.cli_group = cli_group

        # Deferred functions to be registered when blueprint is registered with app
        self.deferred_functions: List[Tuple[str, str, Callable, List[str]]] = []

        # Error handlers
        self.error_handler_spec: Dict[Union[int, type], Callable] = {}

        # Before/after request handlers
        self.before_request_funcs: List[Callable] = []
        self.after_request_funcs: List[Callable] = []
        self.teardown_request_funcs: List[Callable] = []

        # Before/after app request handlers (for all requests)
        self.before_app_request_funcs: List[Callable] = []
        self.after_app_request_funcs: List[Callable] = []
        self.teardown_app_request_funcs: List[Callable] = []

        # Template context processors
        self.app_context_processor_funcs: List[Callable] = []
        self.context_processor_funcs: List[Callable] = []

    def route(self, rule: str, **options) -> Callable:
        """
        Blueprint route decorator (Flask-compatible).

        Args:
            rule: URL rule
            **options: Route options including methods, defaults, etc.

        Returns:
            Decorator function
        """

        def decorator(f: Callable) -> Callable:
            endpoint = options.pop("endpoint", f.__name__)
            methods = options.pop("methods", ["GET"])

            # Store route info for later registration
            self.deferred_functions.append((rule, endpoint, f, methods))
            return f

        return decorator

    def get(self, rule: str, **options) -> Callable:
        """Convenience decorator for GET routes."""
        return self.route(rule, methods=["GET"], **options)

    def post(self, rule: str, **options) -> Callable:
        """Convenience decorator for POST routes."""
        return self.route(rule, methods=["POST"], **options)

    def put(self, rule: str, **options) -> Callable:
        """Convenience decorator for PUT routes."""
        return self.route(rule, methods=["PUT"], **options)

    def delete(self, rule: str, **options) -> Callable:
        """Convenience decorator for DELETE routes."""
        return self.route(rule, methods=["DELETE"], **options)

    def patch(self, rule: str, **options) -> Callable:
        """Convenience decorator for PATCH routes."""
        return self.route(rule, methods=["PATCH"], **options)

    def head(self, rule: str, **options) -> Callable:
        """Convenience decorator for HEAD routes."""
        return self.route(rule, methods=["HEAD"], **options)

    def options(self, rule: str, **options) -> Callable:
        """Convenience decorator for OPTIONS routes."""
        return self.route(rule, methods=["OPTIONS"], **options)

    def before_request(self, f: Callable) -> Callable:
        """
        Register function to run before each request to this blueprint.

        Args:
            f: Function to run before request

        Returns:
            The original function
        """
        self.before_request_funcs.append(f)
        return f

    def after_request(self, f: Callable) -> Callable:
        """
        Register function to run after each request to this blueprint.

        Args:
            f: Function to run after request

        Returns:
            The original function
        """
        self.after_request_funcs.append(f)
        return f

    def teardown_request(self, f: Callable) -> Callable:
        """
        Register function to run after each request to this blueprint,
        even if an exception occurred.

        Args:
            f: Function to run on teardown

        Returns:
            The original function
        """
        self.teardown_request_funcs.append(f)
        return f

    def before_app_request(self, f: Callable) -> Callable:
        """
        Register function to run before every request to the application.

        Args:
            f: Function to run before request

        Returns:
            The original function
        """
        self.before_app_request_funcs.append(f)
        return f

    def after_app_request(self, f: Callable) -> Callable:
        """
        Register function to run after every request to the application.

        Args:
            f: Function to run after request

        Returns:
            The original function
        """
        self.after_app_request_funcs.append(f)
        return f

    def teardown_app_request(self, f: Callable) -> Callable:
        """
        Register function to run after every request to the application,
        even if an exception occurred.

        Args:
            f: Function to run on teardown

        Returns:
            The original function
        """
        self.teardown_app_request_funcs.append(f)
        return f

    def errorhandler(self, code_or_exception: Union[int, type]) -> Callable:
        """
        Register error handler for HTTP status codes or exceptions.

        Args:
            code_or_exception: HTTP status code or exception class

        Returns:
            Decorator function
        """

        def decorator(f: Callable) -> Callable:
            self.error_handler_spec[code_or_exception] = f
            return f

        return decorator

    def app_errorhandler(self, code_or_exception: Union[int, type]) -> Callable:
        """
        Register application-wide error handler.

        Args:
            code_or_exception: HTTP status code or exception class

        Returns:
            Decorator function
        """

        def decorator(f: Callable) -> Callable:
            # This will be registered with the app when blueprint is registered
            self.error_handler_spec[f"app_{code_or_exception}"] = f
            return f

        return decorator

    def context_processor(self, f: Callable) -> Callable:
        """
        Register template context processor for this blueprint.

        Args:
            f: Context processor function

        Returns:
            The original function
        """
        self.context_processor_funcs.append(f)
        return f

    def app_context_processor(self, f: Callable) -> Callable:
        """
        Register application-wide template context processor.

        Args:
            f: Context processor function

        Returns:
            The original function
        """
        self.app_context_processor_funcs.append(f)
        return f

    def url_value_preprocessor(self, f: Callable) -> Callable:
        """
        Register URL value preprocessor for this blueprint.

        Args:
            f: Preprocessor function

        Returns:
            The original function
        """
        # TODO: Implement URL value preprocessing
        return f

    def url_defaults(self, f: Callable) -> Callable:
        """
        Register URL defaults function for this blueprint.

        Args:
            f: URL defaults function

        Returns:
            The original function
        """
        # TODO: Implement URL defaults
        return f

    def app_url_value_preprocessor(self, f: Callable) -> Callable:
        """
        Register application-wide URL value preprocessor.

        Args:
            f: Preprocessor function

        Returns:
            The original function
        """
        # TODO: Implement app URL value preprocessing
        return f

    def app_url_defaults(self, f: Callable) -> Callable:
        """
        Register application-wide URL defaults function.

        Args:
            f: URL defaults function

        Returns:
            The original function
        """
        # TODO: Implement app URL defaults
        return f

    def record(self, func: Callable) -> None:
        """
        Record a function to be called when the blueprint is registered.

        Args:
            func: Function to record
        """
        # TODO: Implement blueprint recording system
        pass

    def record_once(self, func: Callable) -> None:
        """
        Record a function to be called once when the blueprint is registered.

        Args:
            func: Function to record
        """
        # TODO: Implement blueprint recording system
        pass

    def make_setup_state(self, app, options, first_registration: bool = False):
        """
        Create setup state for blueprint registration.

        Args:
            app: Application instance
            options: Registration options
            first_registration: Whether this is the first registration

        Returns:
            Setup state object
        """
        return BlueprintSetupState(self, app, options, first_registration)

    def register(self, app, options, first_registration: bool = False) -> None:
        """
        Register blueprint with application.

        Args:
            app: Application instance
            options: Registration options
            first_registration: Whether this is the first registration
        """
        state = self.make_setup_state(app, options, first_registration)

        if self.has_static_folder:
            # Register static folder
            state.add_url_rule(
                f"{self.static_url_path}/<path:filename>",
                endpoint="static",
                view_func=app.send_static_file,
            )

    @property
    def has_static_folder(self) -> bool:
        """Check if blueprint has a static folder."""
        return self.static_folder is not None

    def send_static_file(self, filename: str):
        """
        Send static file from blueprint's static folder.

        Args:
            filename: Static file name

        Returns:
            Response with static file
        """
        if not self.has_static_folder:
            raise RuntimeError("Blueprint does not have a static folder")

        # TODO: Implement static file serving
        from ..core.helpers import send_from_directory

        return send_from_directory(self.static_folder, filename)

    def open_resource(self, resource: str, mode: str = "rb"):
        """
        Open resource file from blueprint.

        Args:
            resource: Resource path
            mode: File open mode

        Returns:
            File object
        """
        # TODO: Implement resource opening
        pass

    def get_send_file_max_age(self, filename: Optional[str]) -> Optional[int]:
        """
        Get max age for static files.

        Args:
            filename: File name

        Returns:
            Max age in seconds
        """
        # TODO: Implement static file max age
        return None


class BlueprintSetupState:
    """
    State object for blueprint registration.
    """

    def __init__(
        self,
        blueprint: Blueprint,
        app,
        options: Dict[str, Any],
        first_registration: bool = False,
    ):
        """
        Initialize setup state.

        Args:
            blueprint: Blueprint instance
            app: Application instance
            options: Registration options
            first_registration: Whether this is the first registration
        """
        self.blueprint = blueprint
        self.app = app
        self.options = options
        self.first_registration = first_registration

        self.url_prefix = options.get("url_prefix")
        self.subdomain = options.get("subdomain")
        self.url_defaults = options.get("url_defaults")

    def add_url_rule(
        self,
        rule: str,
        endpoint: Optional[str] = None,
        view_func: Optional[Callable] = None,
        **options,
    ) -> None:
        """
        Add URL rule to application.

        Args:
            rule: URL rule
            endpoint: Endpoint name
            view_func: View function
            **options: Additional options
        """
        if self.url_prefix is not None:
            if rule:
                rule = f"{self.url_prefix.rstrip('/')}/{rule.lstrip('/')}"
            else:
                rule = self.url_prefix

        options.setdefault("subdomain", self.subdomain)
        if endpoint is None:
            endpoint = f"{self.blueprint.name}.{view_func.__name__}"
        else:
            endpoint = f"{self.blueprint.name}.{endpoint}"

        defaults = self.url_defaults
        if "defaults" in options:
            if defaults:
                defaults = {**defaults, **options["defaults"]}
            else:
                defaults = options["defaults"]

        if defaults:
            options["defaults"] = defaults

        # Add rule to application
        self.app.add_url_rule(rule, endpoint, view_func, **options)
