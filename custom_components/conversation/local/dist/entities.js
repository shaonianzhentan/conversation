import { getCollection } from "./collection.js";
import { getStates } from "./commands.js";
function processEvent(store, event) {
    const state = store.state;
    if (state === undefined)
        return;
    const { entity_id, new_state } = event.data;
    if (new_state) {
        store.setState({ [new_state.entity_id]: new_state });
    }
    else {
        const newEntities = Object.assign({}, state);
        delete newEntities[entity_id];
        store.setState(newEntities, true);
    }
}
async function fetchEntities(conn) {
    const states = await getStates(conn);
    const entities = {};
    for (let i = 0; i < states.length; i++) {
        const state = states[i];
        entities[state.entity_id] = state;
    }
    return entities;
}
const subscribeUpdates = (conn, store) => conn.subscribeEvents(ev => processEvent(store, ev), "state_changed");
export const entitiesColl = (conn) => getCollection(conn, "_ent", fetchEntities, subscribeUpdates);
export const subscribeEntities = (conn, onChange) => entitiesColl(conn).subscribe(onChange);
