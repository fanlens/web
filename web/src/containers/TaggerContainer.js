import {connect} from 'react-redux'
import {warning} from '../actions/AlertActions'
import {toggleCommentTag} from '../actions/TaggerActions'

import Tagger from '../components/Tagger.jsx'

const mapStateToProps = (state, ownProps) => Object.assign({},
  state.tagger.comments[ownProps.id],
  {tagSet: _.chain(state.tagger.tagSets).filter('active').map('tags').flatten().uniq().value()}//_.uniq(_.flatten(_.map(_.filter(state.tagger.tagSets, 'active'), 'tags')))}
)

const mapDispatchToProps = (dispatch, ownProps) => {
  return {
    onDuplicate: (text) => {
      dispatch(warning(text));
    },
    onToggle: (currentTags, tag) => {
      dispatch(toggleCommentTag(ownProps.id, currentTags, tag));
    }
  }
}

const TaggerContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(Tagger);

export default TaggerContainer