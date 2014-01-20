import logging

log = logging.getLogger(__name__)


def main(argv, environ, mkBrowser):
    panel_user, passwd_key, db, db_user = argv[1:5]

    ua = mkBrowser()

    password = environ[passwd_key]
    login(ua, panel_user, password)

    admin_db(ua, db, db_user, password)


def admin_db(ua, db, db_user, password,
             admin='http://%s.dreamhosters.com/'):
    log.info('MySQL Databases...')
    ua.follow_link(text='MySQL Databases')
    ua.add_password(admin % db, db_user, password)
    log.info('phpMyAdmin...')
    return ua.follow_link(text='phpMyAdmin')


def login(ua, username, password,
          panel='https://panel.dreamhost.com/'):
    log.info('login: visit %s', panel)
    ua.open(panel)
    ua.select_form(nr=0)  # panelLoginForm
    ua['username'] = username
    ua['password'] = password
    log.info('log in as: %s', username)
    return ua.submit()


if __name__ == '__main__':
    def _configure_logging(level=logging.DEBUG):
        logging.basicConfig(level=level)

    def _with_caps():
        from sys import argv
        from os import environ
        from mechanize import Browser

        main(argv=argv,
             environ=environ,
             mkBrowser=lambda: Browser(),
             )

    _configure_logging()
    _with_caps()
