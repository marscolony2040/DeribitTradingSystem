import React from 'react';
import Plot from 'react-plotly.js';


export default class OrderBook extends React.Component {

  plotBook(Book) {
    const bids = []
    const asks = []
    if(Book.length > 0){
      bids.push(
        <Plot
          data={[{
            x: Book[0],
            y: Book[3],
            type: 'bar',
            name: 'Bids',
            marker: {
              color: 'red'
            }
          }]}
          layout={{
            title: {
              text: "Bids",
              font: {
                color: "limegreen"
              }
            },
            paper_bgcolor: 'black',
            plot_bgcolor: 'black',
            xaxis: {
                tickmode: 'array',
                tickvals: Book[0],
                ticktext: Book[1],
                tickfont: {
                  color: "limegreen"
                }
            },
            yaxis: {
                tickfont: {
                  color: 'limegreen'
                }
            }
          }}
        />

      );

      asks.push(
        <Plot
          data={[{
            x: Book[0],
            y: Book[4],
            type: 'bar',
            name: 'Bids',
            marker: {
              color: 'cyan'
            }
          }]}
          layout={{
            title: {
              text: "Asks",
              font: {
                color: "limegreen"
              }
            },
            paper_bgcolor: 'black',
            plot_bgcolor: 'black',
            xaxis: {
                tickmode: 'array',
                tickvals: Book[0],
                ticktext: Book[2],
                tickfont: {
                  color: "limegreen"
                }
            },
            yaxis: {
                tickfont: {
                  color: 'limegreen'
                }
            }
          }}
        />
      );
    }
    return [bids, asks]
  }

  render() {

    const { Book } = this.props.state;

    const bookPlots = this.plotBook(Book);

    return (
      <div>
        { bookPlots }
      </div>
    );
  }
}
