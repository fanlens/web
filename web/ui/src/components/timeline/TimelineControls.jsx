import React from "react";
import {connect} from "react-redux";
import {Link} from "react-router-dom";
import map from "lodash/fp/map";
import isEmpty from "lodash/fp/isEmpty";
import head from "lodash/fp/head";
import values from "lodash/fp/values";
import defaults from "lodash/fp/defaults";
import take from "lodash/fp/take";
import reduce from "lodash/fp/reduce";
import DatePicker from 'material-ui/DatePicker';
import TimePicker from 'material-ui/TimePicker';
import Paper from 'material-ui/Paper';
import RaisedButton from 'material-ui/RaisedButton';
import FlatButton from 'material-ui/FlatButton';
import ContentInbox from 'material-ui/svg-icons/content/inbox';
import ContentFilterList from 'material-ui/svg-icons/content/filter-list';
import HourglassEmpty from 'material-ui/svg-icons/action/hourglass-empty';
import DropDownMenu from 'material-ui/DropDownMenu';
import MenuItem from 'material-ui/MenuItem';
import Dialog from 'material-ui/Dialog';
import Slider from 'material-ui/Slider';
import Toggle from 'material-ui/Toggle';
import ActionGavel from 'material-ui/svg-icons/action/gavel';
import FloatingActionButton from 'material-ui/FloatingActionButton';
import {fetchComments} from '../../actions/activities';
import * as tlActions from "../../actions/app/timeline";

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
    <div className="row start-xs middle-xs">
      <div className="col-xs-2 end-xs">{label}</div>
      <div className="col-xs">
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
    </div>
  </div>
);

class TimelineControls extends React.Component {
  state = {
    rangePickOpen: false,
    sliderValue: null,
  };

  _closeDatePicker = () => this.setState({rangePickOpen: false});

  componentWillReceiveProps(nextProps) {
    const {allTagSets, setTagSets, allSources, setSources, count} = nextProps;
    if (isEmpty(this.props.tagSets) && !isEmpty(allTagSets)) {
      setTagSets(take(1, values(allTagSets)))
    }
    if (isEmpty(this.props.sources) && !isEmpty(allSources)) {
      setSources(take(1, values(allSources)))
    }
    this.setState({sliderValue: count})
  }

