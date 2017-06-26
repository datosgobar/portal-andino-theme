# coding=utf-8
import ckan.lib.mailer as ckan_mailer
import ckanext.gobar_theme.helpers as gobar_helpers
import smtplib
import ckan
from pylons import config
from email.header import Header
from time import time
from email import Utils
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
    plain_body = u'¡Hola, %s!\n\n' % user_name
    plain_body += u'Parece que olvidaste tu contraseña. No te preocupes, vamos a cambiarla:\n\n'
    plain_body += unicode(reset_link) + '\n\n'
    plain_body += u'¡Suerte!\nEl equipo de %s.\n' % site_title

    html_body = plain_body.replace(reset_link, u'<a href="%s" target="_blank">Crear nueva contraseña</a>' % reset_link)
    html_body = html_body.replace('\n', '<br>')
    subject = u'Recuperemos tu contraseña de %s' % site_title
    return subject, plain_body, html_body


def send_reset_link(user):
    if (user.email is None) or not len(user.email):
        raise MailerException("No recipient email address available!")
    ckan_mailer.create_reset_key(user)
    subject, plain_body, html_body = reset_mail_content(user)
    recipient_name = user.display_name
    recipient_email = user.email
    msg = assemble_email(plain_body, html_body, subject, recipient_name, recipient_email)
    return send_mail(msg, recipient_email)


def assemble_email(msg_plain_body, msg_html_body, msg_subject, recipient_name, recipient_email):
    text_msg = MIMEText(msg_plain_body, 'plain', 'UTF-8')
    html_msg = MIMEText(msg_html_body, 'html', 'UTF-8')
    msg = MIMEMultipart('alternative')
    msg.attach(text_msg)
    msg.attach(html_msg)
    msg['Subject'] = Header(msg_subject.encode('utf-8'), 'utf-8')
    mail_from = config.get('smtp.mail_from')
    site_title = gobar_helpers.get_theme_config('title.site-title', 'Portal Andino')
    msg['From'] = "%s <%s>" % (site_title, mail_from)
    recipient = u"%s <%s>" % (recipient_name, recipient_email)
    msg['To'] = Header(recipient, 'utf-8')
    msg['Date'] = Utils.formatdate(time())
    msg['X-Mailer'] = "CKAN %s" % ckan.__version__
    return msg


def send_mail(msg, recipient_email):
    smtp_connection = smtplib.SMTP()
    smtp_server = config.get('smtp.server', 'localhost')
    smtp_user = config.get('smtp.user')
    smtp_password = config.get('smtp.password')
    smtp_connection.connect(smtp_server)
    try:
        smtp_connection.ehlo()
        if smtp_user:
            assert smtp_password, "If smtp.user is configured then smtp.password must be configured as well."
            smtp_connection.login(smtp_user, smtp_password)
        smtp_connection.sendmail(config.get('smtp.mail_from'), [recipient_email], msg.as_string())
    except smtplib.SMTPException, e:
        msg = '%r' % e
        raise MailerException(msg)
    finally:
        smtp_connection.quit()
