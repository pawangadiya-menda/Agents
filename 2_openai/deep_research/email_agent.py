from agents import Agent
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os

load_dotenv(override=True)

MODEL_NAME = os.getenv("DEFAULT_MODEL_NAME", "gpt-5.4-mini")


class EmailContent(BaseModel):
    subject: str = Field(description="Subject line of the email")
    text_body: str = Field(description="Plain text version of the email")
    html_body: str = Field(description="HTML version of the email")


INSTRUCTIONS = """
You are an expert email writer.

You will receive a detailed research report in Markdown.

Your job is to generate:

1. A professional subject line.
2. A plain-text version of the email.
3. A clean HTML email.

Rules:
- Make the subject concise and informative.
- Preserve the important content of the report.
- Produce well-formatted HTML using headings, paragraphs, bullet lists, and emphasis where appropriate.
- Do NOT send the email.
- Only generate the email content.
"""


email_agent = Agent(
    name="Email Agent",
    instructions=INSTRUCTIONS,
    model=MODEL_NAME,
    output_type=EmailContent,
)