import React from 'react';
import _ from 'lodash'

//TODO refactor
const Evaluator = ({loading, suggestion, onEvaluate, onPost, onDelayed}) => {
  let input;
  return (
    <div className="container-fluid">
      <div className="row">
        <div className="container-fluid tool">
          <div className="row">
            <div className="col-md-12 form-group">
              <label for="comment">Post:</label>
                <textarea className="form-control" placeholder="Type your comment here and press evaluate..." rows="5"
                          id="comment" ref={node => input = node}/>
            </div>
          </div>
          <div className="row" style={{marginTop:'1em'}}>
            <div className="col-md-12">
              <div className="btn-group-justified">
                <div className="btn-group">
                  <label type="button" className="btn btn-success" onClick={() => onEvaluate(input.value.trim())}>
                    {loading ?
                      <span><em className="glyphicon glyphicon-hdd"/> Loading...</span> :
                      <span><em className="glyphicon glyphicon-tags"/> Evaluate</span> }
                  </label>
                </div>
                <div className="btn-group">
                  <label type="button" className="btn btn-primary" onClick={() => onPost()}>
                    <em className="glyphicon glyphicon-send"/> Post Now
                  </label>
                </div>
                <div className="btn-group">
                  <label type="button" className="btn btn-info" onClick={() => onDelayed()}>
                    <em className="glyphicon glyphicon-hourglass"/> Post Delayed
                  </label>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      {_.isEmpty(suggestion) ? '' :
        <div className="row">
          <div className="container-fluid tool">
            <div className="row">
              <div className="col-md-12">
                {_.map(suggestion, ([percent, tag]) => <span key={tag} className="badge">{percent * 100} {tag}</span>)}
              </div>
            </div>
          </div>
        </div>
      }
    </div>
  );
}

export default Evaluator
