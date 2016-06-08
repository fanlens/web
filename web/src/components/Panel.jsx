import React from 'react';
import classnames from 'classnames';


export const PanelButton = ({active, children, onClick}) => {
  let btnClasses = classnames('list-group-item', 'btn', {'active': active});
  return (
    <button type="button" className={btnClasses} onClick={() => onClick()}>
      {children}
    </button>
  );
}

const PanelHeading = ({title, panelBodyRef}) => (
  <div className='panel-heading'>
    <a className="panel-title" data-toggle="collapse" href={panelBodyRef}>
      {title}<strong className="caret"></strong>
    </a>
  </div>
)

const Panel = ({id, title, children}) => {
  return (
    <div className="panel panel-default">

      <PanelHeading title={title} panelBodyRef={'#' + id}/>

      <div id={id} className="panel-collapse collapse in">
        <div className="panel-body">
          <div className="list-group">
            {children}
          </div>
        </div>
      </div>
    </div>
  );
}

export default Panel;