import {connect} from 'react-redux'
import _ from 'lodash'

import {toggleTagSet} from '../actions/TaggerActions'
import TagSetPanel from '../components/TagSetPanel.jsx'

const mapStateToProps = (state) => {
  return {
    tagSets: _.sortBy(_.values(state.tagger.tagSets), 'id'),
    tagCounts: state.tagger.stats.__all.tags
  }
}

const mapDispatchToProps = (dispatch) => {
  return {
    onTagSetSelected: (id) => {
      dispatch(toggleTagSet(id));
    }
  }
}

const TagSetPanelContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(TagSetPanel)

export default TagSetPanelContainer

