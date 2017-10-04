import keyMirror from "keymirror";


export const ActionType = keyMirror({
  RECEIVE_DRAWER_STATE: null,
});

const receiveDrawerState = (open) => ({type: ActionType.RECEIVE_DRAWER_STATE, open});

export const setDrawerState = (open) =>
  (dispatch) => dispatch(receiveDrawerState(open));

export const toggleDrawer = () =>
  (dispatch, getState) => dispatch(setDrawerState(!getState().app.drawer.open));
