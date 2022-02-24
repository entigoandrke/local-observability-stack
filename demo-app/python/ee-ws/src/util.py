import json


def health(environ, start_response):
    headers = [("content-type", "application/json")]
    status = "200 OK"

    output = json.dumps({"data": {"status": "running"}})
    output_encoded = output.encode("utf-8")

    start_response(status, headers)
    return [output_encoded]
