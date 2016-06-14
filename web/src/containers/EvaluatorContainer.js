import {connect} from 'react-redux'

import {fetchSuggestionForText} from '../actions/TaggerActions'
import {info} from '../actions/AlertActions'

import Evaluator from '../components/Evaluator.jsx'

const mapStateToProps = (state) => {
  return {
    loading: state.tagger.evaluator.loading,
    suggestion: state.tagger.evaluator.suggestion
  }
}

const mapDispatchToProps = (dispatch) => {
  return {
    onEvaluate: (text) => dispatch(fetchSuggestionForText(text)),
    onPost: () => dispatch(info('The posting function is not available in the demo.')),
    onDelayed: () => dispatch(info('The delayed posting function is not available in the demo.'))
  }
}

const EvaluatorContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(Evaluator)

export default EvaluatorContainer