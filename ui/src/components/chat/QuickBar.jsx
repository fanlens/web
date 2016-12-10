import React from "react";
import {connect} from "react-redux";
import Chip from "material-ui/Chip";
import Avatar from "material-ui/Avatar";
import SvgIconInfo from "material-ui/svg-icons/action/info";
import {updateInputText} from "../../actions/AppActions";

const quickBarStyle = {
  wrapper: {
    display: 'flex',
    flexWrap: 'wrap',
    paddingLeft: '0.5em',
    paddingRight: '0.5em',
  },
  chip: {
    margin: '4px',
    paddingRight: '0.125rem',
    textAlign: 'center',
  }
};

const Quick = ({color, icon, text, onSuggest}) => (
  <Chip className="col-xs quick-suggestion"
        style={quickBarStyle.chip}
        onTouchTap={(evt) => onSuggest(text)}>
    <Avatar color={color || "#444"} icon={icon || <SvgIconInfo />}/>
    {text}
  </Chip>
);

const QuickBar = ({suggestions, onSuggest}) => (
  <div className="row center-xs quickbar" style={quickBarStyle.wrapper}>
    {suggestions.map((suggestion, idx) => (
      <Quick key={idx} onSuggest={onSuggest} {...suggestion}/>
    ))}
  </div>
);

const mapStateToProps = (state) => ({
  suggestions: state.app.suggestions.quick
});

const mapDispatchToProps = (dispatch) => ({
  onSuggest: (text) => dispatch(updateInputText(text)),
});

export default connect(mapStateToProps, mapDispatchToProps)(QuickBar);