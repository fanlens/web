import {connect} from 'react-redux'
import _ from 'lodash'

import {toggleTagSet} from '../actions/TaggerActions'
import TagSetPanel from '../components/TagSetPanel.jsx'

const mapStateToProps = (state) => ({
  tagSets: _.sortBy(_.values(state.tagger.tagSets), 'id'),
  tagCounts: state.tagger.counts
});

const mapDispatchToProps = (dispatch) => ({
  onTagSetSelected: (id) => {
    dispatch(toggleTagSet(id));
  }
});

const TagSetPanelContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(TagSetPanel)

export default TagSetPanelContainer

