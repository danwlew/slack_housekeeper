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

    print("-" * 30)