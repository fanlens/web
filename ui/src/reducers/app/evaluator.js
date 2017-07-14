import defaults from "lodash/fp/defaults";
import {ModelActionType} from "../../actions/ModelActions";

const evaluator = (state = {suggestion: {}, isFetching: false}, action) => {
  switch (action.type) {
    case ModelActionType.MODEL_RECEIVE_ISFETCHING:
      return defaults(state)({isFetching: action.isFetching});
    case ModelActionType.MODEL_RECEIVE_SUGGESTION:
      return defaults(state)({suggestion: action.suggestion});
    default:
      return state;
  }
};

export default evaluator;