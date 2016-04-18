from lib import cd, make_tarfile
from subprocess import call
from glob import glob


class YaourtPackage():
    def __init__(self, pkg):
        self.pkg = pkg

    def build(self, build):
        with cd(build):
            call('yaourt -G ' + self.pkg, shell=True)
            with cd(self.pkg):
                call('makepkg', shell=True)


class ApricityPackage():
    def __init__(self, pkg):
        self.pkg = pkg

    def build(self, build):
        with cd(build):
            call('git clone ' + 'https://github.com/Apricity-OS/' + self.pkg + '.git', shell=True)
            with cd(self.pkg):
                make_tarfile(self.pkg + '.tar.gz', 'src/' + self.pkg)
                call('makepkg')
