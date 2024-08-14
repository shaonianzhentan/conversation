from __future__ import annotations

from typing import Any
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, OptionsFlow, ConfigEntry
from homeassistant.data_entry_flow import FlowResult
from homeassistant.core import callback

from .manifest import manifest

class SimpleConfigFlow(ConfigFlow, domain=manifest.domain):

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        
        DATA_SCHEMA = vol.Schema({})

        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is None:
            return self.async_show_form(step_id="user", data_schema=DATA_SCHEMA)

        return self.async_create_entry(title=manifest.name, data=user_input)
    
    @staticmethod
    @callback
    def async_get_options_flow(entry: ConfigEntry):
        return OptionsFlowHandler(entry)

class OptionsFlowHandler(OptionsFlow):
    def __init__(self, config_entry: ConfigEntry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        return await self.async_step_user(user_input)

    async def async_step_user(self, user_input=None):
        default_name = '停止控制'
        options = self.config_entry.options
        errors = {}
        if user_input is not None:
            if user_input.get('calendar_id') == default_name:
                del user_input['calendar_id']
            if user_input.get('music_id') == default_name:
                del user_input['music_id']
            if user_input.get('tv_id') == default_name:
                del user_input['tv_id']
            if user_input.get('fm_id') == default_name:
                del user_input['fm_id']
            if user_input.get('xiaoai_id') == default_name:
                del user_input['xiaoai_id']
            if user_input.get('xiaodu_id') == default_name:
                del user_input['xiaodu_id']
            return self.async_create_entry(title='', data=user_input)

        # 日历
        calendar_states = self.hass.states.async_all('calendar')
        calendar_entities = { default_name: default_name }
        for state in calendar_states:
            entity_id = state.entity_id
            friendly_name = state.attributes.get('friendly_name')
            if friendly_name is not None:
                calendar_entities[entity_id] = f'{friendly_name}（{entity_id}）'

        media_states = self.hass.states.async_all('media_player')

        media_entities = { default_name: default_name }
        music_media_entities = { default_name: default_name }
        xiaoai_media_entities = { default_name: default_name }
        xiaodu_media_entities = { default_name: default_name }
        tv_media_entities = { default_name: default_name }

        for state in media_states:
            friendly_name = state.attributes.get('friendly_name')
            platform = state.attributes.get('platform')
            entity_id = state.entity_id
            value = f'{friendly_name}（{entity_id}）'

            if platform == 'cloud_music':
                music_media_entities[entity_id] = value
                continue
            if platform == 'tv':
                tv_media_entities[entity_id] = value
                continue
            if platform == 'xiaodu':
                xiaodu_media_entities[entity_id] = value
                continue
            if state.attributes.get('xiaoai_id') is not None:
                xiaoai_media_entities[entity_id] = value
                continue
            media_entities[entity_id] = value

        DATA_SCHEMA = vol.Schema({
            vol.Optional("speech_key", default=options.get('speech_key', '')): str,
            vol.Optional("calendar_id", default=options.get('calendar_id', default_name)): vol.In(calendar_entities),
            vol.Optional("music_id", default=options.get('music_id', default_name)): vol.In(music_media_entities),
            vol.Optional("tv_id", default=options.get('tv_id', default_name)): vol.In(tv_media_entities),
            vol.Optional("fm_id", default=options.get('fm_id', default_name)): vol.In(media_entities),
            vol.Optional("xiaoai_id", default=options.get('xiaoai_id', default_name)): vol.In(xiaoai_media_entities),
            vol.Optional("xiaodu_id", default=options.get('xiaodu_id', default_name)): vol.In(xiaodu_media_entities)
        })
        return self.async_show_form(step_id="user", data_schema=DATA_SCHEMA, errors=errors)