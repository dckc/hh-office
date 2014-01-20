
def main(argv, environ, mkBrowser):
    username, passwd_key = argv[1:3]
    ua = mkBrowser()
    login(ua, username, environ[passwd_key])


def login(ua, username, password,
          panel='https://panel.dreamhost.com/'):
    ua.open(panel)
    ua.select_form(nr=0)  # panelLoginForm
    ua['username'] = username
    ua['password'] = password
    ans = ua.submit()
    import pdb; pdb.set_trace()


if __name__ == '__main__':
    def _with_caps():
        from sys import argv
        from os import environ
        from mechanize import Browser

        main(argv=argv,
             environ=environ,
             mkBrowser=lambda: Browser(),
             )

    _with_caps()
