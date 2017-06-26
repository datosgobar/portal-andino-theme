# coding=utf-8
import ckan.lib.mailer as ckan_mailer
import ckanext.gobar_theme.helpers as gobar_helpers
import smtplib
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart
try:
    from socket import sslerror
except ImportError:
    sslerror = None
MailerException = ckan_mailer.MailerException


def reset_mail_content(user):
    if len(user.fullname) > 0:
        user_name = user.fullname
    else:
        user_name = user.name
    reset_link = ckan_mailer.get_reset_link(user)
    site_title = gobar_helpers.get_theme_config('title.site-title', 'Portal Andino')
    body = '¡Hola, %s\n\n' % user_name + \
        'Parece que olvidaste tu contraseña. No te preocupes, vamos a cambiarla:\n\n' + \
        '<a href="%s" target="_blank">Crear nueva contraseña</a>\n\n' % reset_link + \
        '¡Suerte!\n' + \
        'El equipo de %s.\n' % site_title
    subject = 'Recuperemos tu contraseña de %s' % site_title
    return subject, body


def send_reset_link(user):
    ckan_mailer.create_reset_key(user)
    subject, body = reset_mail_content(user)
    ckan_mailer.mail_user(user, subject, body)


class EmailSender:
    def __init__(self, smtp_server='localhost', smtp_username=None, smtp_password=None, smtp_use_tls=False):
        self.smtp_server = smtp_server
        self.smtp_username = smtp_username
        self.smtp_password = smtp_password
        self.smtp_use_tls = smtp_use_tls

    def send_email(self, **kwargs):
        msg = self.assemble_email(kwargs['msg_body'], kwargs['msg_subject'], kwargs['msg_from'], kwargs['msg_to'])
        server = smtplib.SMTP(self.smtp_server)
        if self.smtp_use_tls:
            server.ehlo()
            server.starttls()
            server.ehlo()
        if self.smtp_username and self.smtp_password:
            server.login(self.smtp_username, self.smtp_password)
        server.sendmail(kwargs['msg_from'], kwargs['msg_to'], msg.as_string())
        try:
            server.quit()
        except sslerror:
            # sslerror is raised in tls connections on closing sometimes
            pass

    @staticmethod
    def assemble_email(msg_body, msg_subject, from_address, to_addresses):
        msg = MIMEMultipart()
        msg.set_type('multipart/alternative')
        msg.preamble = msg.epilogue = ''
        text_msg = MIMEText(msg_body)
        text_msg.set_type('text/plain')
        text_msg.set_param('charset', 'ASCII')
        msg.attach(text_msg)
        html_msg = MIMEText(msg_body)
        html_msg.set_type('text/html')
        # @@: Correct character set?
        html_msg.set_param('charset', 'UTF-8')
        html_long = MIMEText(msg_body)
        html_long.set_type('text/html')
        html_long.set_param('charset', 'UTF-8')
        msg.attach(html_msg)
        msg.attach(html_long)
        msg['Subject'] = msg_subject
        msg['From'] = from_address
        msg['To'] = ', '.join(to_addresses)
        return msg
