#!/usr/bin/python
# -*- coding: UTF-8 -*-
import json

class XiaoAIBase(object):
    # (fieldName, fieldType, isRequired)
    _fields = []

    def _init_args(self, expected_type, value):
        if isinstance(value, expected_type):
            return value
        else:
            return expected_type(**value)

    def __init__(self, **kwargs):
        if (not kwargs):
            return
        else:
            fields_names, field_types, is_required = zip(*self._fields)
            assert([isinstance(name, str) for name in fields_names])
            assert([isinstance(type_, type) for type_ in field_types])

            for name, field_type, is_required in self._fields:
                if is_required and name not in kwargs.keys():
                    raise TypeError("Key: {} is required but not found in the json data".format(name))
                v = kwargs.pop(name, {})
                setattr(self, name, self._init_args(field_type, v))

# type definition of XiaoAI Request
class XiaoAIApplication(XiaoAIBase):
    _fields = [('app_id', str, True)]

class XiaoAIUser(XiaoAIBase):
    _fields = [('user_id', str, True), ('access_token', str, False), ('is_user_login', bool, False), ('gender', str, False), ('real_user_id', str, False)]

class XiaoAISession(XiaoAIBase):
    _fields = [('is_new', bool, True), ('session_id', str, True), ('application', XiaoAIApplication, True), ('attributes', dict, False), ('user', XiaoAIUser, False)]

class XiaoAIClientAppInfo(XiaoAIBase):
    _fields = [('pkg_name', dict, True), ('version_name', str, False)]

class XiaoAIContext(XiaoAIBase):
    _fields = [('passport', dict, False), ('device_id', str, False), ('bind_id', str, False), ('app_info', list, False), ('user_agent', str, False)]

class XiaoAIIntent(XiaoAIBase):
    _fields = [('is_direct_wakeup', bool, False)]

class XiaoAISlot(XiaoAIBase):
    _fields = [('name', str, True), ('value', str, False), ('is_inquire_failed', bool, False)]

class XiaoAISlotInfo(XiaoAIBase):
    _fields = [('intent_name', str, True), ('is_confirmed', bool, False), ('slots', list, False)]

class XiaoAIEventProperty(XiaoAIBase):
    _fields = [('msg_file_id', str, False), ('asr_text', str, False)]

class XiaoAIRequest(XiaoAIBase):
    _fields = [('request_id', str, True), ('timestamp', int, True), ('locale', str, True), ('intent', XiaoAIIntent, False), ('no_response', bool, False), ('type', int, True), ('slot_info', XiaoAISlotInfo, False), ('event_type', str, False), ('event_property', XiaoAIEventProperty, False)]

class XiaoAIOpenRequest(XiaoAIBase):
    _fields = [('version', str, True), ('query', str, False), ('session', XiaoAISession, True), ('context', XiaoAIContext, False), ('request', XiaoAIRequest, True)]


# type definition of XiaoAI Response
class XiaoAIToSpeak:
    def __init__(self, type_, text):
        if (text is not None and type(text) is not str):
            raise TypeError("ToSpeak.text must be str type")
        self.text = text
        if (type_ is not None and type(type_) is not int):
            raise TypeError("ToSpeak.type_ must be int type")
        self.type_ = type_

class XiaoAIRichText:
    def __init__(self, text, sub_text=None, description=None, sub_title=None):
        if (text is not None and type(text) is not str):
            raise TypeError("XiaoAIRichText.text must be str type")
        self.text = text
        if (sub_text is not None and type(sub_text) is not str):
            raise TypeError("XiaoAIRichText.sub_text must be str type")
        self.sub_text = sub_text
        if (description is not None and type(description) is not str):
            raise TypeError("XiaoAIRichText.description must be str type")
        self.description = description
        if (sub_title is not None and type(sub_title) is not str):
            raise TypeError("XiaoAIRichText.sub_title must be str type")
        self.sub_title = sub_title

