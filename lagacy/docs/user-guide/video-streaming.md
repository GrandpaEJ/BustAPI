# Video Streaming & Range Requests

Starting from **v0.9.0**, BustAPI includes production-ready support for **HTTP Range Requests**. This enables:
- **Video Scrubbing**: Users can jump to any part of a video instantly.
- **Resumable Downloads**: Large file downloads can be paused and resumed.
- **Partal Content**: Serving only requested byte ranges (HTTP 206).

This capability is powered by the Rust backend using `actix-files`, ensuring zero-copy efficiency.

## Static File Streaming

Any file served from your `static_folder` automatically supports range requests.

```python
from bustapi import BustAPI

# Files in "static/" are automatically streamable
app = BustAPI(static_folder="static")

if __name__ == "__main__":
    app.run()
```

### HTML5 Video Example
```html
<video width="640" height="360" controls>
    <source src="/static/video.mp4" type="video/mp4">
    Your browser does not support the video tag.
</video>
```
The browser will automatically send `Range: bytes=0-` headers, and BustAPI will respond with `206 Partial Content`.

## Dynamic File Streaming

If you need to serve files dynamically (e.g., protected content, or files outside the static folder), use `send_file`.

```python
from bustapi import BustAPI, send_file

app = BustAPI()

@app.route("/video/<id>")
def stream_video(id):
    # Determine file path based on ID
    file_path = f"secure_storage/videos/{id}.mp4"
    
    # helper `send_file` returns a FileResponse
    return send_file(file_path, mimetype="video/mp4")
```

### `FileResponse` Objects

You can also use `FileResponse` directly for more control:

```python
from bustapi import FileResponse

@app.route("/download")
def download_large_file():
    return FileResponse(
        path="data/dataset.csv",
        filename="custom_name.csv",
        media_type="text/csv",
        content_disposition_type="attachment"
    )
```

## How It Works

1.  **HEAD Requests**: BustAPI automatically handles `HEAD` requests for all routes. Browns use `HEAD` to check if a resource supports `Accept-Ranges: bytes` before sending a `Range` request.
2.  **Actix-Files Integration**: When a `FileResponse` is returned, the Rust backend hands off the file descriptor to `actix-files::NamedFile`, which efficiently handles the seeking and chunking logic at the OS level.
3.  **Correct Status Codes**:
    - `200 OK`: Full file served.
    - `206 Partial Content`: Byte range request served.
    - `416 Range Not Satisfiable`: Invalid range requested.
