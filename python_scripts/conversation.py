text = data.get("text")
hass.services.call("persistent_notification", "create", {
    "title": "语音小助手",
    "message": text
}, False)