class XiaoAIItem:
    def __init__(self, image_style=None, images=None, intent=None, title=None, body=None, background_image=None):
        if (image_style is not None and type(image_style) is not str):
            raise TypeError("Item.image_style must be str type")
        self.image_style = image_style
        if (images is not None and type(images) is not list):
            raise TypeError("Item.images must be list type")
        self.images = images
        if (intent is not None and type(intent) is not str):
            raise TypeError("Item.intent must be str type")
        self.intent = intent
        if (title is not None and type(title) is not XiaoAIRichText):
            raise TypeError("Item.title must be XiaoAIRichText type")
        self.title = title
        if (body is not None and type(body) is not list):
            raise TypeError("Item.body must be list[XiaoAIRichText] type")
        self.body = body
        if (background_image is not None and type(background_image) is not str):
            raise TypeError("Item.background_image must be str type")
        self.background_image = background_image

class XiaoAIUITemplate:
    def __init__(self, type_, items=None, item=None, logo=None, package_name=None, logo_text=None):
        if (type_ is not None and type(type_) is not int):
            raise TypeError("UITemplate.type must be int type")
        self.type_ = type_
        if (items is not None and type(items) is not list):
            raise TypeError("UITemplate.items must be list[XiaoAIItem] type")
        self.items = items
        if (logo is not None and type(logo) is not str):
            raise TypeError("UITemplate.logo must be str type")
        self.logo = logo
        if (item is not None and type(item) is not XiaoAIItem):
            raise TypeError("UITemplate.item must be item type")
        self.item = item
        if (package_name is not None and type(package_name) is not str):
            raise TypeError("UITemplate.package_name must be str type")
        self.package_name = package_name
        if (logo_text is not None and type(logo_text) is not str):
            raise TypeError("UITemplate.logo_text must be str type")
        self.logo_text = logo_text

class XiaoAIPhoneTemplate:
    def __init__(self, template_name, params):
        if (template_name is not None and type(template_name) is not str):
            raise TypeError("PhoneTemplate.template_name must be int type")
        self.template_name = template_name
        if (params is not None and type(params) is not dict):
            raise TypeError("PhoneTemplate.params must be dict type")
        self.params = params

class XiaoAIToDisplay:
    def __init__(self, type_=None, url=None, text=None, ui_template=None, ui_type=None, phone_template=None):
        if (type_ is not None and type(type_) is not int):
            raise TypeError("ToDisplay.type_ must be int type")
        self.type_ = type_
        if (url is not None and type(url) is not str):
            raise TypeError("ToDisplay.url must be str type")
        self.url = url
        if (text is not None and type(text) is not str):
            raise TypeError("ToDisplay.text must be str type")
        self.text = text
        if (ui_template is not None and type(ui_template) is not XiaoAIUITemplate):
            raise TypeError("ToDisplay.ui_template must be UITemplate type")
        self.ui_template = ui_template
        if (ui_type is not None and type(ui_type) is not str):
            raise TypeError("ToDisplay.ui_type must be str type")
        self.ui_type = ui_type
        if (phone_template is not None and type(phone_template) is not XiaoAIPhoneTemplate):
            raise TypeError("ToDisplay.phone_template must be XiaoAIPhoneTemplate type")
        self.phone_template = phone_template

class XiaoAIStream:
    def __init__(self, url, token=None, offset_in_milliseconds=None):
        if (url is not None and type(url) is not str):
            raise TypeError("Stream.url must be str type")
        self.url = url
        if (token is not None and type(token) is not str):
            raise TypeError("Stream.token must be str type")
        self.token = token
        if (offset_in_milliseconds is not None and type(offset_in_milliseconds) is not int):
            raise TypeError("Stream.offset_in_milliseconds must be int type")
        self.offset_in_milliseconds = offset_in_milliseconds


class XiaoAIAudioItem:
    def __init__(self, stream, display_text=None):
        if (stream is not None and type(stream) is not XiaoAIStream):
            raise TypeError("AudioItem.stream must be Stream type")
        self.stream = stream
        if (display_text is not None and type(display_text) is not str):
            raise TypeError("AudioItem.display_text must be str type")
        self.display_text = display_text