  render() {
    const {
      allSources, sources, random, count, allTagSets, isFetching = false, tagSets = [],
      onRange, onRandom, onCount, onSelectTagSet, onSelectSource, onFetch
    } = this.props;
    const since = new Date(this.props.since);
    const until = new Date(this.props.until);
    return (
      <div className="row middle-xs center-xs" style={{padding: '0 0 0.5em 0', margin: 0, overflow: 'hidden'}}>
        <div className="col-sm-4 col-xs-12">
          <div style={{height: controlHeight, marginTop: '0.5em'}}>
            <ControlFrame>
              <DropDownMenu
                style={{height: '3em', marginTop: '-0.31em', width: '100%'}}
                value={isEmpty(tagSets) ? -1 : head(tagSets).id}
                disabled={isEmpty(tagSets)}
                onChange={(_, __, selectedTagSetId) => onSelectTagSet(selectedTagSetId)}
                autoWidth={false}
                multiple={false}
              >
                {map(({id, title}) => (<MenuItem key={id} value={id} primaryText={title}/>))(allTagSets)}
              </DropDownMenu>
            </ControlFrame>
          </div>
        </div>

        <div className="col-sm-4 col-xs-12">
          <div style={{height: controlHeight, marginTop: '0.5em'}}>
            <ControlFrame>
              <DropDownMenu
                style={{height: '3em', marginTop: '-0.31em', width: '100%'}}
                value={isEmpty(sources) ? -1 : head(sources).id}
                disabled={isEmpty(tagSets)}
                onChange={(_, __, selectedSourceId) => onSelectSource(selectedSourceId)}
                autoWidth={false}
                multiple={false}
              >
                {map(({id, type, slug}) => (
                  <MenuItem key={id} value={id} primaryText={`${type} > ${slug}`}/>)
                )(allSources)}
              </DropDownMenu>
            </ControlFrame>
          </div>
        </div>

        <div className="col-sm-2 col-xs-6">
          <RaisedButton
            icon={<ContentFilterList/>}
            label="Range"
            buttonStyle={{height: controlHeight}}
            style={{marginTop: '0.5em'}}
            fullWidth={true}
            onTouchTap={() => this.setState({rangePickOpen: true})}/>
        </div>

        <div className="col-sm-2 col-xs-6">
          <RaisedButton
            label="Fetch"
            labelPosition="after"
            fullWidth={true}
            primary={true}
            disabled={isEmpty(tagSets) || isFetching}
            icon={isFetching ? <HourglassEmpty/> : <ContentInbox/>}
            style={{marginTop: '0.5em'}}
            buttonStyle={{height: controlHeight}}
            onTouchTap={() => onFetch()}
          />
        </div>

        <Dialog
          title={
            <h1 style={{textAlign: 'center'}}>
              <ContentFilterList style={{marginBottom: '-0.125em'}}/>
              Set Comment Range
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
          open={this.state.rangePickOpen}
          onRequestClose={this._closeDatePicker}
        >
          <div className="row center-xs middle-xs">
            <DateTimePicker
              className="col-md col-xs-12"
              label="From"
              origDate={since}
              onChange={(fromDate) => onRange(
                fromDate,
                new Date(Math.max(fromDate, until))
              )}
            />
          </div>
          <div className="row center-xs middle-xs">
            <DateTimePicker
              className="col-md col-xs-12"
              label="To"
              origDate={until}
              onChange={(toDate) => onRange(
                new Date(Math.min(toDate, since)),
                toDate
              )}
            />
          </div>
          <div className="row center-xs middle-xs">
            <div className="col-md-8 col-xs-12">
              <div className="row middle-xs center-xs" style={{height: '100%'}}>
                <div className="col-xs-2">
                  {this.state.sliderValue || count}
                </div>
                <div className="col-xs middle-xs">
                  <Slider
                    style={{marginTop: '3em', paddingRight: '0.5em'}}
                    min={min}
                    max={max}
                    step={max / 100}
                    value={reverse(this.state.sliderValue || count)}
                    onChange={(_, sliderValue) => this.setState({sliderValue: transform(sliderValue)})}
                    onDragStop={() => {
                      onCount(this.state.sliderValue);
                      this.setState({sliderValue: null});
                    }}
                  />
                </div>
              </div>
            </div>
            <div className="col-md-4 col-xs-12">
              <Toggle
                style={{width: null, margin: 'auto'}}
                label="Random Sample"
                toggled={random}
                onToggle={(_, isInputChecked) => onRandom(isInputChecked)}
              />
            </div>
          </div>
        </Dialog>

        <Link to={`/${fanlensVersion}/ui/evaluator`} style={{
          float: 'right',
          position: 'fixed',
          right: '8px',
          bottom: '92px',
          zIndex: 10000
        }}>
          <FloatingActionButton>
            <ActionGavel/>
          </FloatingActionButton>
        </Link>
      </div>
    );
  }
}

const mapStateToProps = (state) => defaults({
  allTagSets: state.activities.tagSets,
  allSources: state.activities.sources,
})(state.app.timeline);

const mapDispatchToProps = (dispatch, props) => ({
    onRange: (since, until) => dispatch(tlActions.setRange(since, until)),
    onRandom: (random) => dispatch(tlActions.setRandom(random)),
    onCount: (count) => dispatch(tlActions.setCount(count)),
    setTagSets: (tagSets) => dispatch(tlActions.setTagSets(tagSets)),
    setSources: (sources) => dispatch(tlActions.setSources(sources)),
    fetchComments: (args) => dispatch(tlActions.setIsFetching(true))
      .then(() => dispatch(fetchComments(defaults(args)({
        since: new Date(args.since).toISOString(),
        until: new Date(args.until).toISOString()
      }))))
      .then(() => dispatch(tlActions.setIsFetching(false))),
  }
);

const mergeProps = (stateProps, dispatchProps, ownProps) => reduce(defaults, {})([
  ownProps,
  stateProps,
  dispatchProps,
  {
    onSelectTagSet: (id) => dispatchProps.setTagSets([stateProps.allTagSets[id]]),
    onSelectSource: (id) => dispatchProps.setSources([stateProps.allSources[id]]),
    onFetch: (args = {}) => dispatchProps.fetchComments(defaults(stateProps)(args)),
  }
]);

export default connect(mapStateToProps, mapDispatchToProps, mergeProps)(TimelineControls);