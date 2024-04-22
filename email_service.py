import imaplib, email
import poplib
from settings import EMAIL_PROVIDERS
from email.utils import parsedate_to_datetime, parseaddr
from bs4 import BeautifulSoup
from database import create_table_if_not_exists, open_db_connection, open_mongo_connection, close_db_connection, insert_into_db


def get_provider_servers(email_addr):
    domain = email_addr.split('@')[1].split('.')[0]
    if domain in EMAIL_PROVIDERS:
        imap_server = EMAIL_PROVIDERS[domain]['imap']
        pop3_server = EMAIL_PROVIDERS[domain]['pop3']
        return imap_server, pop3_server
    else:
        raise ValueError('Email provider not recognized. Please input server settings manually.')


def has_attachments(email_message):
    attachment_count = 0
    for part in email_message.walk():
        if part.get_content_maintype() == 'multipart' or part.get('Content-Disposition') is None:
            continue
        attachment_count += 1
    return attachment_count > 0, attachment_count


def process_email(raw_email):
    email_body = ""
    attachments = []

    email_message = email.message_from_bytes(raw_email)

    message_id = email_message.get('Message-ID')

    if email_message.is_multipart():
        for part in email_message.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain" or content_type == "text/html":
                content = part.get_payload(decode=True)
                if isinstance(content, bytes):
                    content = content.decode('utf-8', 'ignore')
                email_body += content + "\n"
            else:
                content = part.get_payload(decode=True)
                if isinstance(content, bytes):
                    content = content.decode('utf-8', 'ignore')
                attachments.append(content)
    else:
        content_type = email_message.get_content_type()
        content = email_message.get_payload(decode=True)
        if isinstance(content, bytes):
            content = content.decode('utf-8', 'ignore')
        if content_type == "text/plain" or content_type == "text/html":
            email_body = content
        else:
            attachments.append(content)
    return (
        parsedate_to_datetime(email_message['Date']) if email_message else None,
        parseaddr(email_message['From'])[1] if email_message else None,
        email_message['Subject'] if email_message else None,
        bool(attachments),
        len(attachments),
        parseaddr(email_message['To'])[1] if email_message else None,
        message_id,
        email_body,
        attachments
    )


def load_emails_from_inbox(email_addr, password):
    db_connection, db_cursor = open_db_connection()
    mongo_db = open_mongo_connection()

    imap_server, pop3_server = get_provider_servers(email_addr)

    connected = False
    try:
        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(email_addr, password)
        mail.select('inbox')
        protocol = 'IMAP'
        connected = True
    except:
        try:
            mail = poplib.POP3_SSL(pop3_server)
            mail.user(email_addr)
            mail.pass_(password)
            protocol = 'POP3'
            connected = True
        except Exception as e:
            print(e)

    if connected:
        if protocol == 'IMAP':
            result, messages = mail.search(None, 'ALL')

            if result == 'OK':
                for num in messages[0].split():
                    result, data = mail.fetch(num, '(BODY[])')
                    raw_email = data[0][1]
                    email_data = process_email(raw_email)
                    insert_into_db(db_cursor, db_connection, mongo_db, email_data)

        elif protocol == 'POP3':
            num_messages = len(mail.list()[1])

            for num in range(1, num_messages + 1):
                raw_email = b'\n'.join(mail.retr(num)[1])
                email_data = process_email(raw_email)
                insert_into_db(db_cursor, db_connection, mongo_db, email_data)

    close_db_connection(db_connection, db_cursor)

    return True
