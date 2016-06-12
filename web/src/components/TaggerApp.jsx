import React from 'react'

import Panel from './Panel.jsx'
import SourcesPanelContainer from '../containers/SourcesPanelContainer'
import TagSetPanelContainer from '../containers/TagSetPanelContainer'
import TaggerListContainer from '../containers/TaggerListContainer'

const ToolsPanel = () => (
  <Panel id="panel-element-tools" title="Tools">
    <ul className="nav nav-pills nav-stacked">
      <li className="active"><a data-toggle="pill" href="#tagger">Tagger</a></li>
      <li><a data-toggle="pill" href="#evaluator">Evaluator</a></li>
    </ul>
  </Panel>
);

const Sidebar = () => (
  <div className="panel-group" id="panel-sidebar">
    <ToolsPanel />
    <SourcesPanelContainer />
    <TagSetPanelContainer />
  </div>
);

const TaggerApp = () => (
  <div className="container-fluid">
    <div className="row">
      <aside className="col-sm-3" id="sidebar">
        <Sidebar />
      </aside>
      <main className="col-sm-9 tab-content" id="main">
        <div id="evaluator" className="tab-pane fade">
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
        </div>
        <div id="tagger" className="tab-pane fade in active">
          <TaggerListContainer />
        </div>
      </main>
    </div>
  </div>
)

export default TaggerApp