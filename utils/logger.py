import os
from datetime import datetime
from msal import ConfidentialClientApplication
import requests

# Replace these with your actual Azure credentials
CLIENT_ID = "98f784a9-5e71-4e57-9543-a83bc1fec732"
TENANT_ID = "0b89b039-029d-4a76-a420-14aa6287d930"
CLIENT_SECRET = "hmA8Q~g5ZshIHFzpAoZv.HlALN6tOx199wpSFciU"

# Microsoft Graph API scope
SCOPES = ["https://graph.microsoft.com/.default"]

def get_access_token():
    """
    Authenticate and return access token using MSAL
    """
    app = ConfidentialClientApplication(
        client_id=CLIENT_ID,
        authority=f"https://login.microsoftonline.com/{TENANT_ID}",
        client_credential=CLIENT_SECRET
    )
    result = app.acquire_token_for_client(scopes=SCOPES)

    if "access_token" in result:
        return result["access_token"]
    else:
        raise Exception("Failed to acquire token: " + str(result.get("error_description")))

def upload_to_onedrive(file_path, file_name):
    """
    Uploads the given file to the user's OneDrive root folder in a folder called 'StreamlitLogs'
    """
    access_token = get_access_token()

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "text/plain"
    }

    # Create a folder called StreamlitLogs if it doesn't exist
    create_folder_url = "https://graph.microsoft.com/v1.0/me/drive/root/children"
    folder_data = {
        "name": "StreamlitLogs",
        "folder": {},
        "@microsoft.graph.conflictBehavior": "rename"
    }
    requests.post(create_folder_url, headers={"Authorization": f"Bearer {access_token}"}, json=folder_data)

    # Upload the file into the folder
    upload_url = f"https://graph.microsoft.com/v1.0/me/drive/root:/StreamlitLogs/{file_name}:/content"

    with open(file_path, "rb") as f:
        response = requests.put(upload_url, headers=headers, data=f)

    if response.status_code in [200, 201]:
        print("✅ File uploaded successfully to OneDrive.")
    else:
        print(f"❌ Failed to upload file: {response.status_code} - {response.text}")

def save_output_to_file(title: str, chapo: str, article_text: str, transitions: list[str]):
    """
    Saves article content to local .txt file and uploads it to OneDrive
    """
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"generated_output_{timestamp}.txt"
    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"Titre: {title}\n\n")
        f.write(f"Chapeau: {chapo}\n\n")
        f.write("Article:\n")
        f.write(article_text.strip() + "\n\n")
        f.write("Transitions générées:\n")
        for i, t in enumerate(transitions, 1):
            f.write(f"{i}. {t}\n")

    # ✅ Upload to OneDrive
    upload_to_onedrive(filepath, filename)

    return filepath
