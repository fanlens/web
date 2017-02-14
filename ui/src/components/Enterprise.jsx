import _ from "lodash";
import React from "react";
import Paper from "material-ui/Paper";
import {Card, CardActions, CardHeader, CardMedia, CardTitle, CardText} from "material-ui/Card";
import TextField from "material-ui/TextField";
import RaisedButton from "material-ui/RaisedButton";
import Endless from "./Endless.jsx";
import "./Enterprise.css";

const Offer = ({head, tagline, features, theme, children}) => (
  <Card className="offer">
    <CardHeader
      titleStyle={{color: 'white', textShadow: 'black 0px 0px 2px'}}
      className={theme + " darker offer-header"}
      title={tagline}/>
    <CardTitle
      titleStyle={{color: 'white', textShadow: 'black 0px 0px 2px'}}
      className={theme + " lighter offer-title"}
      title={head}/>
    <CardText>
      <ul className="features">
        {_.map(features,
          (feature, idx) => <li key={idx}>{feature}</li>)
        }
      </ul>
      {children}
    </CardText>
  </Card>
);

const offers = [
  {
    head: "Greetings",
    tagline: "The only limit is yourself",
    features: [
      "here",
      "at",
      "zombocom"
    ],
    theme: 'theme-green'
  },
  {
    head: "Enterprise",
    tagline: "The infinite is unkown",
    features: [
      "here",
      "at",
      "zombocom"
    ],
    theme: 'theme-blue'
  },
  {
    head: "Reseller",
    tagline: "The infinite is unkown",
    features: [
      "here",
      "at",
      "zombocom"
    ],
    theme: 'theme-red'
  },
  {
    head: "Special Forces",
    tagline: "The infinite is unkown",
    features: [
      "here",
      "at",
      "zombocom"
    ],
    theme: 'theme-violet'
  }];

const findOffer = (frag) => _.findIndex(offers, {head: frag.substring(1)});

const OffersList = ({initialIndex, onChangeIndex}) => (
  <div id="offers-container" className="row end-sm center-xs">
    <div className="spacer col-lg-5 col-xs-1"></div>
    <div id="offers" className="col-lg-6 col-xs-10">
      <Endless
        tight={true}
        theme={'light'}
        initialIndex={initialIndex}
        onChangeIndex={onChangeIndex}>
        {_.map(offers, (offer, idx) => <Offer key={idx} {...offer}/>)}
      </Endless>
    </div>
    <div className="spacer col-lg-1 col-xs-1"></div>
  </div>
);

const Signup = ({theme}) => (
  <div id="signup" className="row end-lg middle-xs center-xs">
    <div className="spacer col-lg-5 col-xs-1"/>
    <Paper className="signup-fields col-lg-6 col-xs-10">
      <div className="row middle-xs center-xs">
        <div className="col-sm col-xs-12">
          <TextField
            hintText="jane@example.com"
            className={theme + " darker no-bg"}
            floatingLabelText="Enter your Email"
            fullWidth={true}
          />
        </div>
        <div className="col-sm-3 col-xs-12">
          <RaisedButton
            label="Enquire"
            className={theme + " darker"}
            primary={true}
            fullWidth={true}
          />
        </div>
      </div>
    </Paper>
    <div className="spacer col-lg-1 col-xs-1"/>
  </div>
);

const Team = () => (
  <div>
    <div id="team-bg"/>
    <div id="team"/>
  </div>
);

class Enterprise extends React.Component {
  render() {
    const frag = this.props.location.hash;
    const offerIndex = Math.max(findOffer(frag), 0);
    return (
      <main id="legal" style={{display: 'flex', flexDirection: 'column', flex: '1 1 auto'}}>
        <Team/>
        <OffersList
          initialIndex={offerIndex}
          onChangeIndex={(idx) => this.props.router.replace({pathname: this.props.location.pathname, hash: '#'+offers[idx].head})}/>
          />
        <Signup theme={offers[offerIndex].theme}/>
      </main>
    );
  }
}

export default Enterprise;
