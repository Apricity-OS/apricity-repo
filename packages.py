from lib import cd, make_tarfile
from subprocess import call
from os import devnull


class YaourtPackage():
    def __init__(self, name):
        self.name = name

    def build(self, build, verbose=True):
        with cd(build):
            if verbose:
                call(['yaourt', '-G', self.name])
            else:
                call(['yaourt', '-G', self.name], stdout=open(devnull, 'w'))
            with cd(self.name):
                if verbose:
                    call('makepkg')
                else:
                    call('makepkg', stdout=open(devnull, 'w'))

    def install_makedeps(self, verbose=True):
        if verbose:
            call(['yaourt', '-S', '--noconfirm', self.name])
        else:
            call(['yaourt', '-S', '--noconfirm', self.name], stdout=open(devnull, 'w'))


class ApricityPackage():
    def __init__(self, name):
        self.name = name

    def build(self, build, verbose=True):
        with cd(build):
            call(['git', 'clone', 'https://github.com/Apricity-OS/' + self.name + '.git'])
            with cd(self.name):
                make_tarfile(self.name + '.tar.gz', 'src/' + self.name)
                if verbose:
                    call('makepkg')
                else:
                    call('makepkg', stdout=open(devnull, 'w'))

    def install_makedeps(self, verbose=True):
        pass
