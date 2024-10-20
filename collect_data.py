from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scrape import run_scraper, get_group_metadata, save_group_metadata

# Initialize the WebDriver
driver = webdriver.Chrome()  # Make sure to have the appropriate WebDriver for your browser in your PATH
wait = WebDriverWait(driver, 120)  # Adjust the timeout as needed

# Define the chat name as a global or config variable
chat_name = "Your Group Name"  # Replace with the actual group name

# Function to open the group chat by navigating to the WhatsApp Web
def open_group_chat():
    """Open the group chat by navigating to the WhatsApp Web."""
    try:
        driver.get("https://web.whatsapp.com/")  # Open WhatsApp Web
        print("Navigating to WhatsApp Web...")

        # Wait for WhatsApp Web to load and look for the chat with the group name
        group_chat = wait.until(EC.presence_of_element_located(
            (By.XPATH, f'//span[@title="{chat_name}"]')
        ))
        group_chat.click()  # Click to open the chat
        print(f"Opened the group chat: {chat_name}")

    except Exception as e:
        print(f"Failed to open group chat: {e}")
        driver.save_screenshot('open_group_error.png')  # Save a screenshot for debugging

# Now open the group chat
open_group_chat()

# Fetch the group metadata (ID, name, etc.)
metadata = get_group_metadata()

# Save the group metadata to a CSV
if metadata:
    save_group_metadata(metadata, 'group_details.csv')
    print("Group metadata saved.")
else:
    print("Failed to retrieve group metadata.")

# Now, run the scraper to scrape chat messages and save them to a CSV
run_scraper()

print("Scraping process completed.")
