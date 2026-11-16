'''
https://github.com/home-assistant/core/tree/dev/homeassistant/components/conversation
'''
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform
from .manifest import manifest

_LOGGER = logging.getLogger(__name__)
PLATFORMS = [Platform.TTS, Platform.CONVERSATION]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    ''' 安装集成 '''
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(update_listener))
    return True

async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    ''' 配置变更时重载集成 '''
    await hass.config_entries.async_reload(entry.entry_id)

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    ''' 删除集成 '''
    del hass.data[manifest.domain]
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
