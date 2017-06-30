import React from "react";
import {connect} from "react-redux";
import {List, ListItem} from "material-ui/List";
import Toggle from "material-ui/Toggle";
import SvgIconSettings from "material-ui/svg-icons/action/settings";
import SvgIconHelp from "material-ui/svg-icons/action/help";
import SvgIconHelpOutline from "material-ui/svg-icons/action/help-outline";
import SvgIconFlashOn from "material-ui/svg-icons/image/flash-on";
import SvgIconFlashOff from "material-ui/svg-icons/image/flash-off";
import {toggleHelp, toggleSuggestions} from "../../actions/AppActions";

const OptionsList = ({initiallyOpen = false, helpActive, suggestionsActive, onToggleHelp, onToggleSuggestions}) => (
  <List>
    <ListItem
      primaryText="Options"
      initiallyOpen={initiallyOpen}
      leftIcon={<SvgIconSettings/>}
      nestedItems={[
        <ListItem
          key={0}
          primaryText="Help"
          rightIcon={helpActive ? <SvgIconHelp/> : <SvgIconHelpOutline/>}
          leftCheckbox={
            <Toggle
              toggled={helpActive}
              onToggle={onToggleHelp}/>
          }
        />,
        <ListItem
          key={1}
          primaryText="Suggestions"
          rightIcon={suggestionsActive ? <SvgIconFlashOn/> : <SvgIconFlashOff/>}
          leftCheckbox={
            <Toggle
              toggled={suggestionsActive}
              onToggle={onToggleSuggestions}/>
          }
        />
      ]}
    />
  </List>
);

const mapStateToProps = (state) => ({
  helpActive: state.app.help.active,
  suggestionsActive: false,
});

const mapDispatchToProps = (dispatch) => ({
  onToggleHelp: () => dispatch(toggleHelp()),
  onToggleSuggestions: () => dispatch(toggleSuggestions()),
});

export default connect(mapStateToProps, mapDispatchToProps)(OptionsList)
