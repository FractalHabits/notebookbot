# NoteBookBot

NoteBookBot is a research assistant that can retrieve articles from arXiv. It is powered by language models from OpenAI and Anthropic.

## Getting Started

1. Start off by going to 
Start by running the `src/scripts/setup_authentication.py` script to create a password and enter your OpenAI and Anthropic API keys. These keys will be encrypted behind the password you create.

2. To test the NoteBookBot, run the `src/scripts/notebookbot_run.py` file. This script will prompt you for the password you created in the previous step and use it to create an Anthropic-powered NoteBookBot instance.

More tools and a Gradio UI are coming soon, along with the ability to easily import and use NoteBookBot from computational notebooks.
