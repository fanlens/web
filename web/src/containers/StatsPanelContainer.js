import {connect} from 'react-redux'

import StatsPanel from '../components/StatsPanel.jsx'

const mapStateToProps = (state) => {
  return {
    sources: _.sortBy(_.values(state.tagger.sources), 'id'),
    stats: state.tagger.stats
  }
}

const mapDispatchToProps = (dispatch) => {
  return { }
}

const StatsPanelContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(StatsPanel)

export default StatsPanelContainer
