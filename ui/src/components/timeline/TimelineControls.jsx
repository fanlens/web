import React from "react";
import {connect} from "react-redux";
import map from "lodash/fp/map";
import isEmpty from "lodash/fp/isEmpty";
import head from "lodash/fp/head";
import values from "lodash/fp/values";
import DatePicker from 'material-ui/DatePicker';
import TimePicker from 'material-ui/TimePicker';
import Paper from 'material-ui/Paper';
import RaisedButton from 'material-ui/RaisedButton';
import FlatButton from 'material-ui/FlatButton';
import NavigationRefresh from 'material-ui/svg-icons/navigation/refresh';
import ActionDateRange from 'material-ui/svg-icons/action/date-range';
import DropDownMenu from 'material-ui/DropDownMenu';
import MenuItem from 'material-ui/MenuItem';
import Dialog from 'material-ui/Dialog';
import Slider from 'material-ui/Slider';
import Toggle from 'material-ui/Toggle';
import {fetchComments} from '../../actions/ActivitiesActions';


const min = 0;
const max = 200;
const power = 4;

const transform = (value) => Math.floor((Math.round((Math.exp(power * value / max) - 1) / (Math.exp(power) - 1) * max) + 1) / 2) * 2;
const reverse = (value) => (1 / power) * Math.log(((Math.exp(power) - 1) * value / max) + 1) * max;


const controlHeight = '3em';
const ControlFrame = ({className, children}) => (
  <Paper className={className} zDepth={1} rounded={true}
         style={{
           textAlign: 'center',
           display: 'inline-block',
           padding: '0 0.5em',
           width: '100%',
           height: controlHeight
         }}>
    {children}
  </Paper>
);

const DateTimePicker = ({className, label, origDate, onChange}) => (
  <div className={className}>
    <span style={{marginRight: '0.5em'}}>
    {label}
    </span>
    <DatePicker
      onChange={(_, date) => onChange(new Date(new Date(date.setHours(origDate.getHours())).setMinutes(origDate.getMinutes())))}
      style={{display: 'inline-block'}}
      textFieldStyle={{width: '6em'}}
      hintText="1970/01/01"
      container="inline"
      autoOk={false}
      mode="landscape"
      value={origDate}
    />
    <TimePicker
      onChange={(_, date) => onChange(new Date(new Date(origDate.setHours(date.getHours())).setMinutes(date.getMinutes())))}
      format="24hr"
      hintText="00:00"
      style={{display: 'inline-block'}}
      textFieldStyle={{width: '3em'}}
      autoOk={false}
      value={origDate}
    />
  </div>
);

class TimelineControls extends React.Component {
  state = {
    selectedTagsetId: null,
    datePickOpen: false,
    fromDate: new Date(new Date().getTime() - (24 * 60 * 60 * 1000)),
    toDate: new Date(),
    slider: 10,
    random: true,
  };

  _closeDatePicker = () => this.setState({datePickOpen: false});

  componentWillReceiveProps(nextProps) {
    const {tagSets} = nextProps;
    this.setState({selectedTagsetId: this.state.selectedTagsetId || (!isEmpty(tagSets) && head(values(tagSets)).id)});
  }

  render() {
    const {tagSets, sources, onRefresh} = this.props;
    return (
      <div className="row middle-sm center-sm" style={{padding: '0.5em', overflow: 'hidden'}}>
        <div className="col-sm-3">
          <div style={{height: '3em'}}>
            <ControlFrame>
              <DropDownMenu
                style={{height: '3em', marginTop: '-0.31em', width: '100%'}}
                value={this.state.selectedTagsetId}
                disabled={isEmpty(tagSets)}
                onChange={(_, __, selectedTagsetId) => this.setState({selectedTagsetId})}
                autoWidth={false}
              >
                {map(({id, title}) => (<MenuItem key={id} value={id} primaryText={title}/>))(tagSets)}
              </DropDownMenu>
            </ControlFrame>
          </div>
        </div>

        <div className="col-sm-3">
          <ControlFrame>
            <div className="row middle-xs center-xs" style={{height: '100%'}}>
              <div className="col-xs-2">
                {this.state.slider}
              </div>
              <div className="col-xs middle-xs">
                <Slider
                  style={{marginTop: '3em', paddingRight: '0.5em'}}
                  min={min}
                  max={max}
                  step={max / 100}
                  value={reverse(this.state.slider)}
                  onChange={(event, value) => this.setState({slider: transform(value)})}
                />
              </div>
            </div>
          </ControlFrame>
        </div>

        <div className="col-sm-2">
          <RaisedButton
            icon={<ActionDateRange/>}
            label="Range"
            buttonStyle={{height: controlHeight}}
            fullWidth={true}
            onTouchTap={() => this.setState({datePickOpen: true})}/>
        </div>

        <Dialog
          title={
            <h1 style={{textAlign: 'center'}}>
              <ActionDateRange style={{marginBottom: '-0.125em'}}/>
              Pick Date Range
            </h1>
          }
          actions={[
            <FlatButton
              label="Close"
              primary={true}
              keyboardFocused={true}
              onTouchTap={this._closeDatePicker}
            />
          ]}
          modal={false}
          open={this.state.datePickOpen}
          onRequestClose={this._closeDatePicker}
        >
          <div className="row center-sm middle-sm">
            <DateTimePicker
              className="col-sm"
              label="From"
              origDate={this.state.fromDate}
              onChange={(fromDate) => this.setState({
                fromDate,
                toDate: new Date(Math.max(fromDate, this.state.toDate))
              })}
            />
            <DateTimePicker
              className="col-sm"
              label="To"
              origDate={this.state.toDate}
              onChange={(toDate) => this.setState({
                toDate,
                fromDate: new Date(Math.min(toDate, this.state.fromDate))
              })}
            />
            <div className="col-sm">
              <Toggle
                label="Random Sample"
                toggled={this.state.random}
                onToggle={(_, isInputChecked) => this.setState({random: isInputChecked})}
              />
            </div>
          </div>
        </Dialog>
        <div className="col-sm-3">
          <RaisedButton
            label="Fetch Comments"
            labelPosition="after"
            fullWidth={true}
            primary={true}
            disabled={this.state.selectedTagsetId === null}
            icon={<NavigationRefresh/>}
            buttonStyle={{height: controlHeight}}
            onTouchTap={() => onRefresh(
              this.state.slider,
              sources,
              this.state.fromDate.toISOString(),
              this.state.toDate.toISOString(),
              [tagSets[this.state.selectedTagsetId]],
              this.state.random)}
          />
        </div>
      </div>
    );
  }
}

const mapStateToProps = (state) => ({
  tagSets: state.activities.tagSets,
  sources: state.activities.sources,
});

const mapDispatchToProps = (dispatch) => ({
  onRefresh: (count, sources, since, until, tagSets, random) =>
    dispatch(fetchComments(count, sources, since, until, tagSets, random)),
});

export default connect(mapStateToProps, mapDispatchToProps)(TimelineControls);