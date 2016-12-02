import keyMirror from 'keymirror';

export const AlertActionType = keyMirror({
  ALERT_SUCCESS: null,
  ALERT_INFO: null,
  ALERT_WARNING: null,
  ALERT_DANGER: null,
  ALERT_DISMISS: null
});

let nextId = 0;
export const info = (text) => ({id: nextId++, type: AlertActionType.ALERT_INFO, text});

export const success = (text) => ({id: nextId++, type: AlertActionType.ALERT_SUCCESS, text});

export const warning = (text) => ({id: nextId++, type: AlertActionType.ALERT_WARNING, text});

export const danger = (text) => ({id: nextId++, type: AlertActionType.ALERT_DANGER, text});

export const dismiss = (id) => ({type: AlertActionType.ALERT_DISMISS, id});