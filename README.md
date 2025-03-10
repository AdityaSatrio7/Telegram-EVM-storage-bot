How the Bot Works:

1. When a user starts the bot with /start, it welcomes them and asks for their EVM wallet address
2. The user sends their wallet address
3. The bot validates the address using both regex and Web3 validation
4. If valid, the bot stores:
  Telegram user ID,
  Telegram username (if available),
  Wallet address,
  Registration timestamp

5. The bot confirms successful registration to the user
