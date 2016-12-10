import injectTapEventPlugin from 'react-tap-event-plugin';
injectTapEventPlugin(); // will go away

import React from 'react';
import {render} from 'react-dom';
import {createStore, combineReducers, applyMiddleware} from 'redux'
import {Provider} from 'react-redux'
import createLogger from 'redux-logger'
import thunkMiddleware from 'redux-thunk'

import {initEev} from './actions/EevActions'
import {initActivities} from './actions/ActivitiesActions'
import alerts from './reducers/alerts'
import eev from './reducers/eev'
import activities from './reducers/activities'
import app from './reducers/app'

import App from './components/App.jsx'

import './app.css'

const store = createStore(
  combineReducers({
    alerts,
    eev,
    activities,
    app,
  }),
  applyMiddleware(
    thunkMiddleware,
    createLogger()
  )
);

render(
  <Provider store={store}>
    <App />
  </Provider>,
  document.getElementById('app')
);

store.dispatch((dispatch) => Promise.all([dispatch(initEev()), dispatch(initActivities())]));
