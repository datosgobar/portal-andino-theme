# coding=utf-8
import re
import smtplib
from datetime import datetime
from email import utils
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from socket import error as socket_error
from subprocess import check_output
from time import time, sleep

import ckan
import ckan.lib.mailer as ckan_mailer
import paste.deploy.converters
from pylons import config

import ckanext.gobar_theme.helpers as gobar_helpers

MailerException = ckan_mailer.MailerException

andino_address = config.get('smtp.mail_from')

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
    if user.fullname:
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
    if not user.email:
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

Tu usuario es: {login_username}

Para que confirmar tu registro, necesitamos que cambies tu contraseña. También vas a poder cambiar tu e-mail si lo necesitás. 

{reset_link}
 
¡Suerte y a abrir datos!
 
El equipo de {site_title}.

"""

new_user_html_body = u"""
¡Hola, {username}!<br>
<br>
{admin_username} te invitó a colaborar en {site_title}.<br>
<br>
Tu usuario es: {login_username}<br>
<br>
Para que confirmar tu registro, <strong>necesitamos que cambies tu contraseña.</strong> También vas a poder cambiar tu e-mail si lo necesitás.<br> 
<br>
<a href="{reset_link}" target="_blank">Confirmar y cambiar contraseña</a><br>
 <br>
¡Suerte y a abrir datos!<br>
 <br>
El equipo de {site_title}.<br>
<br>
"""


def new_user_content(admin_user, new_user):
    if new_user.fullname:
        username = new_user.fullname
    else:
        username = new_user.name
    if admin_user.fullname:
        admin_username = admin_user.fullname
    else:
        admin_username = admin_user.name
    login_username = new_user.name
    reset_link = ckan_mailer.get_reset_link(new_user)
    site_title = gobar_helpers.get_theme_config('title.site-title', 'Portal Andino')
    plain_body = new_user_plain_body.format(admin_username=admin_username,
                                            username=username,
                                            reset_link=reset_link,
                                            site_title=site_title,
                                            login_username=login_username)
    html_body = new_user_html_body.format(admin_username=admin_username,
                                          username=username,
                                          reset_link=reset_link,
                                          site_title=site_title,
                                          login_username=login_username)
    subject = new_user_subject.format(admin_username=admin_username)
    return subject, plain_body, html_body


def send_new_user_mail(admin_user, new_user):
    ckan_mailer.create_reset_key(new_user)
    subject, plain_body, html_body = new_user_content(admin_user, new_user)
    recipient_name = new_user.display_name
    recipient_email = new_user.email
    msg = assemble_email(plain_body, html_body, subject, recipient_name, recipient_email)
    return send_mail(msg, recipient_email)


def send_test_mail(admin_user):
    current_time = datetime.now().strftime("%H:%M:%S")
    plain_body = html_body = u'Ésta es una prueba de envío de mail. Hora de envío: {}.'.format(current_time)
    subject = \
        u'Prueba de envío de mail - {}'.format(gobar_helpers.get_theme_config('title.site-title', 'Portal Andino'))
    msg = assemble_email(plain_body, html_body, subject, admin_user.display_name, admin_user.email)
    try:
        return_value = send_mail(msg, admin_user.email)
    except Exception as e:
        return_value = {'error': e.message}

    if gobar_helpers.search_for_value_in_config_file('smtp.server') == 'postfix':
        sleep(5)  # Le damos tiempo a postfix para loguear
        return_value['log'] = get_postfix_log()
        issue = search_for_last_postfix_log_issue(return_value['log'], admin_user.email)
        if issue:
            return_value['error'] = \
                '{0}{1}'.format('{} | '.format(return_value.get('error')) if return_value.get('error') else '', issue)
    return return_value


def assemble_email(msg_plain_body, msg_html_body, msg_subject, recipient_name, recipient_email):
    text_msg = MIMEText(msg_plain_body, 'plain', 'UTF-8')
    html_msg = MIMEText(msg_html_body, 'html', 'UTF-8')
    msg = MIMEMultipart('alternative')
    msg.attach(text_msg)
    msg.attach(html_msg)
    msg['Subject'] = Header(msg_subject.encode('utf-8'), 'utf-8')
    msg['From'] = andino_address
    recipient = u"%s <%s>" % (recipient_name, recipient_email)
    msg['To'] = Header(recipient, 'utf-8')
    msg['Date'] = utils.formatdate(time())
    msg['X-Mailer'] = "CKAN %s" % ckan.__version__
    return msg


def send_mail(msg, recipient_email):
    smtp_connection = smtplib.SMTP()
    smtp_server = config.get('smtp.server', 'localhost')
    smtp_starttls = paste.deploy.converters.asbool(
        config.get('smtp.starttls'))
    smtp_user = config.get('smtp.user')
    smtp_password = config.get('smtp.password')
    return_value = {'success': False}
    try:
        smtp_connection.connect(smtp_server)
    except socket_error, e:
        return_value['error'] = str(e)
        return return_value
    try:
        smtp_connection.ehlo()
        if smtp_starttls:
            smtp_connection.starttls()
        if smtp_user:
            assert smtp_password, "If smtp.user is configured then smtp.password must be configured as well."
            smtp_connection.login(smtp_user, smtp_password)
        smtp_connection.sendmail(andino_address, [recipient_email], msg.as_string())
        return_value['success'] = True
    except smtplib.SMTPException, e:
        return_value['error'] = str(e)
    finally:
        smtp_connection.quit()
    return return_value


def get_postfix_log():
    postfix_mail_log_path = '/var/log/shared/postfix/mail.log'
    cmd = 'tail -n 10 {} || true'.format(postfix_mail_log_path)
    log = check_output(cmd, shell=True).strip()
    log = re.sub(r'\n', '\n\n', log)
    return log


def search_for_last_postfix_log_issue(log, email):
    for line in reversed(log.split('\n\n')):
        if email in line and ('status=deferred' in line or 'status=bounced' in line):
            return line
    return ''
