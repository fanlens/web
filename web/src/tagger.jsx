import 'babel-polyfill'
import React from 'react';
import {render} from 'react-dom';
import {createStore, combineReducers, applyMiddleware} from 'redux'
import {Provider} from 'react-redux'
import createLogger from 'redux-logger'
import thunkMiddleware from 'redux-thunk'

import {initApp} from './actions/TaggerActions'
import alerts from './reducers/alerts'
import tagger from './reducers/tagger'

import TaggerApp from './components/TaggerApp.jsx'
import AlertsApp from './components/AlertsApp.jsx'

const taggerReducers = combineReducers({
  alerts,
  tagger
});

const store = createStore(
  taggerReducers,
  applyMiddleware(
    thunkMiddleware,
    createLogger()
  )
)
render(
  <Provider store={store}>
    <TaggerApp />
  </Provider>,
  document.getElementById('app')
);
render(
  <Provider store={store}>
    <AlertsApp />
  </Provider>,
  document.getElementById('alerts')
);

store.dispatch(initApp())
