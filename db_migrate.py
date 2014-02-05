import logging

log = logging.getLogger(__name__)


def main(argv, arg_wr, environ, mkBrowser):
    panel_user, passwd_key, db, db_user, out = argv[1:6]

    ua = mkBrowser()

    password = environ[passwd_key]
    login(ua, panel_user, password)

    admin_db(ua, db, db_user, password)
    db_export(ua, out=arg_wr(out))


def db_export(ua, out,
              structure=True, data=False,
              compression='zip'):
    log.info('Content frame...')
    ua.follow_link(
        predicate=lambda e: (e.tag == 'frame'
                             and ('id', 'frame_content') in e.attrs))
    log.info('to Export...')
    ua.follow_link(text='[IMG]Export')

    ua.select_form(nr=0)

    for name, val in [('sql_structure', structure),
                      ('sql_data', data)]:
        ua.find_control(name).items[0].selected = val

    ua.find_control('asfile').items[0].selected = True
    ua['compression'] = [compression]

    log.info('Export! structure? %s data? %s', structure, data)
    ans = ua.submit()
    out.write(ans.read())


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

        def arg_wr(n):
            if n not in argv:
                raise IOError
            else:
                return open(n, 'w')

        main(argv=argv,
             environ=environ,
             arg_wr=arg_wr,
             mkBrowser=lambda: Browser(),
             )

    _configure_logging()
    _with_caps()
