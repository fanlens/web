import keyMirror from 'keymirror';
import _ from 'lodash';

export const AppActionType = keyMirror({
  APP_STATE: null,
});

export const receiveAppState = (state) => ({type: AppActionType.APP_STATE, state});

export function toggle() {
  return (dispatch, getState) => dispatch(receiveAppState(_.mapValues(getState().app, (appState) => !appState)));
}
