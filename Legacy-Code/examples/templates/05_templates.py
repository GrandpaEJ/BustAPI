import os

from bustapi import BustAPI, render_template

# Initialize app with explicit template folder relative to this script
script_dir = os.path.dirname(os.path.abspath(__file__))
app = BustAPI(template_folder=os.path.join(script_dir, "templates"))


@app.route("/")
def home():
    """Render a template with variables."""
    return render_template(
        "index.html",
        title="BustAPI Templates",
        user="Rustacean",
        items=["Fast", "Safe", "Easy"],
    )


if __name__ == "__main__":
    print("Running templates example on http://127.0.0.1:5004")
    # debug=False to avoid hot-reload loops during testing
    app.run(port=5004, debug=False)
