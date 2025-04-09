import time
import logging
import os
import asyncio

from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError

# --- Google AI Library (importing earlier is better) ---
try:
    import google.generativeai as genai
except ImportError:
    # Using print because the logger might not be configured yet
    print("Please install the Google AI library: pip install google-generativeai")
    exit(1)

# --- Configuration ---
# 1. TELEGRAM API KEYS
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')

# 2. TELEGRAM ACCOUNT DETAILS
PHONE_NUMBER = os.getenv('PHONE_NUM')

# 3. TELEGRAM SESSION FILE
SESSION_FILE = 'my_telegram_session.session' # This file should NOT be committed

# 4. PROMPT FILENAME
PROMPT_FILENAME = 'system_prompt.txt' # Filename for loading the prompt

# 5. GOOGLE GEMINI API KEY
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    print("Error: GOOGLE_API_KEY environment variable is not set.")
    print("Please obtain a key from https://aistudio.google.com/app/apikey and set the environment variable.")
    exit(1)

# --- Logging Setup ---
log_format = '%(asctime)s - %(levelname)s - %(message)s'
log_filename = 'logs.txt' # This file should NOT be committed
logging.basicConfig(
    level=logging.INFO,
    format=log_format,
    handlers=[logging.StreamHandler()] # Explicitly specify the console handler
)
logger = logging.getLogger()
try:
    # Log file handler (use 'a' for append mode)
    file_handler = logging.FileHandler(log_filename, encoding='utf-8', mode='a')
    file_handler.setLevel(logging.INFO) # Set level for file logging
    formatter = logging.Formatter(log_format)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler) # Add handler to the root logger
    logging.info(f"Logging configured. Messages will be output to console and saved to '{log_filename}'")
except Exception as e:
    # Error will be logged to console via basicConfig
    logging.error(f"Failed to set up logging to file '{log_filename}': {e}")
# --- END Logging Setup ---

# --- LOADING SYSTEM PROMPT FROM FILE ---
SYSTEM_PROMPT = "" # Initialization
try:
    logger.info(f"Attempting to load system prompt from file '{PROMPT_FILENAME}'...")
    with open(PROMPT_FILENAME, 'r', encoding='utf-8') as f:
        SYSTEM_PROMPT = f.read().strip() # Read file CONTENT

    if not SYSTEM_PROMPT:
        # This error will go to both console and log file (if configured)
        logger.error(f"Error: Prompt file '{PROMPT_FILENAME}' is empty.")
        # Additionally print to ensure visibility
        print(f"Critical Error: Prompt file '{PROMPT_FILENAME}' is empty. Please fill the file.")
        exit(1) # Exit if prompt is crucial and file is empty

    logger.info(f"System prompt successfully loaded from '{PROMPT_FILENAME}'.")

except FileNotFoundError:
    logger.error(f"Critical Error: Prompt file '{PROMPT_FILENAME}' not found.")
    print(f"Critical Error: Prompt file '{PROMPT_FILENAME}' not found.")
    print(f"Please create the file '{PROMPT_FILENAME}' and place the system prompt text inside.")
    exit(1) # Exit if prompt file is missing
except Exception as e:
    logger.error(f"Critical Error reading prompt file '{PROMPT_FILENAME}': {e}", exc_info=True)
    print(f"Critical Error reading prompt file '{PROMPT_FILENAME}': {e}")
    exit(1) # Exit on other file reading errors
# --- END PROMPT LOADING ---

# --- REMAINING CONFIGURATION ---
# 6. GEMINI SETTINGS
#    Make sure the desired, available model is specified
GEMINI_MODEL_NAME = 'gemini-1.5-flash' # Or 'gemini-1.5-pro-latest', etc.

# 7. FALLBACK RESPONSE
#    User-facing message if Gemini fails
FALLBACK_MESSAGE = "Sorry, I cannot respond right now. Will contact you later."

# --- Gemini Initialization ---
try:
    genai.configure(api_key=GOOGLE_API_KEY)
    gemini_model = genai.GenerativeModel(GEMINI_MODEL_NAME)
    logging.info(f"Gemini model '{GEMINI_MODEL_NAME}' initialized.")
except Exception as e:
    logging.error(f"Error initializing Gemini: {e}", exc_info=True)
    gemini_model = None # Set to None to check later
# --- End Gemini Initialization ---

# --- Main Application (entry point) ---

