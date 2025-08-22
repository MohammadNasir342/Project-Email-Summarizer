#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import requests
import json
import re
from bs4 import BeautifulSoup
from msal import PublicClientApplication
from openai import OpenAI

def trim_email_after_reply_div(html: str) -> str:
                # Common HTML markers inserted by email clients for quoted replies
                reply_markers = [
                    '<div class="gmail_quote"',
                    '<div class="gmail_quote gmail_quote_container"',
                    '<div class="OutlookMessageHeader"',
                    '<div type="cite"',
                    '<div id="yahoo_quoted"',
                    '<div id="reply-intro"',
                    '<blockquote',
                    '<hr',                                      # Often used to separate original message
                    '<div class="moz-cite-prefix"',             # Thunderbird (Mozilla)
                    '<div class="WordSection1"',                # Outlook desktop (Rich Text)
                    '<div class="ecxWordSection1"',             # Older Outlook HTML
                    '<div id="divRplyFwdMsg"',                 # Microsoft Outlook Web
                    '<div class="MsoNormal"',                  # Outlook desktop (sometimes for reply)
                    '<table class="cfh_iframe_holder"',         # Custom client like Zoho
                    '<div class="gmail_attr"',                  # Gmail on mobile
                    '<div class="gmail_extra"',                 # Gmail desktop extras
                    '<div class="yahoo_quoted"',                # Yahoo sometimes uses this variant
                    '<div class="a3s aiL "'                     # Gmail raw quoted text
                ]

                # Find the first position of any marker
                first_pos = len(html)
                for marker in reply_markers:
                    pos = html.lower().find(marker.lower())
                    if pos != -1 and pos < first_pos:
                        first_pos = pos

                # Truncate HTML at the first reply marker (if any found)
                truncated_html = html[:first_pos] if first_pos != len(html) else html

                # Convert to readable text
                soup = BeautifulSoup(truncated_html, "html.parser")
                return soup.get_text(separator="\n").strip()
            
def process_emails(client_id, tenant_id,openai_key, category_name):
    CLIENT_ID = client_id
    TENANT_ID = tenant_id
    AUTHORITY = f"https://login.microsoftonline.com/{tenant_id}"
    SCOPES = ["Mail.Read"]
    CATEGORY_NAME = category_name

    # List to store detailed email info for later use
    stored_emails = []

    # Initialize MSAL public client app and acquire token interactively
    app = PublicClientApplication(CLIENT_ID, authority=AUTHORITY)
    result = app.acquire_token_interactive(scopes=SCOPES)
    
    if "access_token" not in result:
        raise Exception(f"Authentication error: access token not found")
    
    headers = {'Authorization': 'Bearer ' + result['access_token']}

    emails = []
    next_url = (f"https://graph.microsoft.com/v1.0/me/messages"
                f"?$filter=categories/any(c:c eq '{CATEGORY_NAME}')"
                f"&$select=id,subject,from")

    # Fetch all emails with the specified category (handle pagination)
    while next_url:
        response = requests.get(next_url, headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"Error fetching messages: {response.text}")
            
        data = response.json()
        emails.extend(data.get('value', []))
        next_url = data.get('@odata.nextLink')

    # Fetch full email content
    for email in emails:
        message_id = email['id']
        full_url = f"https://graph.microsoft.com/v1.0/me/messages/{message_id}"
        full_response = requests.get(full_url, headers=headers)
        
        if full_response.status_code != 200:
            raise Exception(f"Error fetching full message {message_id}: {full_response.text}")
            
        full_message = full_response.json()

        subject = full_message.get('subject', 'No Subject')
        sender = full_message.get('from', {}).get('emailAddress', {}).get('name', 'Unknown')
        body = full_message.get('body', {}).get('content', '')
        content_type = full_message.get('body', {}).get('contentType', '')

        current_msg = trim_email_after_reply_div(body)

        # Store email details in a dict
        stored_emails.append({
            "Category": CATEGORY_NAME,
            "id": message_id,
            "subject": subject,
            "time": full_message.get('receivedDateTime', 'No Time'),
            "senderName": full_message.get('from', {}).get('emailAddress', {}).get('name', 'Unknown'),
            "senderAddress": full_message.get('from', {}).get('emailAddress', {}).get('address', 'Unknown'),
            "ToName": [recipient.get("emailAddress", {}).get("name") for recipient in full_message.get('toRecipients', {})],
            "ToAddress": [recipient.get("emailAddress", {}).get("address") for recipient in full_message.get('toRecipients', {})],
            "body_text": current_msg,
        })

    client = OpenAI(api_key=openai_key)
    json_data = json.dumps(stored_emails)

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": f"Analyze the following emails:\n{json_data}"}
        ]
    )
    
    summary = response.choices[0].message.content.strip()
    
    
    return f"✅ Retrieved {len(stored_emails)} emails from '{category_name}'\n\n🧠 OpenAI Summary:\n{summary}"

