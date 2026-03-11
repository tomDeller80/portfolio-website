from mailersend import MailerSendClient, EmailBuilder
from html2text import html2text
from logger import Logger
from pprint import pprint

class Mailer():

    def __init__(self, sender_name, sender_email, key):

        self.sender_name = sender_name
        self.sender_email = sender_email
        self.ms = MailerSendClient(api_key=key)
        self.logger = Logger(__name__).get_logger()


    def send_email(self, email, name, subject, content):

        try:

            request = (EmailBuilder()
                     .from_email(
                        email=self.sender_email,
                        name=self.sender_name
                     )
                     .to_many([{ "email": f"{email}", "name": f"{name}" }])
                     .subject(subject)
                     .html(content)
                     .text(html2text(content).strip())
                     .build())

            response = self.ms.emails.send(request)

            pprint(response)

            if not response.success:

                error_data = response.data
                error_message = error_data.get("message", "Unknown error")
                error_code = error_data.get("code")

                return {
                    "status_code": response.status_code,
                    "text": f"[{error_code}] {error_message}"
                }

            else:

                return {
                    "status_code": response.status_code,
                    "text": "Successfully sent email"
                }

        except Exception as e:

            self.logger.exception("MailerSend sending failed")

            return {
                "status_code": 500,
                "text": f"MailerSend error: {str(e)}"
            }