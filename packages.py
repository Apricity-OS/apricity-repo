from lib import cd
from subprocess import call
from os import devnull, mkdir
from shutil import copytree, rmtree


class YaourtPackage():
    def __init__(self, name):
        self.name = name

    def build(self, build, verbose=True, signed=False, dev=False):
        if signed:
            sign_str = '--sign'
        else:
            sign_str = '--nosign'
        with cd(build):
            if verbose:
                call(['yaourt', '-G', self.name])
            else:
                call(['yaourt', '-G', self.name], stdout=open(devnull, 'w'))
            with cd(self.name):
                if verbose:
                    call(['makepkg', sign_str, '--syncdeps'])
                else:
                    call(['makepkg', sign_str, '--syncdeps'], stdout=open(devnull, 'w'))

    def install_makedeps(self, verbose=True):
        if verbose:
            call(['pacaur', '-ay', '--noedit', '--noconfirm', '--needed', self.name])
        else:
            call(['pacaur', '-ay', '--noedit', '--silent', '--noconfirm', '--needed', self.name], stdout=open(devnull, 'w'))


class ApricityPackage():
    def __init__(self, name):
        self.name = name

    def build(self, build, verbose=True, signed=False, dev=False):
        if signed:
            sign_str = '--sign'
        else:
            sign_str = '--nosign'
        if dev:
            dev_str = '-dev'
        else:
            dev_str = ''
        with cd(build):
            mkdir(self.name + '-clone')
            with cd(self.name + '-clone'):
                call(['git', 'clone', 'https://github.com/Apricity-OS/apricity-packages' + dev_str])
                copytree('apricity-packages' + dev_str + '/' + self.name, '../' + self.name)
            rmtree(self.name + '-clone')
            with cd(self.name):
                if verbose:
                    call(['makepkg', sign_str, '--syncdeps'])
                else:
                    call(['makepkg', sign_str, '--syncdeps'], stdout=open(devnull, 'w'))

    def install_makedeps(self, verbose=True):
        pass
