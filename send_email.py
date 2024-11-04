from mailjet_rest import Client
import os

def send_email(email_from, emails_to, subject, html):
    api_key = os.environ["MJ_APIKEY_PUBLIC"]
    api_secret = os.environ["MJ_APIKEY_PRIVATE"]
    mailjet = Client(auth=(api_key, api_secret))

    recipients = [{"Email": email} for email in emails_to]

    data = {
        "FromEmail": email_from,
        "FromName": "Stock Info",
        "Subject": subject,
        "Html-part": html,
        "Recipients": recipients,
    }
    mailjet.send.create(data=data)

def default_email_service(tickers):
    email_from = "christopher.sharp@hotmail.co.uk"
    emails_to = ["christopher.sharp@hotmail.co.uk", "nuclearcactus1@gmail.com"]
    subject = "Daily Top Stock Newsletter"
    html= """<h1>Hello, here are the top stocks for today:</h1>"""

    for ticker in tickers:
        header = f"<h2>{ticker.ticker}</h2>"
        five_yr_return = f"<p>Five Year Return: {ticker.five_yr_return}</p>"
        ytd_return = f"<p>Year To Date Return: {ticker.ytd_return}</p>"
        current_price = f"<p>Current Price: {ticker.data_close[-1]}</p>"
        off_all_time_high = f"<p>Off All Time High: {ticker.off_all_time_high}</p>"

        yearly_return = "<p>Yearly Return:</p>"
        yearly_return += "<ul>"
        for year_return in ticker.yearly_return:
            yearly_return += f"<li>{year_return}</li>"
        yearly_return += "</ul>"

        html += header + five_yr_return + ytd_return + current_price + off_all_time_high + yearly_return

    

    send_email(email_from, emails_to, subject, html)