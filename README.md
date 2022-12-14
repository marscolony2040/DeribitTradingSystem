# DeribitTradingSystem :brain:

## Description :penguin:
An algorithmic trading system designed using a Python server and a React.js front-end which trades on the crypto-currency exchange Deribit. This system is not able to work as of now since Deribit does not allow US residents to trade on their exchange. Overall this was a fun project for me having been able to create a powerful asynchronus server which imports high speed websocket data, along with using sockets to send trade orders. The front end has a graphical interface showing live updates to the orderbook, along with showcasing metrics such as filled order volume on the home page. As I said before, this system does not work anymore, however, if you would like to add modifications to this system, feel free. I would like to see this project go far.

[update] This system still runs well as long as you have the correct python and React libraries; additionally you must not be a US resident in order to actually trade on Deribit. The strategy included ceased to work since prior to the beginning of 2020. I have kept updating it the past few years but have not made much profit. 

## Running Example :ice_cube:
```shell
python server & npm start
```
![alt](https://github.com/marscolony2040/DeribitTradingSystem/blob/main/images/Trader.gif)

## Installation (for Mac) :apple:
```shell
brew install node
node -v
npm -v
pip install websockets
pip install numpy
pip install pandas
```
