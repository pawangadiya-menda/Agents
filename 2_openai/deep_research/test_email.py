from messenger import send_email

send_email(
    recipient="pawangadiya@gmail.com",
    subject="Test from Deep Research",
    text_body="Plain text test.",
    html_body="<h2>HTML test</h2><p>It works.</p>",
)
print("Sent OK")
