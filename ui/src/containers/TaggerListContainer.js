import {connect} from 'react-redux'
import _ from 'lodash'

import {fetchRandomComments, resetCommentTags, addCommentTag, fetchTagCounts} from '../actions/TaggerActions'
import TaggerList from '../components/TaggerList.jsx'

const mapStateToProps = (state) => {
  return {
    comments: _.values(state.tagger.comments),
    sources: state.tagger.sources
  };
};

const mapDispatchToProps = (dispatch) => {
  return {
    onReload: (count, sources) => dispatch(fetchRandomComments(count, sources)),
    onReset: (comments) => Promise.all(_.chain(comments)
      .map(comment => dispatch(resetCommentTags(comment)))
      .value())
      .then(() => dispatch(fetchTagCounts())),
    onAcceptAll: (comments) => Promise.all(_.chain(comments)
      .flatMap((comment) => _.chain(comment.suggestion)
        .map('1')
        .flatMap(tag => dispatch(addCommentTag(comment, tag)))
        .value())
      .value())
      .then(() => dispatch(fetchTagCounts()))
  }
};

const TaggerListContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(TaggerList);

export default TaggerListContainer;