import {connect} from 'react-redux'

import Evaluator from '../components/Evaluator.jsx'

const mapStateToProps = (state) => {
  return {}
}

const mapDispatchToProps = (dispatch) => {
  return {}
}

const EvaluatorContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(Evaluator)

export default EvaluatorContainer