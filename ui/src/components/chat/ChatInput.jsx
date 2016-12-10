import _ from "lodash";
import React from "react";
import ReactDOM from "react-dom";
import {connect} from "react-redux";
import AutoComplete from "material-ui/AutoComplete";
import RaisedButton from "material-ui/RaisedButton";
import MenuItem from "material-ui/MenuItem";
import Toggle from "material-ui/Toggle";
import SvgIconNavigationMenu from "material-ui/svg-icons/navigation/menu";
import SvgIconHelp from "material-ui/svg-icons/action/help";
import SvgIconHelpOutline from "material-ui/svg-icons/action/help-outline";
import IconButton from "material-ui/IconButton";
import {sendMessage} from "../../actions/EevActions";
import * as AppActions from "../../actions/AppActions";
import QuickBar from "./QuickBar.jsx";

const Suggestion = ({text, icon}) => ({
  text,
  value: <MenuItem primaryText={text} rightIcon={icon}/>
});

const ChatInput = ({input, help, suggestions, onSetInputActive, onUpdateText, onSubmit, onToggleDrawer}) => (
  <div style={{margin: 0, backgroundColor: 'white', padding: '0.5em 0.75em'}}>
    {help.active && (
      <div className="row middle-xs">
        <div className="col-xs">
          <QuickBar />
        </div>
      </div>
    )}
    <div className="row middle-xs">
      <div className="col-xs-1" style={{zIndex: 10, margin: 0, padding: 0, flexBasis: 0}}>
        <IconButton tooltip="Menu" onClick={(evt) => onToggleDrawer()}>
          <SvgIconNavigationMenu />
        </IconButton>
      </div>
      <div className="col-xs">
        <AutoComplete
          id="guiframeworkssucksometimes"
          hintText="Chat with eev..."
          multiLine={true}
          fullWidth={true}
          rowsMax={3}
          openOnFocus={true}
          filter={AutoComplete.caseInsensitiveFilter}
          maxSearchResults={7}
          dataSource={suggestions.active ? _.map(suggestions.all, Suggestion) : []}
          onFocus={(evt) => onSetInputActive(true)}
          onBlur={(evt) => onSetInputActive(false)}
          onUpdateInput={(txt) => onUpdateText(txt)}
          onKeyDown={(evt) => {
            if (evt.keyCode === 13 && !evt.shiftKey) {
              onSubmit(input.text);
              evt.preventDefault();
              evt.stopPropagation();
            }
          }}
          searchText={input.text}/>
      </div>
      <div className="col-xs-2">
        <RaisedButton
          label="Send"
          disabled={!input.text}
          disabledBackgroundColor={input.active ? 'hsl(187, 30%, 80%)' : 'hsl(0, 0%, 90%)' }
          fullWidth={true}
          onTouchTap={(evt) => onSubmit(input.text)}
          primary={true}
        />
      </div>
    </div>
  </div>
);

const mapStateToProps = (state) => ({
  input: state.app.input,
  help: state.app.help,
  suggestions: state.app.suggestions,
});

const mapDispatchToProps = (dispatch) => ({
  onToggleDrawer: () => dispatch(AppActions.toggleDrawer()),
  onSetInputActive: (active) => dispatch(AppActions.setInputActive(active)),
  onUpdateText: (text) => dispatch(AppActions.updateInputText(text)),
  onSubmit: (text) => _.forEach([
    AppActions.updateInputText(""),
    AppActions.addSuggestion(text),
    sendMessage(text)
  ], dispatch)
});


export default connect(mapStateToProps, mapDispatchToProps)(ChatInput)