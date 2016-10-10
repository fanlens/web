import React from 'react'

import Panel, {PanelButton} from './Panel.jsx';
import SourceElement from './Source.jsx';

const SourcesPanel = ({sources, onSourceSelected}) => (
  <Panel id="panel-element-sources" title="Sources">
    <div className="list-group">
      {sources.map((source) => (
        <PanelButton key={source.id} active={source.active} onClick={() => onSourceSelected(source)}>
          <SourceElement source={source}/>
        </PanelButton>
      ))}
    </div>
  </Panel>
)

export default SourcesPanel
