import React, { Component } from 'react';
import CardCreation from './CardCreation';
import CardListing from './CardListing.js';
import Home from './Home.js';
import {
  BrowserRouter as Router,
  Switch,
  Route,
  Link
} from "react-router-dom";
import PlayerListing from './PlayerListing';
import PlayerCreation from './PlayerCreation'


class App extends Component {
  render() {
    return (
      <Router>
        <Switch>
          <Route path="/cards">
            <CardCreation></CardCreation>
            <CardListing></CardListing>
            <Link to="/">Home</Link>
          </Route>
          <Route path="/players">
            <PlayerCreation></PlayerCreation>
            <PlayerListing></PlayerListing>
            <Link to="/">Home</Link>
          </Route>

          <Route path="/">
            <Home></Home>
          </Route>
        </Switch>
      </Router>
    );
  }
}

export default App;
