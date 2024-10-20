from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import pandas as pd
import csv

# Initial setup
driver = webdriver.Chrome()
wait = WebDriverWait(driver, 120)  # Wait longer for WhatsApp to load

# WhatsApp Web setup: Open the main page
driver.get("https://web.whatsapp.com/")

# Name of the group chat you want to scrape
chat_name = "pookies"  # Replace with your actual group name

def output_to_csv(data, filename):
    """Writes data to a CSV file."""
    try:
        with open(filename, "w", newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Chat', 'Message Type', 'Chat Text', 'Sender Number', 'Chat Time', 'Chat DateTime', 'Sender Name', 'URLs'])  # Header
            writer.writerows(data)
        print(f"Data successfully written to {filename}.")
    except Exception as e:
        print(f"Error writing to CSV: {e}")

def open_group_chat(driver):
    try:
        driver.get("https://web.whatsapp.com/")  # Open WhatsApp Web
        # Your logic to find and open the group chat
    except Exception as e:
        print(f"Failed to open group chat: {e}")
        driver.save_screenshot('open_group_error.png')  # Save screenshot for debugging

# Call the function, passing in the driver
open_group_chat(driver)

def process_chat(chat):
    """Parse the chat HTML to extract message data."""
    message_type = ""
    chat_text = ""

    check_image = chat.find('div', class_='_3v3PK')
    check_video = chat.find('div', class_='_1opHa video-thumb')
    check_admin = '_3rjxZ' in chat['class']
    check_deleted_msg = chat.find('div', class_='_1fkCN')
    check_document = chat.find('a', class_='_1vKRe')
    check_waiting_message = chat.find('div', class_='_3zb-j ZhF0n _18dOq')
    check_whatsapp_audio_1 = chat.find('div', class_='_3_7SH _17oKL message-in')
    check_whatsapp_audio_2 = chat.find('div', class_='_3_7SH _17oKL message-in tail')
    check_sound_clip_1 = chat.find('div', class_='_3_7SH _1gqYh message-in')
    check_sound_clip_2 = chat.find('div', '_3_7SH _1gqYh message-in tail')
    check_gif = chat.find('span', {'data-icon': 'media-gif'})

    if check_video:
        message_type = "video"
    elif check_image:
        message_type = "image"
        try:
            chat_text = chat.find('span', class_='selectable-text invisible-space copyable-text').text
        except Exception as e:
            print(f"Error extracting image chat text: {e}")
    elif check_admin:
        message_type = "admin"
        chat_text = chat.text
    elif check_deleted_msg:
        message_type = "deleted_message"
    elif check_document:
        message_type = "document"
    elif check_waiting_message:
        chat_text = check_waiting_message.text
    elif check_whatsapp_audio_1 or check_whatsapp_audio_2:
        message_type = 'whatsapp_audio'
    elif check_sound_clip_1 or check_sound_clip_2:
        message_type = 'sound_clip'
    elif check_gif:
        message_type = 'gif'
    else:
        message_type = "text"
        try:
            chat_text = chat.find('div', class_='copyable-text').text
        except Exception as e:
            print("Error extracting text message:", e)
            return chat

    sender_number = chat.find('span', class_="RZ7GO").text if chat.find('span', class_="RZ7GO") else "NA"
    chat_time = chat.find('span', class_='_3EFt_').text if chat.find('span', '_3EFt_') else "NA"
    chat_datetime = chat.find('div', class_='copyable-text')['data-pre-plain-text'] if chat.find('div', class_='copyable-text') else "NA"
    chat_msg = chat.find('div', '_3zb-j ZhF0n').text if chat.find('div', '_3zb-j ZhF0n') else "NA"
    sender_name = chat.find('span', '_3Ye_R _1wjpf _1OmDL').text if chat.find('span', '_3Ye_R _1wjpf _1OmDL') else "NA"

    urls = [a['href'] for a in chat.find_all('a')] if chat.find_all('a') else []

    return [chat, message_type, chat_text, sender_number, chat_time, chat_datetime, sender_name, str(urls)]

def get_group_metadata():
    """Extracts metadata for the WhatsApp group."""
    try:
        # Wait for and click the group header to open group details
        group_header = wait.until(EC.presence_of_element_located((By.XPATH, f'//span[@title="{chat_name}"]')))
        group_header.click()
        time.sleep(2)  # Give time for the group info to load

        # Extract group name
        group_name = group_header.get_attribute('title')

        # Attempt to extract group description
        try:
            group_description_element = wait.until(EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "_3VvZl")]')))
            group_description = group_description_element.text if group_description_element else "No Description"
        except Exception as e:
            print(f"Error extracting group description: {e}")
            group_description = "No Description"

        # Extract other metadata similarly...
        admin_details = "You"  # Assuming you're the admin
        group_creation_date = "2023-05-07"  # Update with actual extraction logic
        number_of_members = "3"  # Update with actual extraction logic
        last_activity_date = "2024-10-20"  # Update with actual extraction logic
        group_id = "HACNY2BVSPPBD6kgmHCI7O"  # Update with actual extraction logic

        return {
            "Group ID": group_id,
            "Group Name": group_name,
            "Group Creation Date": group_creation_date,
            "Number of Members": number_of_members,
            "Group Description": group_description,
            "Admin Details": admin_details,
            "Last Activity Date": last_activity_date
        }
    except Exception as e:
        print(f"Error extracting group metadata: {e}")
        return None

def save_group_metadata(metadata, filename='group_details.csv'):
    """Saves group metadata to a CSV file."""
    if metadata:
        try:
            with open(filename, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([
                    metadata['Group ID'], 
                    metadata['Group Name'], 
                    metadata['Group Creation Date'], 
                    metadata['Number of Members'], 
                    metadata['Group Description'], 
                    metadata['Admin Details'], 
                    metadata['Last Activity Date']
                ])
            print(f"Group metadata saved to {filename}.")
        except Exception as e:
            print(f"Error saving metadata: {e}")

def run_scraper():
    """Main function to run the scraper."""
    # First, extract group metadata
    metadata = get_group_metadata()
    
    if metadata:
        save_group_metadata(metadata)

    # Now, continue with scraping chat messages as before
    try:
        message_window = wait.until(EC.presence_of_element_located((By.ID, 'main')))
        print("Main message window found.")

        # Wait for chats to load
        chats = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "vW7d1")))
        print(f"Number of chats loaded: {len(chats)}")

        chat_data = []
        for i in chats:
            parsed_chat = process_chat(i)
            chat_data.append(parsed_chat)

        print("Chat data ready...")
        output_to_csv(chat_data, f'{metadata["Group Name"]}_chats.csv') # type: ignore

    except Exception as e:
        print(f"An error occurred: {e}")

# Run the scraper
run_scraper()
