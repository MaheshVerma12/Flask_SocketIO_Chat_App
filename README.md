# Code with Mahesh Chat

## Description

Code with Mahesh Chat is a real-time chat application built using Flask and Socket.IO. It allows users to join different chat rooms and communicate with each other in real-time. The application is designed to be easy to use and scalable, with features like private messaging and an online user list.

## Features

- Real-time chat
- Multiple chat rooms
- Private messaging
- Online user list

## Installation

1. Clone the repository
2. Install the dependencies using pip:
    ```
    pip install -r requirements.txt
    ```
3. Set up the environment variables:
    - `SECRET_KEY`: A secret key for your application. You can generate one using `os.urandom(24)`
    - `FLASK_DEBUG`: Set to `True` for debug mode, `False` otherwise.
    - `CORS_ORIGINS`: A comma-separated list of allowed origins for CORS.

## Usage

1. Run the application:
    ```
    flask run
    ```
2. Open your browser and go to `http://localhost:5000`
3. Enter a username and select a chat room to join.

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request. When submitting a pull request, please make sure to include a clear description of the changes you made and any relevant tests.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
