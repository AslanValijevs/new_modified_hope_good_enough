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
db_Host ='emaildbserver.mysql.database.azure.com'
db_User ='mailadmin'
db_Password ='Wparolj123!'
db_Name ='maildb1'

#MongoDB Database
mn_Host = 'mongodb://localhost:27017/'
mn_Name = 'Mongo_email_db'
mn_Collection = 'Email'
