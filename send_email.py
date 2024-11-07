from mailjet_rest import Client
import os
import pandas as pd


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

def add_stock_to_table(ticker, html):
    yearly_return = "<ul>"
    for index, year_return in enumerate(ticker.yearly_return):
        if index == 0:
            yearly_return += f"<li>Year 1: {round(ticker.ytd_return, 2)}%</li>"
        else:
            yearly_return += f"<li>Year {index + 1}: {round(year_return, 2)}%</li>"
    yearly_return += "</ul>"

    html += f"""
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
    """

    if ticker.market_cap:
        html += f"<td>{round(ticker.market_cap / 1_000_000, 2)}M</td>"

    html += "</tr>"
    return html

def email_html(normal_tickers, good_tickers):
    today_date = pd.to_datetime("today")
    # Convert to be DD/MM/YYYY
    today_date = today_date.strftime("%d/%m/%Y")

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
    <h1>The Top Stock Newsletter</h1>
    """
    
    html += f"""
    <p>Welcome to today's stock information for: {today_date}. The first table includes data on common stocks, while the second are stock which have high growth.</p>
    <h2>Common Stock Data:</h2>
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

    for ticker in normal_tickers:
        html = add_stock_to_table(ticker, html)

    html += """
    </table>

    <h2>Best Stocks Data:</h2>
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
            <th>Market Cap</th>
        </tr>
    """

    # Iterate over each ticker to add data rows
    for ticker in good_tickers:
        html = add_stock_to_table(ticker, html)

    html += """
    </table>
    </body>
    </html>
    """
    return html


def get_emails(testing):
    file_folder = os.path.dirname(os.path.realpath(__file__))

    if testing:
        file_path = os.path.join(file_folder, "test_emails.csv")
    else:
        file_path = os.path.join(file_folder, "emails.csv")

    with open(file_path, "r") as file:
        return file.read().splitlines()


def default_email_service(html, testing):
    emails = get_emails(testing)
    email_from = emails[0]
    emails_to = emails
    subject = "Daily Top Stock Newsletter"

    print("Sending Email to: ", emails_to)

    if testing:
        # Save HTML to a file
        with open("test_email.html", "w") as file:
            file.write(html)
            file.close()

    send_email(email_from, emails_to, subject, html)