class XiaoAITTSItem:
    def __init__(self, type_, text=None):
        if (type_ is not None and type(type_) is not str):
            raise TypeError("TTSItem.type_ must be str type")
        self.type_ = type_
        if (text is not None and type(text) is not str):
            raise TypeError("TTSItem.text must be str type")
        self.text = text


class XiaoAIDirective:
    def __init__(self, type_, audio_item=None, tts_item=None):
        if (type_ is not None and type(type_) is not str):
            raise TypeError("Directive.type_ must be str type")
        self.type_ = type_
        if (audio_item is not None and type(audio_item) is not XiaoAIAudioItem):
            raise TypeError("Directive.audio_item must be AudioItem type")
        self.audio_item = audio_item
        if (tts_item is not None and type(tts_item) is not XiaoAITTSItem):
            raise TypeError("Directive.tts_item must be TTSItem type")
        self.tts_item = tts_item

class XiaoAIPushAppActionProperty:
    def __init__(self, title = None, content = None, uri = None):
        if (title is not None and type(title) is not str):
            raise TypeError("XiaoAIPushAppActionProperty.title must be str type")
        self.title = title

        if (content is not None and type(content) is not str):
            raise TypeError("XiaoAIPushAppActionProperty.content must be list type")
        self.content = content

        if (uri is not None and type(uri) is not str):
            raise TypeError("XiaoAIPushAppActionProperty.uri must be str type")
        self.uri = uri

class XiaoAIDeviceCommandActionProperty:
    def __init__(self, command = None):
        if (command is not None and type(command) is not str):
            raise TypeError("XiaoAIDeviceCommandActionProperty.command must be str type")
        self.command = command

class XiaoAIQuickAppCardActionProperty:
    def __init__(self, card_params, ui_type = None):
        if (card_params is not None and type(card_params) is not dict):
            raise TypeError("XiaoAIQuickAppCardActionProperty.card_params must be dict type")
        self.card_params = card_params
        if (ui_type is not None and type(ui_type) is not str):
            raise TypeError("XiaoAIQuickAppCardActionProperty.ui_type must be str type")
        self.ui_type = ui_type

class XiaoAIQuickAppExtra:
    def __init__(self, key = None, value = None):
        if (key is not None and type(key) is not str):
            raise TypeError("XiaoAIPushAppExtra.key must be str type")
        self.key = key

        if (value is not None and type(value) is not str):
            raise TypeError("XiaoAIPushAppExtra.value must be str type")
        self.value = value

class XiaoAIIntentInfoExtra:
    def __init__(self, intent_type = None, uri = None):
        if (intent_type is not None and type(intent_type) is not str):
            raise TypeError("XiaoAIIntentInfoExtra.intent_type must be str type")
        self.intent_type = intent_type

        if (uri is not None and type(uri) is not str):
            raise TypeError("XiaoAIIntentInfoExtra.uri must be str type")
        self.uri = uri

