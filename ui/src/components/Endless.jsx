import React from "react";
import SwipeableViews from "react-swipeable-views";
import {bindKeyboard, virtualize} from "react-swipeable-views-utils";
import IconButton from "material-ui/IconButton";
import SVGNavPrev from "material-ui/svg-icons/image/navigate-before";
import SVGNavNext from "material-ui/svg-icons/image/navigate-next";

const randomInt = (min, max) => {
  min = Math.ceil(min);
  max = Math.floor(max);
  return Math.floor(Math.random() * (max - min)) + min;
};

const VirtualizeSwipeableViews = bindKeyboard(virtualize(SwipeableViews));


const rgba = (amount) => `rgba(${new Array(3).fill(amount).join()}, 0.87)`;
const arrowColor = (theme) => rgba(theme === 'light' ? 255 : 0);

class Endless extends React.Component {
  state = {index: null, offset: randomInt(0, 100)};

  _indexMapper = (index) => {
    const offset = this.props.random ? this.state.offset : 0;
    const mod = (Math.abs(index) + offset) % this.props.children.length;
    if (index >= 0 || mod === 0) { // invert in neg direction to continue scrolling in appropriate direction
      return mod;
    } else {
      return this.props.children.length - mod;
    }
  };
  _onChangeIndex = (index) => {
    this.setState({index});
    this.props.onChangeIndex && this.props.onChangeIndex(this._indexMapper(index));
  };
  _next = () => this._onChangeIndex(this.state.index + 1, this.state.index);
  _prev = () => this._onChangeIndex(this.state.index - 1, this.state.index);

  slideRenderer = ({key, index}) => (
    <div key={key}>
      {this.props.children[this._indexMapper(index)]}
    </div>
  );

  componentWillMount() {
    if (this.state.index === null) {
      this.setState({index: this.props.initialIndex || 0});
    }
  }

  render() {
    return (
      <div className="row center-xs middle-xs">
        <div className={`col-xs-1 ${this.props.tight ? 'end' : 'start'}-xs`} style={{margin: 0, padding: 0}}>
          <IconButton
            style={{width: 'initial', height: 'initial', margin: 0, padding: 0}}
            onTouchTap={this._prev}>
            <SVGNavPrev color={arrowColor(this.props.theme)}/>
          </IconButton>
        </div>
        <div className="col-xs-10 col-xs-10">
          <VirtualizeSwipeableViews
            index={this.state.index}
            onChangeIndex={this._onChangeIndex}
            slideRenderer={this.slideRenderer}/>
        </div>
        <div className={`col-xs-1 ${this.props.tight ? 'start' : 'end'}-xs`} style={{margin: 0, padding: 0}}>
          <IconButton
            style={{width: 'initial', height: 'initial', margin: 0, padding: 0}}
            onTouchTap={this._next}>
            <SVGNavNext color={arrowColor(this.props.theme)}/>
          </IconButton>
        </div>
      </div>
    );
  }
}

export default Endless;
