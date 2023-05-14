# SO Analytics API

This project is an API for indexing messages in Elasticsearch and saving the message data to a JSON file. It provides an endpoint `/messages` for creating events.

## Prerequisites

- Python 3.9
- Elasticsearch

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/notapixelstudio/analytics
    ```
2. Install the dependencies:

    ```bash
    pip install -r requirements.txt
    ```

## Configuration

Before running the application, make sure to configure the Elasticsearch connection and other environment variables. The following environment variables can be set:

- `ELASTIC_HOSTNAME`: Elasticsearch hostname (default: `https://localhost:9200`)
- `ELASTIC_USERNAME`: Elasticsearch username (default: `elastic`)
- `ELASTIC_PASSWORD`: Elasticsearch password (default: `changeme`)
- `TOKEN`: Secret token for authentication (default: `secret_token`)

## Usage

Run the following command to start the API server:

```bash
uvicorn main:app --reload

```

The API will be available at `http://localhost:8000`.

### Endpoint: POST /messages

This endpoint allows you to create an event by indexing a message in Elasticsearch and saving the message data to a JSON file.

**Request**

- Header:
  - Authorization: Basic authentication token (e.g., "Basic base64(username:password)")

- Body:
  - id (string): Event ID
  - version (string): Event version
  - event_name (string): Name of the event

**Response**

- Status: 200 OK
- Body: JSON object with a message indicating whether the message has been indexed successfully or if an error occurred.

**Example**

```bash
curl -X POST -H "Authorization: Basic base64(username:password)" -H "Content-Type: application/json" \
     -d '{"id": "godot_1", "version": "1.0", "event_name": "example_event"}' \
     http://localhost:8000/messages
```

## Logging

The application logs information using the logger named api_logger. By default, log messages are displayed on the console.

## License

This project is licensed under the MIT License.

## Development
The following make targets are available for development:

- `install-dev`: Install development dependencies.
- `setup-dev-env`: Set up the development environment, including pre-commit hooks and commit message validation.
- `clean`: Remove temporary files and directories generated during development.
- `bump`, `bump-minor`, `bump-major`, `bump-patch`: Bump the project version, generate changelog, create a git tag, and commit the changes.
- `docker-build`: Build a Docker image for the project.
- `local-run`: Run the project locally using uvicorn with environment variables from the .env file.

To execute a make target, run the following command:


    make <target>

For example, to install development dependencies, run make install-dev.

## Notes

- The application uses the pydantic library for data validation and modeling.
- IP address validation and anonymization functions are provided.
- The Elasticsearch index used is "starship_olympics_analytics".
- The application saves the event data to a JSON file in the "data" directory with the name <event_id>.json.

Feel free to modify and adapt this code to suit your specific needs.
