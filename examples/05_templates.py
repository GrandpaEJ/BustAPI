from bustapi import BustAPI, render_template

# Initialize app with explicit template folder (optional if 'templates')
app = BustAPI(template_folder="examples/templates")


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
    app.run(port=5004, debug=True)
