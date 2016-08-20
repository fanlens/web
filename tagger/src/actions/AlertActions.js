import keyMirror from 'keymirror';

export const AlertActionType = keyMirror({
  ALERT_SUCCESS: null,
  ALERT_INFO: null,
  ALERT_WARNING: null,
  ALERT_DANGER: null,
  ALERT_DISMISS: null
});

let nextId = 0;
export const info = (text) => {
  return {id: nextId++, type: AlertActionType.ALERT_INFO, text};
}

export const success = (text) => {
  return {id: nextId++, type: AlertActionType.ALERT_SUCCESS, text};
}

export const warning = (text) => {
  return {id: nextId++, type: AlertActionType.ALERT_WARNING, text};
}

export const danger = (text) => {
  return {id: nextId++, type: AlertActionType.ALERT_DANGER, text};
}

export const dismiss = (id) => {
  return {type: AlertActionType.ALERT_DISMISS, id};
}