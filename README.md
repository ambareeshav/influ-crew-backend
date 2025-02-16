# Multi Agentic system for Analyzing Influencers

This is a sophisticated Node.js backend designed to streamline the process of identifying and analyzing potential YouTube collaborators for your company. By inputting a keyword, the system searches YouTube for relevant videos and gathers comprehensive data, including likes, views, comment counts, transcripts, video length, sponsors, description links, and social links. This data is then analyzed against your company's profile to determine the suitability of potential collaborations. Additionally, the system can generate a business profile by researching your company's name.

## Key Features

- **YouTube Data Extraction**: Scrapes detailed information from YouTube videos based on specified keywords.
- **Company Profile Analysis**: Evaluates potential collaborators by comparing extracted data with your company's profile.
- **Business Profile Generation**: Creates a comprehensive business profile by researching the provided company name.

## Technologies Used

- **CrewAI**: Serves as the agentic framework, orchestrating autonomous AI agents to perform specific tasks collaboratively. 
- **Composio**: Provides a suite of tools that integrate with AI agents, enabling them to perform actions such as data extraction and analysis. 
- **Apify**: Utilized for web scraping, allowing the extraction of data from YouTube and other relevant sources.
- **OpenAI Assistants**: Employed for data analysis, leveraging advanced AI capabilities to assess and interpret the gathered information.

## Clone the repo
```
git clone https://github.com/ambareeshav/influ-crew-backend
```
## Create virtual environment
```
py -m venv venv
./venv/scripts/activate
```
## Install required libraries
```
pip install -r requirements.txt --no-deps
```
## Start the Server
```
uvicorn main:app --reload
```
## Access docs at - http://127.0.0.1:8000/docs
