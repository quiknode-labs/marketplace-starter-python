This is a sample QuickNode Marketplace application built on top of Flask.

It implements the 4 routes that a partner needs to [integrate with Marketplace](https://www.notion.so/quicknode/Marketplace-Integration-Overview-f272bbbfac364cbdae70566984de77bf).

# Installation

To install and run the application locally:

1. Clone the repository.
2. Create a virtual environment: `python -m venv venv`.
3. Activate the virtual environment: `source venv/bin/activate`.
4. Install the required packages: `pip install -r requirements.txt`.
5. Copy `.env.example` to `.env` file and fill in `DB_URL`, `AUTH_USERNAME`, and `AUTH_PASSWORD` with the appropiate values.
6. Run the application: `flask run`.

# Routes

The application has 4 different routes:

- `POST /provision`
- `PUT /update`
- `DELETE /deactivate`
- `DELETE /deprovision`

It uses postgres to store/update provisioned endpoints.
