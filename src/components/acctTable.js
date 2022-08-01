import React from 'react';


export default class AccountTable extends React.Component {

  fetchData(Acct) {
    const head = []
    const tails = []
    Object.keys(Acct).map((ii, jj) => {
      head.push(
        <td style={{width: '190px'}}>
          {ii}
        </td>
      );
      tails.push(
        <td style={{width: '190px'}}>
          {Acct[ii]}
        </td>
      );
    });
    return {'heads': head, 'tails': tails}
  }



  render() {

    const { Acct, Orders } = this.props.state;

    const trade_style = {width: '100%', color: 'limegreen', fontSize: 19};
    const trade_data = this.fetchData(Acct)
    const position_data = this.fetchData(Orders)

    return (
      <div style={{color: 'limegreen'}}>
          <table style={trade_style}>
            <center>
              <tr>
                {position_data['heads']}
              </tr>
              <tr>
                {position_data['tails']}
              </tr>
            </center>
          </table>
          <table style={trade_style}>
            <center>
              <tr>
                {trade_data['heads']}
              </tr>
              <tr>
                {trade_data['tails']}
              </tr>
            </center>
          </table>
      </div>
    );
  }
}
