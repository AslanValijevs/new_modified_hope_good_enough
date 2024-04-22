import imaplib, email, poplib


EMAIL_PROVIDERS = {
    'gmail': {
        'imap': 'imap.gmail.com',
        'pop3': 'pop.gmail.com',
    },
    'yahoo': {
        'imap': 'imap.mail.yahoo.com',
        'pop3': 'pop.mail.yahoo.com',
    },
    'outlook': {
        'imap': 'imap-mail.outlook.com',
        'pop3': 'pop-mail.outlook.com'
    }
}

#MySQL Database
db_Host =''
db_User =''
db_Password =''
db_Name =''

#MongoDB Database
mn_Host = ''
mn_Name = ''
mn_Collection = ''
