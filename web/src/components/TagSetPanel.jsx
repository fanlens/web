import React from 'react';

import Panel, {PanelButton} from './Panel.jsx';

const TagSetElement = ({title, tags}) => (
  <div style={{lineHeight:'1.75em', whiteSpace:'normal'}}>{title}:<br/>
    {tags.map((tag, idx) => (
      <span key={idx} className="badge" style={{marginRight:'0.5em', display:'inline-block'}}>
        <span className="glyphicon glyphicon-tag" aria-hidden="true"></span> {tag}
      </span>
    ))}
  </div>
)

const TagSetPanel = ({tagSets, onTagSetSelected}) => (
  <Panel id="panel-element-tagsets" title="Tag Sets">
    {tagSets.map(tagSet => (
      <PanelButton key={tagSet.id} {...tagSet} onClick={() => onTagSetSelected(tagSet.id)}>
        <TagSetElement {...tagSet}/>
      </PanelButton>))}
  </Panel>
)

export default TagSetPanel;