import _ from 'lodash'
import {AppActionType} from '../actions/AppActions'

const app = (state = {
  eev: false,
  tagger: true,
}, action) => {
  switch (action.type) {
    case AppActionType.APP_STATE:
      return _.defaults(action.state, state)
    default:
      return state;
  }
}

export default app