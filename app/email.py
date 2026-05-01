from threading import Thread
from flask import current_app, render_template, Flask
from flask_mail import Message
from . import mail


def send_async_email(app: Flask, msg: Message) -> None:
    with app.app_context():
        mail.send(msg)


def send_email(to: str, subject: str, template: str, **kwargs) -> Thread:
    app: Flask = current_app._get_current_object()

    msg: Message = Message(
        f"{app.config['FLASKY_MAIL_SUBJECT_PREFIX']} {subject}",
        sender=app.config["FLASKY_MAIL_SENDER"],
        recipients=[to]
    )

    msg.body = render_template(f"{template}.txt", **kwargs)
    msg.html = render_template(f"{template}.html", **kwargs)

    thr: Thread = Thread(target=send_async_email, args=[app, msg], name="email-sender")
    thr.start()

    return thr
