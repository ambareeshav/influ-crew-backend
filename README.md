# Multi Agentic system for Analyzing Influencers

This is a python backend built with fastAPI designed to streamline the process of identifying and analyzing potential YouTube collaborators for your company. By inputting a keyword, the system searches YouTube for relevant videos and gathers comprehensive data, including likes, views, comment counts, transcripts, video length, sponsors, description links, and social links. This data is then analyzed against your company's profile to determine the suitability of potential collaborations. Additionally, the system can generate a business profile by researching your company's name.

## Key Features

- **YouTube Data Extraction**: Scrapes detailed information from YouTube videos based on specified keywords.
- **Company Profile Analysis**: Evaluates potential collaborators by comparing extracted data with your company's profile.
- **Business Profile Generation**: Creates a comprehensive business profile by researching the provided company name.
- **Automated Data Logging**: As each channel is evaluated and ranked, the data is written into a shared Google Sheet, enhancing transparency and collaboration among team members. [Output](https://docs.google.com/spreadsheets/d/1Zc4i5V5e7hKnUXJftCUDD3ISfsUsMml2HTUFnzyJU74/edit?usp=sharing)

## Technologies Used

- **CrewAI**: Serves as the agentic framework, orchestrating autonomous AI agents to perform specific tasks collaboratively. 
- **Composio**: Provides a suite of tools that integrate with AI agents, enabling them to perform actions such as data extraction and analysis. 
- **Apify**: Utilized for web scraping, allowing the extraction of data from YouTube and other relevant sources.
- **OpenAI Assistants**: Employed for data analysis, leveraging advanced AI capabilities to assess and interpret the gathered information.
