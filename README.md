# Project-Email-Summarizer
A Python-based GUI tool to fetch categorized Outlook emails using Microsoft Graph API, analyze them using OpenAI GPT, and display clean results.

Features:
1. Interactive GUI (Tkinter)
2. Microsoft OAuth 2.0 login with MSAL
3. Category-based email filtering
4. Email Parcing
5. GPT integration for summarization or analysis

## Setup

1. Clone this repo
2. Create a virtual environment
3. Install dependencies
4. Create an Azure App Registration:
    Enable Microsoft Graph Mail.Read
    Note the Client ID and Tenant ID
5. Create a OpenAI account:
   Note the API Key
6. Run the app
