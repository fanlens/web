import {AlertActionType} from '../actions/alert';
import reject from 'lodash/fp/reject';

const alerts = (state = [], action) => {
  switch (action.type) {
    case AlertActionType.ALERT_DISMISS:
      return reject({id: action.id})(state);
    case AlertActionType.ALERT_INFO:
    case AlertActionType.ALERT_SUCCESS:
    case AlertActionType.ALERT_WARNING:
    case AlertActionType.ALERT_DANGER:
      return [...state, action];
    default:
      return state;
  }
};

export default alerts;