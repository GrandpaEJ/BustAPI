# Deployment

BustAPI uses an embedded Actix-web server.

For production, simply run your application file:

```bash
python main.py
```

Arguments like `workers` can be configured in your `app.run()` call.
