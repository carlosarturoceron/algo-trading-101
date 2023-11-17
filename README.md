# Algo Trading 101: Crypto Trading with Simple Moving Averages on Phemex 🚀📈

Welcome to Algo Trading 101, your gateway to the exciting world of algorithmic trading in the cryptocurrency market! 🌐💸 In this repository, we'll guide you through the process of creating a Simple Moving Average (SMA) trading bot that operates on the Phemex exchange.

## Table of Contents 🗂️

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Running the Bot](#running-the-bot)
6. [Results and Performance](#results-and-performance)
7. [Contributing](#contributing)
8. [License](#license)

## Introduction 🚀

Algorithmic trading, or algo trading, has become increasingly popular in the cryptocurrency space. This repository is designed to help you understand the basics of algorithmic trading and guide you in implementing a simple yet effective trading bot using Simple Moving Averages.

## Getting Started 🚀

To get started with algo trading on Phemex, make sure you have the following:

- A Phemex account: [Sign up on Phemex](https://phemex.com/register?referralCode=YOUR_REFERRAL_CODE) 🌐
- Basic knowledge of Python programming 🐍
- Git installed on your machine 🖥️

## Installation ⚙️

Clone this repository to your local machine using:

```bash
git clone https://github.com/carlosarturoceron/algo-trading-101.git
cd algo-trading-101
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Configuration ⚙️

Add a `.env` file. Specify your Phemex API key and secret, choose your trading pair, and set your desired SMA parameters.

```python
# Phemex API Key and Secret
API_KEY = "YOUR_API_KEY"
API_SECRET = "YOUR_API_SECRET"
```
Configure the market you want to trade in line #31 in sma_bot.py for running the bot or in the notebook. By default it will trade Ethereum.

```python
# Set Parameters
symbol = 'ETHUSD' #symbol to trade
pos_size = 10 # position size
params = {'timeInForce':'PostOnly'}
target = 25
```

## Running the Bot 🤖

Execute the trading bot using the following command:

```bash
python sma_bot.py
```

Or deploy to a cloud server provider to schedule the bot to run 24/7

Sit back, relax, and watch your bot execute trades based on the Simple Moving Average strategy. 🍿📊

## Results and Performance 📈

We encourage users to share their results and experiences with the community. Feel free to open issues, submit pull requests, or participate in discussions.

## Contributing 🤝

We welcome contributions! If you have improvements or new features to suggest, please open an issue or submit a pull request.

## License 📜

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Happy trading! 🚀📈💰

*Disclaimer: Trading cryptocurrencies involves risk, and this repository is for educational purposes only. The creators and contributors are not responsible for any financial losses incurred.*