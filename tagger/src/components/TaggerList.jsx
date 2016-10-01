import React from 'react'
import _ from 'lodash'

import TaggerContainer from '../containers/TaggerContainer'


class TaggerList extends React.Component {
  constructor(props) {
    super(props);
    if (this.props.comments.length !== 8) {
      this.props.onReload(8, this.props.sources);
    }
  }

  render() {
    const {comments, sources, onReload, onAcceptAll, onReset} = this.props;
    return (<div className="container-fluid">
      <div className="row">
        <ul className="list-group">
          {_.map(_.sortBy(comments, 'id'), (comment) => {
            return (
              <li key={comment.id} className="list-group-item col-md-6">
                <TaggerContainer id={comment.id}/>
              </li>
            );
          })}
        </ul>
      </div>
      <div className="row controls">
        <div className="btn-group-justified">
          <div className="btn-group">
            <label className="btn btn-primary" type="button" onClick={() => onReload(comments.length, sources)}>
              <span className="glyphicon glyphicon-refresh" aria-hidden="true"/> New Batch
            </label>
          </div>
          <div className="btn-group">
            <label className="btn btn-success" type="button" onClick={() => onAcceptAll(comments)}>
              <span className="glyphicon glyphicon-tags" aria-hidden="true"/> Accept All
            </label>
          </div>
          <div className="btn-group">
            <label className="btn btn-warning" type="button" onClick={() => onReset(comments)}>
              <span className="glyphicon glyphicon-erase" aria-hidden="true"/> Reset Batch
            </label>
          </div>
        </div>
      </div>
    </div>);
  }
}

export default TaggerList;