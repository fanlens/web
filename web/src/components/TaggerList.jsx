import React from 'react'
import _ from 'lodash'

import TaggerContainer from '../containers/TaggerContainer'


const TaggerList = ({comments, sources, onReload, onReset}) => (
  <div className="container-fluid">
    <div className="row">
      <ul className="list-group">
        {_.map(_.sortBy(comments, 'id'), (comment) => {
          return (
            <li key={comment.id} className="list-group-item">
              <TaggerContainer id={comment.id}/>
            </li>
          );
        })}
      </ul>
    </div>
    <div className="row controls">
      <div className="btn-group-justified">
        <div className="btn-group">
          <label className="btn btn-default" type="button" onClick={() => onReload(sources)}>
            <span className="glyphicon glyphicon-refresh" aria-hidden="true"></span> New Batch
          </label>
        </div>
        <div className="btn-group">
          <label className="btn btn-default" type="button" onClick={() => onReset(comments)}>
            <span className="glyphicon glyphicon-erase" aria-hidden="true"></span> Reset Batch
          </label>
        </div>
      </div>
    </div>
  </div>
);

export default TaggerList;