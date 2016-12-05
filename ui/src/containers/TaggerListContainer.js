import {connect} from 'react-redux'
import _ from 'lodash'

import {fetchRandomComments, resetCommentTags, addCommentTag, fetchTagCounts} from '../actions/TaggerActions'
import TaggerList from '../components/TaggerList.jsx'

const mapStateToProps = (state) => ({
  comments: state.tagger.comments,
  sources: state.tagger.sources
});

const mapDispatchToProps = (dispatch) => ({
  onReload: (count, sources) => dispatch(fetchRandomComments(count, sources)),
  onReset: (comments) => Promise.all(_.forEach((comment) => dispatch(resetCommentTags(comment))))
    .then(() => dispatch(fetchTagCounts())),
  onAcceptAll: (comments) => Promise.all(
    _.chain(comments)
      .values()
      .map((comment) => ({
        comment,
        best: _.max(_.reject(_.keys(comment.prediction), (k) => comment.prediction[k] > 2), (k) => comment.prediction[k])
      }))
      .filter('best')
      .forEach(({comment, best}) => dispatch(addCommentTag(comment, best)))
      .value())
    .then(() => dispatch(fetchTagCounts()))
});

const TaggerListContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(TaggerList);

export default TaggerListContainer;