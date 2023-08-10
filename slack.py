from slack_sdk import WebClient

# Set your Slack API token here
slack_token = "xoxp-cośtam"

# Initialize the Slack Web API client
client = WebClient(token=slack_token)


def get_last_message(channel_id):
    response = client.conversations_history(channel=channel_id, limit=1)

    if response["ok"] and response["messages"]:
        return response["messages"][0]
    else:
        print(f"Error fetching last message for channel {channel_id}: {response.get('error', 'Unknown error')}")
        return None


def get_all_channels_with_last_message():
    all_channels_with_last_message = []
    cursor = None

    while True:
        response = client.conversations_list(types="public_channel,private_channel", cursor=cursor)

        if response["ok"]:
            channels = response["channels"]
            for channel in channels:
                last_message = get_last_message(channel["id"])
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

    last_message = channel.get("last_message")
    if last_message:
        print("Last Message Text:", last_message.get("text", "No messages"))
        print("Last Message Timestamp:", last_message.get("ts"))

    print("-" * 30)
