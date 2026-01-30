import os

from bustapi import BustAPI, FileResponse, HTMLResponse

app = BustAPI(static_folder="static", root_path=os.getcwd())


@app.route("/")
def index():
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <body>
        <h1>Video Streaming Demo</h1>

        <h2>1. Static File (Recommended)</h2>
        <p>Start downloading immediately, handled by Rust backend.</p>
        <video width="640" height="360" controls>
            <source src="/static/bigbuckbunny.mp4" type="video/mp4">
            Your browser does not support the video tag.
        </video>

        <h2>2. Dynamic Route (FileResponse)</h2>
        <p>Served via Python route handler.</p>
        <video width="640" height="360" controls>
            <source src="/video/dynamic" type="video/mp4">
            Your browser does not support the video tag.
        </video>
    </body>
    </html>
    """)


@app.route("/video/dynamic")
def video_dynamic():
    # Use Flask-style send_file for Range support
    from bustapi import send_file

    return send_file("static/bigbuckbunny.mp4", mimetype="video/mp4")


if __name__ == "__main__":
    print("Serving video on http://127.0.0.1:8004")
    app.run(debug=True, port=8004)
