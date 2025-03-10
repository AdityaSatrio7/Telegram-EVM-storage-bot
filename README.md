How the Bot Works

When a user starts the bot with /start, it welcomes them and asks for their EVM wallet address
The user sends their wallet address
The bot validates the address using both regex and Web3 validation
If valid, the bot stores:

Telegram user ID
Telegram username (if available)
Wallet address
Registration timestamp


The bot confirms successful registration to the user
