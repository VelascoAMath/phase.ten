import React, { Component } from 'react';
import CardCreation from './CardCreation';
import CardListing from './CardListing.js';

class App extends Component {
  render() {
    return (
      <div>
        <CardCreation></CardCreation>
        <CardListing></CardListing>
      </div>
    );
  }
}

export default App;
