# Telegemi: Telegram Autoresponder with Google Gemini

A Python-based Telegram autoresponder that uses a **user account** (via Telethon) to automatically reply to incoming private messages using Google's Gemini AI. The bot's personality and response style are defined by a customizable system prompt loaded from a file.

---

## Features

*   **Automatic Replies:** Responds to incoming private messages on your Telegram user account.
*   **AI-Powered Responses:** Utilizes the Google Gemini API (`gemini-1.5-flash` by default, configurable) to generate context-aware replies.
*   **Customizable Persona:** Define the bot's behavior, personality, and response style through an external `system_prompt.txt` file.
*   **Logging:** Logs activity to both the console and a file (`logs.txt`) for monitoring and debugging.
*   **Configuration via Environment Variables:** Securely manage API keys and sensitive information.
*   **Fallback Mechanism:** Provides a default message if the Gemini API fails or returns an empty response.
*   **Safety Settings Control:** Includes options to adjust Gemini's content safety filters (use with caution).

---

## Getting Started

### Prerequisites

*   **Python:** Version 3.8 or higher installed.
*   **Telegram Account:** A regular Telegram user account (this script does **not** use a Telegram Bot Token).
*   **Telegram API Credentials:**
    *   `API_ID` and `API_HASH`. You can obtain these from [my.telegram.org](https://my.telegram.org/apps).
*   **Google Gemini API Key:**
    *   Obtain an API key from [Google AI Studio](https://aistudio.google.com/app/apikey).

### Installation & Setup

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/chernobrys/Telegemi.git 
    cd Telegemi
    ```

2.  **Create a Virtual Environment (Recommended):**
    ```bash
    python -m venv venv
    ```
    *   Activate the environment:
        *   **Linux/macOS:** `source venv/bin/activate`
        *   **Windows:** `venv\Scripts\activate`

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configuration:**
    *   **Environment Variables:** Set the following environment variables in your system or deployment environment:
        *   `API_ID`: Your Telegram API ID.
        *   `API_HASH`: Your Telegram API Hash.
        *   `PHONE_NUM`: Your Telegram phone number (in international format, e.g., +1234567890).
        *   `GOOGLE_API_KEY`: Your Google Gemini API Key.
    *   **(Optional) Using a `.env` file:**
        *   Install `python-dotenv` (`pip install python-dotenv` and uncomment it in `requirements.txt`).
        *   Create a file named `.env` in the project root.
        *   Add your credentials:
            ```dotenv
            API_ID=1234567
            API_HASH=your_api_hash_here
            PHONE_NUM=+1234567890
            GOOGLE_API_KEY=your_gemini_api_key_here
            ```
        *   **Ensure `.env` is listed in your `.gitignore` file!**
    *   **System Prompt File:**
        *   The repository includes a file named `system_prompt.txt` located in the project root (the same directory as `main.py`).
        *   This file defines the AI's persona, instructions, and response style.
        *   You can (and are encouraged to) **edit this file** and replace the default text with your own custom instructions to give the bot a specific personality or behavior.
        *   Ensure the file is saved with **UTF-8 encoding** if you modify it.
        *   **Note:** The script requires this file to exist and contain text to run. Do not leave it empty.

5.  **Run the Bot:**
    ```bash
    python main.py
    ```
    *   **First Run:** Telethon will likely ask you to enter your phone number, the code sent to your Telegram account, and potentially your 2FA password (if enabled) interactively in the console. This creates the `.session` file for future logins.

---

## Configuration Details

*   **Environment Variables:** `API_ID`, `API_HASH`, `PHONE_NUM`, `GOOGLE_API_KEY`.
*   **`main.py` Constants:**
    *   `SESSION_FILE`: (`my_telegram_session.session`) Name for the Telethon session file.
    *   `PROMPT_FILENAME`: (`system_prompt.txt`) Name of the file containing the system prompt.
    *   `GEMINI_MODEL_NAME`: (`gemini-1.5-flash`) Gemini model to use.
    *   `FALLBACK_MESSAGE`: Message sent if Gemini fails.
*   **`safety_settings` (in `main.py`):** Controls Gemini's content filtering. Default settings disable most filters (`BLOCK_NONE`). Adjust or remove as needed.

---

## Contributing

Contributions are welcome! Please fork the repository, make changes, and submit a pull request.

---

## License

Distributed under the MIT License. See `LICENSE` file for more information.

---

## Acknowledgements

*   [Telethon Library](https://github.com/LonamiWebs/Telethon)
*   [Google Gemini API](https://ai.google.dev/)

---

**Disclaimer:** Using user accounts for automated actions might violate Telegram's Terms of Service. Use this script responsibly and at your own risk. Ensure your system prompt and usage comply with Google's API policies.