async def main():
    # Check for essential environment variables before starting
    if not API_ID or not API_HASH:
        logging.error("Critical Error: API_ID or API_HASH not set in environment variables.")
        print("Critical Error: Make sure API_ID and API_HASH environment variables are set.")
        exit(1)
    if not PHONE_NUMBER:
        logging.error("Critical Error: PHONE_NUM not set in environment variables.")
        print("Critical Error: Make sure PHONE_NUM environment variable is set.")
        exit(1)

    # Check if API_ID is a number before conversion
    try:
        api_id_int = int(API_ID)
    except (ValueError, TypeError):
        logging.error(f"Critical Error: API_ID ('{API_ID}') is not a valid integer.")
        print(f"Critical Error: API_ID ('{API_ID}') must be an integer.")
        exit(1)

    logging.info("Initializing Telegram client...")
    client = TelegramClient(
        SESSION_FILE,
        api_id_int,
        API_HASH,
        sequential_updates=True # Recommended for user bots
    )

    # --- Registering message handler ---
    @client.on(events.NewMessage(incoming=True))
    async def handle_new_message(event):
        """Handles incoming messages and generates a response using Gemini."""
        # Ignore messages from groups/channels, only process private chats
        if not event.is_private:
            return

        sender = None # Initialize sender
        try:
            sender = await event.get_sender()
            # Ignore messages from bots, self, or without a sender
            if not sender or sender.bot or sender.is_self:
                return

            incoming_text = event.message.text
            # Ignore messages without text content (e.g., photos, stickers)
            if not incoming_text:
                 logging.debug(f"Message {event.id} from {sender.username or sender.id} ignored (no text).")
                 return

            logging.info(f"Received message from {sender.username or sender.id}: '{incoming_text[:50]}...'")

            reply_text = FALLBACK_MESSAGE # Default response

            # Proceed only if Gemini model was initialized successfully
            if gemini_model:
                try:
                    # Form the full prompt for Gemini
                    full_prompt = f"{SYSTEM_PROMPT}\n\nUser message:\n{incoming_text}" # Added context marker

                    # Asynchronous call to Gemini
                    logging.debug("Querying Gemini...")
                    # Safety settings to potentially allow more content types
                    # Use with caution and adjust according to Google's policies
                    safety_settings = [
                        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
                    ]
                    response = await gemini_model.generate_content_async(
                        full_prompt,
                        safety_settings=safety_settings
                        # generation_config=genai.types.GenerationConfig(...) # Optional: Add temperature, top_k etc.
                    )
                    logging.debug("Received response from Gemini.")

                    # Check response validity and extract text safely
                    try:
                        reply_text = response.text.strip()
                        if not reply_text:
                            # Handle cases where Gemini responds but text is empty
                             logging.warning("Gemini returned a valid response object, but the generated text is empty. Using fallback.")
                             reply_text = FALLBACK_MESSAGE
                    except (ValueError, AttributeError): # Catch potential errors if response structure is unexpected
                        logging.warning("Gemini response structure invalid or text extraction failed. Using fallback.")
                        if response and response.prompt_feedback:
                           logging.warning(f"Gemini prompt feedback: {response.prompt_feedback}")
                        reply_text = FALLBACK_MESSAGE

                # Handle potential API errors during generation
                except Exception as e:
                    logging.error(f"Error calling Gemini API: {e}", exc_info=False)
                    logging.warning("Failed to generate response via Gemini. Using fallback.")
                    reply_text = FALLBACK_MESSAGE
            else:
                # Handle case where Gemini model failed to initialize
                logging.warning("Gemini model was not initialized. Using fallback response.")

            # Optional short delay before sending response
            await asyncio.sleep(1)

            # Send the reply
            await event.respond(reply_text)
            logging.info(f"Response ('{reply_text[:50]}...') sent to {sender.username or sender.id}")

        # Catch-all for unexpected errors during message handling
        except Exception as e:
            sender_info = f" from {sender.username or sender.id}" if sender else ""
            logging.error(f"General error processing message {event.id}{sender_info}: {e}", exc_info=True)

    # --- Starting Client ---
    logging.info("Starting autoresponder...")
    try:
        # Connect and log in using the phone number
        await client.start(phone=PHONE_NUMBER)

        if client.is_connected():
             me = await client.get_me()
             logging.info(f"Client successfully started as {me.username}. Waiting for messages...")
             # Keep the client running until disconnected
             await client.run_until_disconnected()
        else:
             # This case is less likely as start() usually raises exceptions on failure
             logging.error("Failed to connect to Telegram after client.start().")

    except SessionPasswordNeededError:
         logging.warning("Two-factor authentication (2FA) password required.")
         # Inform the user how to handle 2FA
         print("Please run the script interactively once to enter the 2FA password when prompted by Telethon.")
    except Exception as e:
        logging.error(f"Critical error during client startup or execution: {e}", exc_info=True)
    finally:
        # Ensure disconnection when the script stops or crashes
        logging.info("Stopping autoresponder...")
        if client.is_connected():
            await client.disconnect()
            logging.info("Client disconnected.")
        else:
             logging.info("Client was not connected or already disconnected.")


# --- Script Execution ---
if __name__ == "__main__":
    # Run the main asynchronous function
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Script interrupted by user (Ctrl+C). Exiting.")