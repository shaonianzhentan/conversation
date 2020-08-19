export declare type Error = 1 | 2 | 3 | 4;
export declare type UnsubscribeFunc = () => void;
export declare type MessageBase = {
    id?: number;
    type: string;
    [key: string]: any;
};
export declare type HassEventBase = {
    origin: string;
    time_fired: string;
    context: {
        id: string;
        user_id: string;
    };
};
export declare type HassEvent = HassEventBase & {
    event_type: string;
    data: {
        [key: string]: any;
    };
};
export declare type StateChangedEvent = HassEventBase & {
    event_type: "state_changed";
    data: {
        entity_id: string;
        new_state: HassEntity | null;
        old_state: HassEntity | null;
    };
};
export declare type HassConfig = {
    latitude: number;
    longitude: number;
    elevation: number;
    unit_system: {
        length: string;
        mass: string;
        volume: string;
        temperature: string;
    };
    location_name: string;
    time_zone: string;
    components: string[];
    config_dir: string;
    allowlist_external_dirs: string[];
    allowlist_external_urls: string[];
    version: string;
    config_source: string;
    safe_mode: boolean;
    state: "NOT_RUNNING" | "STARTING" | "RUNNING" | "STOPPING" | "FINAL_WRITE";
    external_url: string | null;
    internal_url: string | null;
};
export declare type HassEntityBase = {
    entity_id: string;
    state: string;
    last_changed: string;
    last_updated: string;
    attributes: HassEntityAttributeBase;
    context: {
        id: string;
        user_id: string | null;
    };
};
export declare type HassEntityAttributeBase = {
    friendly_name?: string;
    unit_of_measurement?: string;
    icon?: string;
    entity_picture?: string;
    supported_features?: number;
    hidden?: boolean;
    assumed_state?: boolean;
    device_class?: string;
};
export declare type HassEntity = HassEntityBase & {
    attributes: {
        [key: string]: any;
    };
};
export declare type HassEntities = {
    [entity_id: string]: HassEntity;
};
export declare type HassService = {
    description: string;
    fields: {
        [field_name: string]: {
            description: string;
            example: string | boolean | number;
        };
    };
};
export declare type HassDomainServices = {
    [service_name: string]: HassService;
};
export declare type HassServices = {
    [domain: string]: HassDomainServices;
};
export declare type HassUser = {
    id: string;
    is_owner: boolean;
    name: string;
};
