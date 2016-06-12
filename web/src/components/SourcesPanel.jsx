import React from 'react';

import Panel, {PanelButton} from './Panel.jsx';

const SourceElement = ({source}) => (
  <div className="ellipsis">
    <img className="fb-sources-icon" src={"https://graph.facebook.com/" + source + "/picture"}/>
    <span className="fb-sources-text"> Facebook > {source} </span>
  </div>
)

const SourcesPanel = ({sources, onSourceSelected}) => (
  <Panel id="panel-element-sources" title="Sources">
    <div className="list-group">
      {sources.map((source) => (
        <PanelButton key={source.id} {...source} onClick={() => onSourceSelected(source.id)}>
          <SourceElement source={source.id}/>
        </PanelButton>
      ))}
    </div>
  </Panel>
)

export default SourcesPanel
