import React from "react";
import {connect} from "react-redux";
import {Link} from "react-router";
import Avatar from "material-ui/Avatar";
import {ListItem} from "material-ui/List";
import FlatButton from "material-ui/FlatButton";

const firstUpper = (str) => str.charAt(0).toUpperCase() + str.slice(1);
const oppositeOrientation = (orientation) => orientation === 'left' ? 'right' : 'left';

const prepared = {
  // terms: <div>Many Terms</div>,
  // team: <FlatButton label="Head to Team Page" containerElement={<Link to="/team"/>}/>,
  // help: <div>Halp</div>,
  // connect: <div>Connect</div>,
  // ignore: null,
};
const chatMessageStyle = (orientation, avatar) => ({
  style: {
    cursor: 'text',
    fontSize: '14px',
    marginBottom: '0.5em',
    backgroundColor: orientation === 'right' ? 'hsla(203, 78%, 92%, 1)' : 'hsla(203, 10%, 95%, 1)',
    textAlign: orientation,
    borderRadius: '0.25em',
    [`margin${firstUpper(oppositeOrientation(orientation))}`]: '72px'
  },
  innerDivStyle: {
    [`padding${firstUpper(orientation)}`]: '72px'
  },
  [`${orientation}Avatar`]: <Avatar backgroundColor="transparent" src={avatar}/>
});
const userOrDemo = (user) => user.email === 'demo@example.com' ?
  '/cdn/img/blank-profile.svg' :
  `https://www.gravatar.com/avatar/${user.email_md5}`;
const rightMessageStyle = (user) => chatMessageStyle('right', userOrDemo(user));
const leftMessageStyle = () => chatMessageStyle('left', '/cdn/img/logo.png');
const selectMessageStyle = (from) => from.startsWith('eev') ? leftMessageStyle : rightMessageStyle;

const Message = ({id, from, user, meta: {internal} = {}, children}) => {
  if (internal === 'ignore') {
    return null;
  }
  return (
    <ListItem
      disableFocusRipple={true}
      disableTouchRipple={true}
      primaryText={
        <span style={{color: id ? 'black' : 'darkgrey'}}>
        {prepared[internal] || children}
      </span>
      }
      {... selectMessageStyle(from)(user)}
    />
  );
};

const mapStateToProps = (state) => ({
  user: state.app.user
});

export default connect(mapStateToProps)(Message);