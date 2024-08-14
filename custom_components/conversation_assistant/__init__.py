'''
https://github.com/home-assistant/core/tree/dev/homeassistant/components/conversation
'''
from __future__ import annotations

import logging, asyncio

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, Context
from homeassistant.const import Platform
from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.http import StaticPathConfig
from .http import HttpView
from .manifest import manifest

_LOGGER = logging.getLogger(__name__)
PLATFORMS = [Platform.STT,  Platform.TTS, Platform.CONVERSATION]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    ''' 安装集成 '''
    hass.http.register_view(HttpView)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(update_listener))

    local = hass.config.path("custom_components/conversation_assistant/www")
    LOCAL_PATH = '/www-conversation'
    await hass.http.async_register_static_paths([StaticPathConfig(LOCAL_PATH, local, False)])    
    add_extra_js_url(hass, f'{LOCAL_PATH}/wake-up.js?v={manifest.version}')
    return True

async def update_listener(hass, entry):
    ''' 更新配置 '''
    await async_unload_entry(hass, entry)
    await asyncio.sleep(1)
    await async_setup_entry(hass, entry)

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    ''' 删除集成 '''
    del hass.data[manifest.domain]
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)