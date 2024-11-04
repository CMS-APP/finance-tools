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


def email_html(tickers):
    html = """
    <html>
    <head>
    <style>
        table {
            font-family: Arial, sans-serif;
            border-collapse: collapse;
            width: 100%;
        }
        th, td {
            border: 1px solid #dddddd;
            text-align: left;
            padding: 8px;
        }
        th {
            background-color: #f2f2f2;
        }
    </style>
    </head>
    <body>
    <h1>Hello, here are the top stocks for today:</h1>
    <h2>Here are the top stocks for today:</h2>
    <table>
        <tr>
            <th>Ticker</th>
            <th>Current Price ($)</th>
            <th>Highest Price ($)</th>
            <th>Off All Time High (%)</th>
            <th>Five Year Return (%)</th>
            <th>Year To Date Return (%)</th>
            <th>Yearly Returns (%)</th>
            <th>Volatility</th>
            <th>Sharpe Ratio</th>
        </tr>
    """

    # Iterate over each ticker to add data rows
    for ticker in tickers:
        yearly_return = "<ul>"
        for index, year_return in enumerate(ticker.yearly_return):
            if index == 0:
                yearly_return += f"<li>Year 1: {round(ticker.ytd_return, 2)}%</li>"
            else:
                yearly_return += f"<li>Year {index + 1}: {round(year_return, 2)}%</li>"
        yearly_return += "</ul>"

        # Construct the table row for each ticker
        row = f"""
        <tr>
            <td><b>{ticker.ticker}</b></td>
            <td>{round(ticker.data_close[-1], 3)}</td>
            <td>{round(ticker.max_close, 3)}</td>
            <td>{round(ticker.off_all_time_high, 2)}%</td>
            <td>{round(ticker.five_yr_return, 2)}%</td>
            <td>{round(ticker.ytd_return, 2)}%</td>
            <td>{yearly_return}</td>
            <td>{round(ticker.volatility, 2)}</td>
            <td>{round(ticker.sharpe_ratio, 2)}</td>
        </tr>
        """
        html += row

    html += """
    </table>

    <h2>Thank you for using our service.</h2>
    </body>
    </html>
    """
    return html


def get_emails():
    with open("emails.csv", "r") as file:
        return file.read().splitlines()


def default_email_service(html):
    emails = get_emails()
    email_from = emails[0]
    emails_to = emails
    subject = "Daily Top Stock Newsletter"

    send_email(email_from, emails_to, subject, html)
