This is a Flask web application that runs 4 different routes.

# Installation

To install and run the application locally:

Clone the repository.
Create a virtual environment: `python -m venv venv`.
Activate the virtual environment: `source venv/bin/activate`.
Install the required packages: `pip install -r requirements.txt`.
Run the application: `flask run`.

# Routes

The application has 4 different routes:

- `POST /provision`
- `PUT /update`
- `DELETE /deactivate`
- `DELETE /deprovision`

It uses postgres to store/update provisioned endpoints.
