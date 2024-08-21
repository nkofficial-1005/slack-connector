# Slack Connector App

This Flask application enables integration with Slack to perform various actions such as sending messages, uploading files, and managing channel content. Follow the setup instructions below to get started.

## Prerequisites

- Python 3.x
- Flask
- Slack account
- App URL

## Setup Instructions

1. **Create a Slack App**:
   - Navigate to [Slack API](https://api.slack.com/apps) and create a new app.
   - Add the app to your Slack workspace.
   - Navigate to "OAuth & Permissions" to add required scopes such as `chat:write`, `files:read`, and others as needed.
   - Set the redirect URI to the secure URL provided by your organization, where you want Slack to send the OAuth code.

2. **Configure Environment**:
   - Clone this repository or copy the code into a new Python file.
   - Install the required Python packages:
     ```sh
     pip install Flask slack_sdk
     ```
   - Set environment variables for your Flask secret key.
   - Update `redirect_uri` in the Flask app and the Slack app settings to match the secure HTTPS URL provided by the organization.

3. **Run the Application**:
   - Ensure your server is set up to run over HTTPS with the provided XYZ organization's URL.
   - Run the Flask app:
     ```sh
     python app.py
     ```

## Usage

Once the application is running, follow these steps:

1. Navigate to the provided HTTPS URL in your web browser.
2. Enter your Slack app credentials (Client ID and Client Secret).
3. Authenticate with Slack; this will redirect you to Slack's OAuth page.
4. Once authenticated, you will be redirected back to the app to perform actions like sending messages or uploading files.

## Features

- **Send Messages**: Send messages directly to the channels where the app is added.
- **Upload Files**: Upload files to the channels.
- **List Channels**: View a list of all channels (public and private) available to the app.
- **Update and Delete Messages**: Modify or remove existing messages.
- **Delete Files**: Remove files that were previously uploaded.

## Important Notes

- Ensure the HTTPS URL settings remain consistent across all configuration points.
- Keep your client secrets and tokens secure and never expose them in your codebase.

## Support

If you encounter any issues or have questions about the setup, feel free to ping me.
