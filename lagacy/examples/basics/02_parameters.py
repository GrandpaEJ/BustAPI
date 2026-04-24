from bustapi import BustAPI, request

app = BustAPI()


@app.route("/user/<int:user_id>")
def get_user(user_id):
    """Path parameter example"""
    return {
        "user_id": int(
            request.path.split("/")[-1]
        ),  # Simple manual extraction since param passing might vary
        # Note: In a full impl, extracting user_id would be clean.
        # For now, let's assume the router passes generic RequestData.
        # Actually, let's assume request.view_args matches if implemented,
        # or stick to parsing url.
        "status": "active",
    }


@app.route("/search")
def search():
    """Query parameter example"""
    # Verify request.args works
    query = request.args.get("q", "default")
    page = request.args.get("page", 1)

    return {"search_query": query, "page": page, "results": []}


if __name__ == "__main__":
    print("Running parameters example on http://127.0.0.1:5001")
    app.run(port=5001, workers=4)
