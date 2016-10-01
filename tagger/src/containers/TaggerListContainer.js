import {connect} from 'react-redux'
import _ from 'lodash'

import {fetchRandomComments, resetCommentTags, addCommentTag, fetchTagCounts} from '../actions/TaggerActions'
import TaggerList from '../components/TaggerList.jsx'

const mapStateToProps = (state) => {
  return {
    comments: _.values(state.tagger.comments),
    sources: _.chain(state.tagger.sources).filter('active').map('id').value()
  };
};

const mapDispatchToProps = (dispatch) => {
  return {
    onReload: (count, sources) => dispatch(fetchRandomComments(count, sources)),
    onReset: (comments) => Promise.all(_.chain(comments)
      .map(comment => dispatch(resetCommentTags(comment.id, comment.tags)))
      .value())
      .then(() => dispatch(fetchTagCounts())),
    onAcceptAll: (comments) => Promise.all(_.chain(comments)
      .flatMap(({id, suggestion}) => _.chain(suggestion)
        .map('1')
        .flatMap(tag => dispatch(addCommentTag(id, tag)))
        .value())
      .value())
      .then(() => dispatch(fetchTagCounts()))
  }
}

const TaggerListContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(TaggerList)

export default TaggerListContainer