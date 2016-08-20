import {AlertActionType} from '../actions/AlertActions'
import _ from 'lodash'

const alerts = (state = [], action) => {
  switch (action.type) {
    case AlertActionType.ALERT_DISMISS:
      return _.reject(state, {id: action.id})
    case AlertActionType.ALERT_INFO:
    case AlertActionType.ALERT_SUCCESS:
    case AlertActionType.ALERT_WARNING:
    case AlertActionType.ALERT_DANGER:
      return [...state, action];
    default:
      return state;
  }
}

export default alerts