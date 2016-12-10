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

const slideRenderer = ({children, offset}) => ({key, index}) => (
  <div key={key}>
    {children[(Math.abs(index) + offset) % children.length]}
  </div>
);

class Endless extends React.Component {
  state = {idx: 0, offset: randomInt(0, 100)};
  _onChangeIndex = (idx) => this.setState({idx});
  _next = () => this._onChangeIndex(this.state.idx + 1, this.state.idx);
  _prev = () => this._onChangeIndex(this.state.idx - 1, this.state.idx);

  render() {
    const renderer = slideRenderer({
      children: this.props.children,
      offset: this.state.offset
    });
    return (
      <div className="row middle-xs">
        <div className="col-xs-2 start-xs">
          <IconButton
            onTouchTap={this._prev}>
            <SVGNavPrev/>
          </IconButton>
        </div>
        <div className="col-xs-8">
          <VirtualizeSwipeableViews
            index={this.state.idx}
            onChangeIndex={this._onChangeIndex}
            slideRenderer={renderer}/>
        </div>
        <div className="col-xs-2 end-xs">
          <IconButton
            onTouchTap={this._next}>
            <SVGNavNext/>
          </IconButton>
        </div>
      </div>
    );
  }
}

export default Endless;
