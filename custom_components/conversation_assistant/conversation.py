from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components import conversation
from homeassistant.const import MATCH_ALL

from .entity_assistant import EntityAssistant
from .conversation_assistant import ConversationAssistant
from .manifest import manifest

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:

    assistant = ConversationAssistantAgent(hass, entry)

    hass.data[manifest.domain] = ConversationAssistant(hass, entry)

    async_add_entities(
        [
            assistant,
        ]
    )

class ConversationAssistantAgent(conversation.ConversationEntity):
    """语音小助手 Conversation Entity."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the agent."""
        self.hass = hass
        self.entry = entry
        self._attr_name = '语音小助手'
        self._attr_unique_id = f"{entry.entry_id}-conversation"
        self._attr_supported_features = (
                conversation.ConversationEntityFeature.CONTROL
            )
        self.entity_assistant = EntityAssistant(hass, entry.options)
        self._last_text = ''
        self._last_reply = ''

    @property
    def supported_languages(self):
        """Return a list of supported languages."""
        return MATCH_ALL

    @property
    def extra_state_attributes(self):
        """Return state attributes."""
        return {
            'last_text': self._last_text,
            'reply': self._last_reply,
        }

    async def _async_handle_message(
        self,
        user_input: conversation.ConversationInput,
        chat_log: conversation.ChatLog,
    ) -> conversation.ConversationResult:
        """Process the user input."""
        conversation_id = user_input.conversation_id
        conversation_assistant = self.hass.data[manifest.domain]
        text = conversation_assistant.trim_char(user_input.text)
        if text == '':
            return conversation.ConversationResult(
                response=conversation_assistant.intent_result('没有接收到控制命令'),
                conversation_id=conversation_id,
                continue_conversation=False,
            )
        # 插件意图
        result = await self.entity_assistant.async_process(text)
        if result is not None:
            message, entity_id = result
            state = self.hass.states.get(entity_id)
            entities = [
                {
                    'id': entity_id,
                    'name': state.attributes.get('friendly_name'),
                    'state': state.state
                }
            ]
            intent_response = conversation_assistant.intent_result(message, {
                'entities': entities
            })
        else:
            intent_response = await conversation_assistant.async_process(text)

        speech = intent_response.speech.get('plain')
        if speech is not None:
            self._last_reply = speech.get('speech', '')
            self._last_text = text
            self.async_write_ha_state()

        return conversation.ConversationResult(
            response=intent_response,
            conversation_id=conversation_id,
            continue_conversation=False,
        )