class XiaoAIActionProperty:
    def __init__(self, file_id_list = None, quick_app_path = None, push_app_info = None, quick_app_extra = None, device_command = None, app_intent_info = None, quick_app_card_info = None, app_h5_url = None):
        if (file_id_list is not None and type(file_id_list) is not list):
            raise TypeError("ActionProperty.file_id_list must be list type")
        self.file_id_list = file_id_list

        if (quick_app_path is not None and type(quick_app_path) is not str):
            raise TypeError("ActionProperty.quick_app_path must be str type")
        self.quick_app_path = quick_app_path

        if (push_app_info is not None and type(push_app_info) is not XiaoAIPushAppActionProperty):
            raise TypeError("ActionProperty.push_app_info must be XiaoAIPushAppActionProperty type")
        self.push_app_info = push_app_info

        if (quick_app_extra is not None and type(quick_app_extra) is not list):
            raise TypeError("ActionProperty.quick_app_extra must be list type")
        self.quick_app_extra = quick_app_extra

        if (device_command is not None and type(device_command) is not XiaoAIDeviceCommandActionProperty):
            raise TypeError("ActionProperty.device_command must be XiaoAIDeviceCommandActionProperty type")
        self.device_command = device_command

        if (app_intent_info is not None and type(app_intent_info) is not XiaoAIIntentInfoExtra):
            raise TypeError("ActionProperty.app_intent_info must be XiaoAIIntentInfoExtra type")
        self.app_intent_info = app_intent_info

        if (quick_app_card_info is not None and type(quick_app_card_info) is not XiaoAIQuickAppCardActionProperty):
            raise TypeError("ActionProperty.quick_app_card_info must be XiaoAIQuickAppCardActionProperty type")
        self.quick_app_card_info = quick_app_card_info

        if (app_h5_url is not None and type(app_h5_url) is not str):
            raise TypeError("ActionProperty.app_h5_url must be str type")
        self.app_h5_url = app_h5_url

class XiaoAIRegisterEvent:
    def __init__(self, event_name):
        if (event_name is not None and type(event_name) is not str):
            raise TypeError("RegisterEvent.event_name must be str type")
        self.event_name = event_name

class XiaoAIResponse:
    def __init__(self, to_speak  = None,
                 to_display = None,
                 directives = None,
                 open_mic=None,
                 not_understand=None,
                 action=None,
                 action_property=None,
                 register_events=None,
                 is_directive_not_interrupted=None):
        if (to_speak is not None and type(to_speak) is not XiaoAIToSpeak):
            raise TypeError("Response.to_speak must be ToSpeak type")
        self.to_speak = to_speak

        if (to_display is not None and type(to_display) is not XiaoAIToDisplay):
            raise TypeError("Response.to_display must be ToDisplay type")
        self.to_display = to_display

        if (directives is not None and type(directives) is not list):
            raise TypeError("Response.directives must be list type")
        self.directives = directives

        if (open_mic is not None and type(open_mic) is not bool):
            raise TypeError("Response.open_mic must be bool type")
        self.open_mic = open_mic

        if (not_understand is not None and type(not_understand) is not bool):
            raise TypeError("Response.not_understand must be bool type")
        self.not_understand = not_understand

        if (action is not None and type(action) is not str):
            raise TypeError("Response.action must be str type")
        self.action = action

        if (action_property is not None and type(action_property) is not XiaoAIActionProperty):
            raise TypeError("Response.action_property must be ActionProperty type")
        self.action_property = action_property

        if (register_events is not None and type(register_events) is not list):
            raise TypeError("Response.register_events must be list type")
        self.register_events = register_events

        if (is_directive_not_interrupted is not None and type(is_directive_not_interrupted) is not bool):
            raise TypeError("Response.is_directive_not_interrupted must be bool type")
        self.is_directive_not_interrupted = is_directive_not_interrupted

class XiaoAIOpenResponse:

    def __init__(self, version, is_session_end, response, session_attributes=None):
        if (version is not None and type(version) is not str):
            raise TypeError("AIResponse.version must be str type")
        self.version = version
        if (session_attributes is not None and type(session_attributes) is not dict):
            raise TypeError("AIResponse.session_attributes must be dict type")
        self.session_attributes = session_attributes
        if (is_session_end is not None and type(is_session_end) is not bool):
            raise TypeError("AIResponse.is_session_end must be bool type")
        self.is_session_end = is_session_end
        if (response is not None and type(response) is not XiaoAIResponse):
            raise TypeError("AIResponse.response must be Response type")
        self.response = response

def xiaoai_response(data):
    return json.dumps(data, default=lambda obj: dict(("type" if key == "type_" else key, value) for (key, value) in obj.__dict__.items() if value is not None))


def xiaoai_request(result):
    return XiaoAIOpenRequest(**result)

def xiaoai_from_json(data):
    result = json.loads(data)
    return XiaoAIOpenRequest(**result)