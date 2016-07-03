import {connect} from 'react-redux'
import _ from 'lodash'

import {warning, info} from '../actions/AlertActions'
import {toggleCommentTag, fetchTagCounts} from '../actions/TaggerActions'

import Tagger from '../components/Tagger.jsx'

const mapStateToProps = (state, ownProps) => Object.assign({},
  state.tagger.comments[ownProps.id],
  {tagSet: _.chain(state.tagger.tagSets).filter('active').map('tags').flatten().uniq().value()}
)

const mapDispatchToProps = (dispatch, ownProps) => {
  return {
    onDuplicate: (text) => {
      dispatch(warning(text));
    },
    onToggle: (currentTags, tag) => dispatch(toggleCommentTag(ownProps.id, currentTags, tag)).then(dispatch(fetchTagCounts())),
    onNewTag: (currentTags, tag) => {
      dispatch(info('Adding new tags is not possible in the demo. Please choose from the provided tag sets.'))
      //this.onToggle(currentTags, tag)
    }
  }
}

const TaggerContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(Tagger);

export default TaggerContainer