from slack_sdk import WebClient
from datetime import datetime, timedelta

# Set your Slack API token here
slack_token = "xoxp-cośtam"

# Initialize the Slack Web API client
client = WebClient(token=slack_token)


def get_channel_creator(channel_id):
    response = client.conversations_info(channel=channel_id)

    if response["ok"]:
        return response["channel"].get("creator")
    else:
        print(f"Error fetching channel info for channel {channel_id}: {response.get('error', 'Unknown error')}")
        return None


def get_last_message(channel_id):
    response = client.conversations_history(channel=channel_id, limit=1)

    if response["ok"] and response["messages"]:
        return response["messages"][0]
    else:
        print(f"Error fetching last message for channel {channel_id}: {response.get('error', 'Unknown error')}")
        return None


def convert_unix_timestamp_to_datetime(unix_timestamp):
    return datetime.fromtimestamp(float(unix_timestamp))


def get_time_duration(last_message_time):
    current_time = datetime.now()
    duration = current_time - last_message_time
    return duration


def send_notification_to_creator(creator_id, channel_name):
    message = (
        f"The channel #{channel_name} has been inactive for more than 2 hours. "
        "It will be autoarchived soon. If you wish to keep the channel active, please send a message."
    )

    response = client.chat_postMessage(channel=creator_id, text=message)
    if response["ok"]:
        print("Notification sent successfully to channel creator.")
    else:
        print(f"Error sending notification to channel creator: {response.get('error', 'Unknown error')}")


def send_notification_to_housekeeping(channel_name):
    housekeeping_channel = "#housekeeping"  # Replace with the actual name or ID of the channel

    message = (
        f"Autoarchive Notice: The channel #{channel_name} has been inactive for more than 2 hours and will be autoarchived soon. "
        "If there are any concerns, please address them."
    )

    response = client.chat_postMessage(channel=housekeeping_channel, text=message)
    if response["ok"]:
        print("Notification sent successfully to #housekeeping channel.")
    else:
        print(f"Error sending notification to #housekeeping channel: {response.get('error', 'Unknown error')}")


def send_archived_notification(channel_id, channel_name):
    archive_notification = (
        f"The channel #{channel_name} has been archived. If you need it reopened, please contact an admin. :("
    )

    response = client.chat_postMessage(channel=channel_id, text=archive_notification)
    if response["ok"]:
        print("Archived notification sent successfully to channel.")
    else:
        print(f"Error sending archived notification to channel: {response.get('error', 'Unknown error')}")


def archive_channel(channel_id):
    response = client.conversations_archive(channel=channel_id)
    if response["ok"]:
        print(f"Channel {channel_id} archived successfully.")
    else:
        print(f"Error archiving channel {channel_id}: {response.get('error', 'Unknown error')}")


def get_all_channels_with_last_message():
    all_channels_with_last_message = []
    cursor = None

    while True:
        response = client.conversations_list(types="public_channel,private_channel", cursor=cursor)

        if response["ok"]:
            channels = response["channels"]
            for channel in channels:
                channel_id = channel["id"]
                creator_id = get_channel_creator(channel_id)
                last_message = get_last_message(channel_id)

                channel["creator_id"] = creator_id
                channel["last_message"] = last_message
                all_channels_with_last_message.append(channel)

            cursor = response.get("response_metadata", {}).get("next_cursor")

            if not cursor:
                break
        else:
            print("Error fetching channel list:", response["error"])
            break

    return all_channels_with_last_message


channel_list_with_last_message = get_all_channels_with_last_message()
for channel in channel_list_with_last_message:
    print("Channel ID:", channel["id"])
    print("Channel Name:", channel["name"])
    print("Is Channel:", channel["is_channel"])
    print("Is Member:", channel["is_member"])

    creator_id = channel.get("creator_id")
    if creator_id:
        print("Channel Creator ID:", creator_id)

    last_message = channel.get("last_message")
    if last_message:
        print("Last Message Text:", last_message.get("text", "No messages"))
        print("Last Message Timestamp:", last_message.get("ts"))

        last_message_time = convert_unix_timestamp_to_datetime(last_message.get("ts"))
        print("Last Message Time:", last_message_time)

        time_duration = get_time_duration(last_message_time)
        print("Time Duration since Last Message:", time_duration)

        if time_duration > timedelta(hours=2):
            send_notification_to_creator(creator_id, channel["name"])
            send_notification_to_housekeeping(channel["name"])

        if time_duration > timedelta(hours=24):
            archive_channel(channel["id"])
            send_archived_notification(channel["id"], channel["name"])

    print("-" * 30)