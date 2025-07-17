
from flask import request, jsonify

def extract_mandatory_headers():
    """
    Extract and validate mandatory headers from the request.

    Returns:
        tuple: (dict containing headers, response if missing headers, HTTP status code)
    """
    content_type = request.headers.get("Content-Type")
    device_name = request.headers.get("Device-Name")
    device_uuid = request.headers.get("Device-UUID")

    if not content_type or not device_name or not device_uuid:
        return None, jsonify({
            "message": "Missing required headers",
            "required_headers": ["Content-Type", "Device-Name", "Device-UUID"]
        }), 400

    return {
        "Content-Type": content_type,
        "Device-Name": device_name,
        "Device-UUID": device_uuid
    }, None, None