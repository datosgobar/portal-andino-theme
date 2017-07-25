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
from socket import error as socket_error
try:
    from socket import sslerror
except ImportError:
    sslerror = None
MailerException = ckan_mailer.MailerException

andino_address = 'no-reply@andino.datos.gob.ar'

reset_password_subject = u'Recuperemos tu contraseña de {site_title}'

reset_password_plain_body = u"""
¡Hola, {username}!

Parece que olvidaste tu contraseña. No te preocupes, vamos a cambiarla:

{reset_link}

¡Suerte!
El equipo de {site_title}.

"""

reset_password_html_body = u"""
¡Hola, {username}! <br>
<br>
<strong>Parece que olvidaste tu contraseña.</strong> No te preocupes, vamos a cambiarla: <br>
<br>
<a href="{reset_link}" target="_blank">Crear nueva contraseña</a> <br>
<br>
¡Suerte! <br>
El equipo de {site_title}. <br>
"""


def reset_mail_content(user):
    if user.fullname and len(user.fullname) > 0:
        username = user.fullname
    else:
        username = user.name
    reset_link = ckan_mailer.get_reset_link(user)
    site_title = gobar_helpers.get_theme_config('title.site-title', 'Portal Andino')
    plain_body = reset_password_plain_body.format(username=username, reset_link=reset_link, site_title=site_title)
    html_body = reset_password_html_body.format(username=username, reset_link=reset_link, site_title=site_title)
    subject = reset_password_subject.format(site_title=site_title)
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


new_user_subject = u'{admin_username} te invitó a colaborar en el portal de datos.'

new_user_plain_body = u"""
¡Hola, {username}!

{admin_username} te invitó a colaborar en {site_title}.

Para que confirmar tu registro, <strong>necesitamos que cambies tu contraseña.</strong> También vas a poder cambiar tu e-mail si lo necesitás. 

{reset_link}
 
¡Suerte y a abrir datos!
 
El equipo de {site_title}.

"""

new_user_html_body = u"""
¡Hola, {username}!<br>
<br>
{admin_username} te invitó a colaborar en {site_title}.<br>
<br>
Para que confirmar tu registro, necesitamos que cambies tu contraseña. También vas a poder cambiar tu e-mail si lo necesitás.<br> 
<br>
<a href="{reset_link}" target="_blank">Confirmar y cambiar contraseña</a><br>
 <br>
¡Suerte y a abrir datos!<br>
 <br>
El equipo de {site_title}.<br>
<br>
"""


def new_user_content(admin_user, new_user):
    if new_user.fullname and len(new_user.fullname) > 0:
        username = new_user.fullname
    else:
        username = new_user.name
    if admin_user.fullname and len(admin_user.fullname) > 0:
        admin_username = admin_user.fullname
    else:
        admin_username = admin_user.name
    reset_link = ckan_mailer.get_reset_link(new_user)
    site_title = gobar_helpers.get_theme_config('title.site-title', 'Portal Andino')
    plain_body = new_user_plain_body.format(admin_username=admin_username, username=username, reset_link=reset_link, site_title=site_title)
    html_body = new_user_html_body.format(admin_username=admin_username, username=username, reset_link=reset_link, site_title=site_title)
    subject = new_user_subject.format(admin_username=admin_username)
    return subject, plain_body, html_body


def send_new_user_mail(admin_user, new_user):
    ckan_mailer.create_reset_key(new_user)
    subject, plain_body, html_body = new_user_content(admin_user, new_user)
    recipient_name = new_user.display_name
    recipient_email = new_user.email
    msg = assemble_email(plain_body, html_body, subject, recipient_name, recipient_email)
    return send_mail(msg, recipient_email)


def assemble_email(msg_plain_body, msg_html_body, msg_subject, recipient_name, recipient_email):
    text_msg = MIMEText(msg_plain_body, 'plain', 'UTF-8')
    html_msg = MIMEText(msg_html_body, 'html', 'UTF-8')
    msg = MIMEMultipart('alternative')
    msg.attach(text_msg)
    msg.attach(html_msg)
    msg['Subject'] = Header(msg_subject.encode('utf-8'), 'utf-8')
    site_title = gobar_helpers.get_theme_config('title.site-title', 'Portal Andino')
    msg['From'] = "%s <%s>" % (site_title, andino_address)
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
    try:
        smtp_connection.connect(smtp_server)
    except socket_error, e:
        return {'success': False, 'error': e}
    try:
        smtp_connection.ehlo()
        if smtp_user:
            assert smtp_password, "If smtp.user is configured then smtp.password must be configured as well."
            smtp_connection.login(smtp_user, smtp_password)
        smtp_connection.sendmail(andino_address, [recipient_email], msg.as_string())
        return {'success': True}
    except smtplib.SMTPException, e:
        return {'success': False, 'error': e}
    finally:
        smtp_connection.quit()
