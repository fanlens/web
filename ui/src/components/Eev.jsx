import React from 'react';
import classnames from 'classnames';

const Message = ({from, created, children}) => {
  const isEev = from.id !== "user";
  const icon = isEev ? '/cdn/img/logo.png' : '/cdn/img/logo.png';
  return <li className={classnames('clearfix', {
    'left': isEev,
    'right': !isEev
  })}>
    <span className={classnames('chat-img', {'pull-left': isEev, 'pull-right': !isEev})}>
      <img src={icon} alt="User Avatar"/>
    </span>
    <div className="chat-body clearfix">
      <div className="header">
        <strong className="primary-font">{from.id}</strong>
        <small className="pull-right text-muted"><i className="fa fa-clock-o"/>&nbsp;{created}</small>
      </div>
      <p>
        {children}
      </p>
    </div>
  </li>;
};


const Eev = ({ready, messages, onSend}) => {
  let msg = null;
  const sendAndClear = () => {
    onSend(msg.value);
    msg.value = ''
  };
  return (<div id="evaluator" className="container-fluid">
    <div className="row">
      <div className="col-md-12">
        <div className="chat-message">
          <ul className="chat">
            {messages.map((msg, idx) => (
              <Message key={idx} {...msg}>
                {msg["text"]}
              </Message>
            ))}
          </ul>
        </div>
        <div className="chat-input">
          <div className="input-group">
            <textarea rows="1"
                      className="form-control border no-shadow no-rounded input-lg"
                      placeholder="Type your message here"
                      ref={(c) => msg = c}
                      onKeyUp={(e) => ready && (e.nativeEvent.keyCode === 13 && e.nativeEvent.shiftKey) && sendAndClear()}/>
            <span className="input-group-btn">
                <button className={classnames('btn', 'btn-success', 'no-rounded', 'btn-lg', {'disabled': !ready})}
                        type="button"
                        onClick={() => ready && sendAndClear() }>
                  <i className="fa fa-paper-plane" aria-hidden="true"/> Send
                </button>
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>);
};

export default Eev;


