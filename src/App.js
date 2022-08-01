import React, { Component, Fragment } from 'react';

import title from './images/title.png';

import DataTable from './components/dataTable.js';
import OrderBook from './components/orderBook.js';
import AccountTable from './components/acctTable.js';

export default class App extends Component {

    constructor() {
        super();

        this.state = { Ticker: {},
                       Metrics: {},
                       Book: [],
                       Acct: {},
                       Orders: {},
                       endpoint: "ws://localhost:5678"
                     }
    }

    componentDidMount() {
        const { endpoint } = this.state;
        const socket = new WebSocket(endpoint);
        let resp = []
        socket.onmessage = evt => {
            resp = JSON.parse(evt.data);
            this.setState({ Ticker: resp['Ticker'],
                            Metrics: resp['Metrics'],
                            Book: resp["Book"],
                            Acct: resp["Account"],
                            Orders: resp["Orders"]
                          });
        }
    }

    render() {

        return (
            <Fragment>
                <center>
                  <img src={title} alt="title" style={{width: '80%', height: '6.66%'}} />
                  <DataTable state={this.state} />
                  <OrderBook state={this.state} />
                  <AccountTable state={this.state} />
                </center>
            </Fragment>
        );
    }
}
