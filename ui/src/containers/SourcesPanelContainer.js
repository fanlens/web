import {connect} from 'react-redux'
import _ from 'lodash'

import SourcesPanel from '../components/SourcesPanel.jsx'
import {toggleSource} from '../actions/TaggerActions'

const mapStateToProps = (state) => {
  return {
    sources: _.sortBy(_.values(state.tagger.sources), 'id')
  }
};

const mapDispatchToProps = (dispatch) => {
  return {
    onSourceSelected: (source) => dispatch(toggleSource(source))
  }
};

const SourcesPanelContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(SourcesPanel);

export default SourcesPanelContainer
