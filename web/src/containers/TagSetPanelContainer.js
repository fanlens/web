import {connect} from 'react-redux'
import _ from 'lodash'

import {toggleTagSet} from '../actions/TaggerActions'
import TagSetPanel from '../components/TagSetPanel.jsx'

const mapStateToProps = (state) => {
  const activeSources = _.chain(state.tagger.sources).filter('active').map('id').value();
  return {
    tagSets: _.sortBy(_.values(state.tagger.tagSets), 'id'),
    tagCounts: _.chain(state.tagger.stats)
      .pickBy((value, key) => _.includes(activeSources, key))
      .mapValues('tags')
      .values()
      .reduce((acc, val) => _.reduce(val, (acc, val, key) => {
        (acc[key] += val) || (acc[key] = val);
        return acc;
      }, acc), {})
      .value()
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

