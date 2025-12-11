import os

from bustapi import BustAPI, request

app = BustAPI()


@app.route("/upload", methods=["POST"])
def upload_file():
    files = request.files
    response_text = []

    for name, file in files.items():
        # Check if /tmp exists, otherwise use current dir
        save_dir = "/tmp" if os.path.exists("/tmp") else "."
        save_path = os.path.join(save_dir, file.filename)
        file.save(save_path)
        response_text.append(f"Saved {name} as {save_path} ({file.content_type})")

    form_data = request.form
    for key, value in form_data.items():
        response_text.append(f"Form field {key}: {value}")

    return "\n".join(response_text)


if __name__ == "__main__":
    app.run(port=5005)
