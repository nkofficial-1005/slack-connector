from flask import Flask, request, redirect, url_for, session
import os
from werkzeug.utils import secure_filename
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.oauth import AuthorizeUrlGenerator

app = Flask(__name__)
FLASK_SECRET_KEY = ['your_secret_key']
app.secret_key = os.environ.get('FLASK_SECRET_KEY')

client_id = ""
client_secret = "" 
access_token = ""

UPLOAD_FOLDER = 'upload_folder' 
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        session['client_id'] = request.form['client_id']
        session['client_secret'] = request.form['client_secret']
        
        return redirect(url_for('pre_install'))
    return '''
        <h1>Enter your Slack App Credentials</h1>
        <form method="post">
            Client ID:<br>
            <input type="text" name="client_id"><br>
            Client Secret:<br>
            <input type="text" name="client_secret"><br><br>
            <input type="submit" value="Submit">
        </form>
    '''

@app.route('/pre_install', methods=['GET'])
def pre_install():
    # Retrieve client_id and client_secret from session
    client_id = session.get('client_id')
    client_secret = session.get('client_secret')

    if not client_id or not client_secret:
        return redirect(url_for('index'))
    state = ['your_state_value']
    session['state'] = state
    redirect_uri = "your_xyz_app_url/slack/callback"
    scopes = ['chat:write', 'chat:write.customize', 'files:read', 'files:write',
              'links.embed:write', 'links:read', 'links:write', 'channels:read',
              'remote_files:read', 'remote_files:share', 'remote_files:write', 'groups:read']
    url_generator = AuthorizeUrlGenerator(client_id=client_id, scopes=scopes, user_scopes=[])
    url = url_generator.generate(state, redirect_uri)
    
    return redirect(url)

@app.route('/slack/callback', methods=['POST','GET'])
def oauth_callback():

    if request.method == 'POST':
    # Store access token in session
        session['access_token'] = request.form['access_token'] 
        
    # Redirect the user to another endpoint in your application
        return redirect(url_for('list_channels'))
    return '''
        <h1>Enter your Bot or User Access Token</h1>
        <form method="post">
            Access Token:<br>
            <input type="text" name="access_token"><br>
            <input type="submit" value="Submit">
        </form>
        <a href="/list_channels?skip=true">Skip</a>
    '''

@app.route('/list_channels')
def list_channels():
    client = WebClient(token=session.get('access_token'))
    try:
        result = client.conversations_list(types="public_channel,private_channel")
        channels = result['channels']
        
        # Build a list of strings containing channel info to display in HTML
        channels_display = [f"{channel['name']} - ID: {channel['id']}" for channel in channels]
        channels_list_html = "<ul>" + "".join([f"<li>{channel}</li>" for channel in channels_display]) + "</ul>"
        
        # Add a form at the end of the list that submits to the send_message route
        proceed_form_html = '<form action="/send_message" method="get">' \
                            '<input type="submit" value="Proceed to Send a Message">' \
                            '</form>'
        
        # Combine the list and the form into one HTML response
        full_html_response = f"<h2>Channels List:</h2>{channels_list_html}{proceed_form_html}"
        
        return full_html_response
    except SlackApiError as e:
        print(f"Error fetching channels: {e}")
        return "Failed to retrieve the list of channels."

@app.route('/send_message', methods=['GET', 'POST'])
def send_message():
    if request.method == 'GET':
        return '''
            <h2>Send a message to Slack</h2>
            <form method="post">
                <label>Channel ID:<input type="text" name="channel_id"></label><br>
                <label>Message:<input type="text" name="message"></label><br>
                <input type="submit" value="Send Message">
            </form>
            <a href="/upload_file?skip=true">Skip</a>
        '''
    elif request.method == 'POST' or request.args.get('skip') == "true":
        channel_id = request.form.get('channel_id', 'default_channel_id')
        message = request.form.get('message', 'Hello from Flask!')
        try:
            client = WebClient(token=session['access_token'])
            response = client.chat_postMessage(channel=channel_id, text=message)
            
            # Extract the necessary data from the response
            ts = response['ts']  # Timestamp of the message
            sent_message = response['message']['text']  # The message text that was sent
            app_id = response['message']['bot_id']  # App/Bot ID that sent the message

            # Below is a placeholder print statement.
            print(f"Stored message data - Channel ID: {channel_id}, Timestamp: {ts}, Message: {sent_message}, App ID: {app_id}")
            
        except SlackApiError as e:
            print(f"Error sending message: {e}")
        return redirect(url_for('upload_file'))

