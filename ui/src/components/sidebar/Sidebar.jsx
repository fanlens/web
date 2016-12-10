import React from "react";
import {connect} from "react-redux";
import Drawer from "material-ui/Drawer";
import AppBar from "material-ui/AppBar";
import Divider from "material-ui/Divider";
import IconButton from "material-ui/IconButton";
import NavigationClose from "material-ui/svg-icons/navigation/close";
import {setDrawerState} from "../../actions/AppActions";
import SourcesList from "./SourcesList.jsx";
import OptionsList from "./OptionsList.jsx";

const Sidebar = ({open, onHide}) => (
  <aside>
    <Drawer
      width={384}
      open={open}>
      <AppBar
        title="Options"
        style={{backgroundColor: 'rgb(120, 120, 120)'}}
        iconElementLeft={<IconButton onTouchTap={onHide}><NavigationClose /></IconButton>}
      />
      <SourcesList initiallyOpen={true}/>
      <Divider />
      <OptionsList initiallyOpen={true}/>
    </Drawer>
  </aside>
);

const mapStateToProps = (state) => ({
  open: state.app.drawer.open,
});

const mapDispatchToProps = (dispatch) => ({
  onHide: () => dispatch(setDrawerState(false)),
});

export default connect(mapStateToProps, mapDispatchToProps)(Sidebar)
