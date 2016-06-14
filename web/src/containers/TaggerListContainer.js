import {connect} from 'react-redux'
import _ from 'lodash'

import {fetchRandomComments, resetCommentTags, addCommentTag} from '../actions/TaggerActions'
import TaggerList from '../components/TaggerList.jsx'

const mapStateToProps = (state) => {
  return {comments: _.values(state.tagger.comments), sources: _.values(state.tagger.sources)};
}

const mapDispatchToProps = (dispatch) => {
  return {
    onReload: (sources, count) =>
      dispatch(fetchRandomComments(count, _.chain(sources)
        .filter('active')
        .map('id')
        .value())),
    onReset: (comments) => _.chain(comments)
      .each(comment => dispatch(resetCommentTags(comment.id, comment.tags)))
      .value(),
    onAcceptAll: (comments) => _.chain(comments)
      .each(({id, suggestion}) => _.chain(suggestion)
        .map('1')
        .each(tag => dispatch(addCommentTag(id, tag)))
        .value())
      .value()
  }
}

const TaggerListContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(TaggerList)

export default TaggerListContainer