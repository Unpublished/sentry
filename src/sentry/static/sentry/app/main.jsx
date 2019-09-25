import {hot} from 'react-hot-loader/root'; // This needs to come before react
import React from 'react';
import {Router, browserHistory} from 'react-router';
import {useBasename} from 'history';

import routes from 'app/routes';
import {loadPreferencesState} from 'app/actionCreators/preferences';

class Main extends React.Component {
  componentDidMount() {
    loadPreferencesState();
  }

  render() {
    return (
      <Router history={useBasename(() => browserHistory)({basename: '/sentry'})}>
        {routes()}
      </Router>
    );
  }
}

export default hot(Main);
