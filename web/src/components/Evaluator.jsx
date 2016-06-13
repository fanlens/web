import React from 'react';

const Evaluator = () => (
  <div className="form-group">
    <div className="row">
      <div className="col-md-12">
        <label for="comment">Post:</label>
                <textarea className="form-control" placeholder="Type your comment here and press evaluate..." rows="5"
                          id="comment"/>
      </div>
    </div>
    <div className="row" style={{marginTop:'1em'}}>
      <div className="col-md-12">
        <div className="btn-group-justified">
          <div className="btn-group">
            <label type="button" className="btn btn-success">
              <em className="glyphicon glyphicon-tags"/> Evaluate
            </label>
          </div>
          <div className="btn-group">
            <label type="button" className="btn btn-primary">
              <em className="glyphicon glyphicon-send"/> Post Now
            </label>
          </div>
          <div className="btn-group">
            <label type="button" className="btn btn-info">
              <em className="glyphicon glyphicon-hourglass"/> Post Delayed
            </label>
          </div>
        </div>
      </div>
    </div>
  </div>
);

export default Evaluator
