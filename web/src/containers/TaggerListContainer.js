import {connect} from 'react-redux'
import _ from 'lodash'

import {fetchRandomComments, resetCommentTags} from '../actions/TaggerActions'
import TaggerList from '../components/TaggerList.jsx'

const mapStateToProps = (state) => {
  return {comments: _.values(state.tagger.comments), sources: _.values(state.tagger.sources)};
}

const mapDispatchToProps = (dispatch, ownProps) => {
  return {
    onReload: (sources) => {
      dispatch(fetchRandomComments(ownProps.count, _.chain(sources).filter('active').map('id').value()));
    },
    onReset: (comments) => {
      _.values(comments).forEach(comment => dispatch(resetCommentTags(comment.id, comment.tags)));
    }
  }
}

const TaggerListContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(TaggerList)

export default TaggerListContainer