import {connect} from 'react-redux'
import _ from 'lodash'

import {warning, info} from '../actions/AlertActions'
import {toggleCommentTag} from '../actions/TaggerActions'

import Tagger from '../components/Tagger.jsx'

const mapStateToProps = (state, ownProps) => ({
  comment: state.tagger.comments[ownProps.id],
  tagSet: _.chain(state.tagger.tagSets).filter('active').map('tags').flatten().uniq().value()
});

const mapDispatchToProps = (dispatch) => ({
  onDuplicate: (text) => {
    dispatch(warning(text));
  },
  onToggle: (comment, tag) => dispatch(toggleCommentTag(comment, tag)),
  onNewTag: (comment, tag) => {
    dispatch(info('Adding new tags is not possible in the demo. Please choose from the provided tag sets.'))
    //this.onToggle(currentTags, tag)
  }
});

const TaggerContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(Tagger);

export default TaggerContainer