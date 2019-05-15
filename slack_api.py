import slack


class SlackApi:
    def __init__(self, token: str):
        self.token = token

    def send_message(self, channel: str, message: str):
        client = slack.WebClient(self.token)

        response = client.chat_postMessage(
            channel=channel, text=message)

        return response
