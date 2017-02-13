import _ from "lodash";
import React from "react";
import Paper from "material-ui/Paper";
import TextField from "material-ui/TextField";
import RaisedButton from "material-ui/RaisedButton";
import Endless from "./Endless.jsx";
import "./Enterprise.css";

const Offer = ({head, tagline, features, children}) => (
  <div className="offer">
    <h1 className="head">{head}</h1>
    <h2 className="tagline">{tagline}</h2>
    <ul className="features">
      {_.map(features,
        (feature, idx) => <li key={idx}>{feature}</li>)
      }
    </ul>
    <p className="content-area">{children}</p>
  </div>
);

const Offers = () => (
  <div id="offers-container" className="row end-sm center-xs">
    <div className="spacer col-sm-6 col-xs-1"></div>
    <Paper id="offers" className="col-sm-5 col-xs-10">
      <Endless>
        {_.map([
          {
            head: "Greetings",
            tagline: "The only limit is yourself",
            features: [
              "here",
              "at",
              "zombocom"
            ]
          },
          {
            head: "Enterprise",
            tagline: "The infinite is unkown",
            features: [
              "here",
              "at",
              "zombocom"
            ]
          },
          {
            head: "Reseller",
            tagline: "The infinite is unkown",
            features: [
              "here",
              "at",
              "zombocom"
            ]
          },
          {
            head: "Special Forces",
            tagline: "The infinite is unkown",
            features: [
              "here",
              "at",
              "zombocom"
            ]
          }], (offer, idx) => <Offer key={idx} {...offer}/>)}
      </Endless>
    </Paper>
    <div className="spacer col-sm-1 col-xs-1"></div>
  </div>
);

const Signup = () => (
  <div id="signup" className="row end-lg middle-xs center-xs">
    <div className="spacer col-lg-6 col-xs-1"/>
    <Paper className="signup-fields col-lg-5 col-xs-10">
      <div className="row middle-xs center-xs">
        <div className="col-sm col-xs-12">
          <TextField
            hintText="jane@example.com"
            floatingLabelText="Enter your Email"
            fullWidth={true}
          />
        </div>
        <div className="col-sm-3 col-xs-12">
          <RaisedButton
            label="Enquire"
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

const Enterprise = ({messages}) => (
  <main id="legal" style={{display: 'flex', flexDirection: 'column', flex: '1 1 auto'}}>
    <Team/>
    <Offers/>
    <Signup/>
  </main>
);

export default Enterprise;
