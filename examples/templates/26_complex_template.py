from bustapi import BustAPI

app = BustAPI(template_folder="templates", static_folder="static")


@app.route("/")
def index():
    items = [
        {"id": 1, "name": "Item One", "active": True},
        {"id": 2, "name": "Item Two", "active": False},
        {"id": 3, "name": "Item Three", "active": True},
    ]
    return app.render_template(
        "complex.html",
        user="Tester",
        items=items,
        show_secret=True,
        secret_code="RUST_IS_FAST",
    )


if __name__ == "__main__":
    print("Starting server for complex templating verification...")
    # Port 8003 to avoid conflicts
    app.run(port=8003)
