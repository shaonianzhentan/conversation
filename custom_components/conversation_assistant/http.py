from homeassistant.components.http import HomeAssistantView
from .manifest import manifest

class HttpView(HomeAssistantView):

    url = "/api/conversation_assistant"
    name = "api:conversation_assistant"
    requires_auth = True

    async def post(self, request):
        hass = request.app["hass"]
        body = await request.json()
        text = body.get('text')
        conversation_assistant = hass.data[manifest.domain]
        result = await conversation_assistant.recognize(text)
        return self.json(result.as_dict())