@app.route('/upload_file', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'GET':
        return '''
            <h2>Upload a file to Slack</h2>
            <form method="post" enctype="multipart/form-data">
                <label>Channel ID:<input type="text" name="channel_id"></label><br>
                <label>File:<input type="file" name="file"></label><br>
                <input type="submit" value="Upload File">
            </form>
            <a href="/update_delete_message?skip=true">Skip</a>
        '''
    elif request.method == 'POST' or request.args.get('skip') == "true":
        channel_id = request.form.get('channel_id', 'default_channel_id')
        file_obj = request.files['file']
        if file_obj:
            filename = secure_filename(file_obj.filename)

            # Save the file to the upload folder
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file_obj.save(file_path)
            try:
                client = WebClient(token=session['access_token'])
                with open(file_path, 'rb') as file_content:
                    response = client.files_upload(
                        channels=channel_id,
                        file=file_content,
                        title=os.path.splitext(os.path.basename(file_path))[0],
                        filetype=os.path.splitext(file_path)[1][1:]
                    )

                # Assuming the upload was successful, retrieve the file ID
                file_id = response['file']['id']

                print(f"Stored file data - Channel ID: {channel_id}, File ID: {file_id}")

            except SlackApiError as e:
                print(f"Error uploading file: {e}")
        return redirect(url_for('update_delete_message'))

@app.route('/update_delete_message', methods=['GET', 'POST'])
def update_delete_message():
    if request.method == 'GET':
        return '''
            <h2>Update or Delete a Message in Slack</h2>
            <form action="/update_delete_message" method="post">
                <label>Channel ID:<input type="text" name="channel_id"></label><br>
                <label>Timestamp:<input type="text" name="timestamp"></label><br>
                <label>New Text:<input type="text" name="new_text"></label><br>
                <input type="submit" name="action" value="Update Message">
                <input type="submit" name="action" value="Delete Message">
            </form>
            <a href="/delete_file">Skip</a>
        '''
    elif request.method == 'POST':
        channel_id = request.form.get('channel_id')
        timestamp = request.form.get('timestamp')
        action = request.form.get('action')
        client = WebClient(token=session['access_token'])

        try:
            if action == 'Update Message':
                new_text = request.form.get('new_text', 'Updated message text!')
                response = client.chat_update(channel=channel_id, ts=timestamp, text=new_text)

                print(f"Updated Message Info - Channel ID: {channel_id}, TimeStamp: {timestamp}, Message: {new_text}")

            elif action == 'Delete Message':
                response = client.chat_delete(channel=channel_id, ts=timestamp)
        except SlackApiError as e:
            print(f"Error during {action.lower()}: {e}")

        return redirect(url_for('delete_file'))

@app.route('/delete_file', methods=['GET', 'POST'])
def delete_file():
    if request.method == 'GET':
        return '''
            <h2>Delete an Uploaded File from Slack</h2>
            <form method="post">
                <label>File ID:<input type="text" name="file_id"></label><br>
                <input type="submit" value="Delete File">
            </form>
            <a href="/completed">Skip</a>
        '''
    elif request.method == 'POST':
        file_id = request.form.get('file_id')
        client = WebClient(token=session['access_token'])

        try:
            delete_response = client.files_delete(file=file_id)
            print(f"File {file_id} deleted successfully.")
        except SlackApiError as e:
            print(f"Error deleting file: {e}")

        return redirect(url_for('completed'))

@app.route('/completed')
def completed():
    return "All operations completed. You can close this window or start over."

if __name__ == '__main__':
    app.run(debug=True, port=5000)
