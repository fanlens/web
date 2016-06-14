import React from 'react';

const Evaluator = ({loading, suggestion, onEvaluate, onPost, onDelayed}) => {
  let input;
  return (
    <div className="form-group">
      <div className="row">
        <div className="col-md-12">
          <label for="comment">Post:</label>
                <textarea className="form-control" placeholder="Type your comment here and press evaluate..." rows="5"
                          id="comment" ref={node => input = node}/>
        </div>
      </div>
      <div className="row" style={{marginTop:'1em'}}>
        <div className="col-md-12">
          <div className="btn-group-justified">
            <div className="btn-group">
              <label type="button" className="btn btn-success"  onClick={() => onEvaluate(input.value.trim())}>
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
  );
}

export default Evaluator
