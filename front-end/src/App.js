import React, { Component } from 'react';
import CardCreation from './CardCreation';
import CardListing from './CardListing.js';
import Home from './Home.js';

import PlayerListing from './PlayerListing';
import PlayerCreation from './PlayerCreation'
import PlayerPage from './PlayerPage';


class App extends Component {
  render() {
    return (
      <div>
        <CardCreation></CardCreation>
        <CardListing></CardListing>
        <PlayerPage></PlayerPage>
        <PlayerCreation></PlayerCreation>
        <PlayerListing></PlayerListing>
        <Home></Home>
      </div>

    );
  }
}

export default App;
