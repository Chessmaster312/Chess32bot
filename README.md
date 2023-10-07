# Chess32bot

Chess32bot is a multi-user Telegram bot for playing chess based on a web application. It allows users to play chess with random opponents or friends. In the future, the project plans to add subscription functionality, track statistics (game history, wins, losses, Elo rating) and analyze games.

## Content
1. [Project structure](#project-structure)
2. [Requirements](#requirements)
3. [Installation](#installation)
4. [Usage](#usage)
5. [Possible errors](#possible-errors)
6. [License](#license)

### Project structure

The project is organized into the following directories and files:

- `bootstrap.py `: The entry point to the project.
- `build/`: Contains the HTML file of the web application.
- `config.py `: Project configuration file.
- `config.yaml': Configuration file in YAML format.
- `db_api/`: Directory for modules associated with the database.
- `engine/`: Contains modules and classes for game logic and sessions.
- `handlers/`: Telegram bot handlers.
- `websocket/`: Modules to support WebSocket connections.
- `states/`: Bot state management modules.
- `utils.py `: Utilitarian functions.
- `main.py `: The entry point to the project.
- `requirements.txt `: List of project dependencies.
- `router.py `: Registration of Telegram bot handlers.
- `routes.py `: Routes to access the web application.
- `settings.py `: Project settings.

### Requirements

To run the Chess32bot project, you will need the following:

- Python 3.10
- PostgreSQL Database Management System
- HTTPS-enabled web server (for example, Apache)

### Installation

1. Install Python 3.10, PostgreSQL and Git on your server.
2. Clone the repository:
   ``git clone https://github.com/your_username/chess32bot.git ``
3. Create a virtual environment:
   ```python -m venv venv```
4. Activate the virtual environment:
``source venv/bin/activate``
5. Install project dependencies:
   ```pip install -r requirements.txt```
6. Configure your PostgreSQL database and update the `config.yaml` file with the necessary credentials for the database.
7. Configure your web server (for example, Apache) to support HTTPS. Here is an example of Apache Virtual host configuration for HTTPS:
     ```
     <VirtualHost *:443>
        ServerName your_site
        ProxyPreserveHost On
        ProxyPass /wss/ ws://localhost:80/
        ProxyPassReverse /wss/ ws://localhost:80/
        ProxyPass /.well-known/acme-challenge !
        ProxyPass / http://localhost:8080/
        ProxyPassReverse / http://localhost:8080/
        SSLEngine on
        SSLCertificateFile /etc/ssl/your_crt.crt
        SSLCertificateKeyFile /etc/ssl/rsa_key
        SSLCertificateChainFile /etc/ssl/your_ca-bundle.ca-bundle
        ServerAdmin webmaster@localhost
        DocumentRoot /var/www/html
        ErrorLog ${APACHE_LOG_DIR}/error.log
       CustomLog ${APACHE_LOG_DIR}/access.log combined
   </VirtualHost>

### Usage

To use Chess32bot, you need to follow these steps:

1. **Launch Telegram and find the bot by its name:** `@Chess32bot`.

2. **Start a dialogue with the bot by sending the /start command.** The bot welcomes you and provides several options for action.

3. **Choose one of the actions:**

   - **Start the game with a random opponent:** By selecting this option, you will be immediately matched with another random player who also wants to play chess. This is a great way to test your skills and fight against different opponents.

   - **Invite a friend to play chess:** If you want to play with your friend, you will need his Telegram name or login. After entering information about your friend, the bot will create a game between the two of you, and you can play a game together.

4. **Follow the instructions of the bot to start the game.** Depending on the selected option, the bot will guide you in the process of creating and playing chess. You will be able to make moves and interact with the chess board directly.

5. **Open the web application:** After the game starts, the bot will provide you with a button that you can click to open the web application for chess. The web application provides an interactive whiteboard and additional features for the convenience of the game.

6. **Additional functions are planned:** In the future, we plan to expand the functionality of the bot by adding additional options, such as subscriptions to access advanced features, game statistics, including history and Elo rating, and batch analysis to improve the game strategy.

### Possible errors

When using Chess32bot and the web application, the following potential errors may occur:

1. **Error connecting to the Telegram server:** If you have problems connecting to the Telegram server, make sure that your server has Internet access and does not block the connection to Telegram. Check the proxy settings if they are used.

2. **Problems with the PostgreSQL database:** If there are problems with the PostgreSQL database, make sure that you have correctly configured the `config.yaml` file with the credentials for the database. Check that PostgreSQL is running and available for your server.

3. **Error when configuring the web server:** Configuring a web server (for example, Apache) may cause difficulties. Make sure that you have configured the virtual host and SSL certificates correctly. Check the web server configuration files for typos and syntax errors.

4. **Problems with WebSocket connection:** If the WebSocket connection is not established or does not work correctly, make sure that the web server is configured correctly to support WebSocket. Check that the ports and paths are configured correctly in the web server and your application.

### License

Chess32bot is distributed under the open license [MIT]. This means that you have the right to freely use, modify and distribute the code of this project in accordance with the terms of the license.

To read the full text of the license, read the [LICENSE](LICENSE) file in the root directory of the project.

We welcome your contributions and cooperation! If you have suggestions, fixes or improvements for this project, feel free to create merge Requests (Pull Requests) or report issues on GitHub.

It is important to remember to comply with the terms of the license and respect copyright when using this project.
