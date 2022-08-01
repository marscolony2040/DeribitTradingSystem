import React from 'react';


export default class DataTable extends React.Component {

  fetchData(Ticker) {
    const head = []
    const tails = []
    Object.keys(Ticker).map((ii, jj) => {
      head.push(<td style={{width: '190px'}}>
                    {ii}
                </td>
                );
      tails.push(<td style={{width: '190px'}}>
                    {Ticker[ii]}
                 </td>

                 );
    });
    return {'heads': head, 'tails': tails}
  }

  render() {

    const { Ticker, Metrics } = this.props.state;

    const trade_data = this.fetchData(Ticker);
    const metric_data = this.fetchData(Metrics);
    const trade_style = {width: '100%', color: 'limegreen', fontSize: 19};

    return(
      <div>
        <table style={trade_style}>
        <center>
          <tr>
            {trade_data['heads']}
          </tr>
          <tr>
            {trade_data['tails']}
          </tr>
          <tr>
          </tr>
          <tr>
            {metric_data['heads']}
          </tr>
          <tr>
            {metric_data['tails']}
          </tr>
        </center>
        </table>
      </div>
    );
  }
}
