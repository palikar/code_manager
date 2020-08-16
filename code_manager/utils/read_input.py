import readline


readline.parse_and_bind('tab: complete')
readline.parse_and_bind('set editing-mode emacs')


YES_OPT = ['yes', 'y', 'ye']
NO_OPT = ['no', 'n']


def promt_yes_no(text, tries=5):
    for _ in range(tries):
        try:
            line = input(f'{text} [Yes/No]: ').lower()
        except KeyboardInterrupt:
            return False

        if line in YES_OPT:
            return True

        if line in NO_OPT:
            return False

    return False


def promt(text, default):
    line = input(f'{text} : (default: {default})  ').strip()
    if not line:
        return default
    return line
