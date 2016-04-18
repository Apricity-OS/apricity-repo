from subprocess import call
from os import mkdir
from shutil import copy, rmtree
from glob import glob
from lib import cd, make_tarfile
from packages import YaourtPackage, ApricityPackage


def get_packages():
    yaourt_packages = ['broadcom-wl', 'broadcom-wl-dkms', 'btsync',
                       'btsync-gui', 'cower', 'expac-git',
                       'firefox-extension-shumway', 'google-chrome',
                       'google-talkplugin', 'gst-plugin-libde265',
                       'kpmcore-git', 'libde265', 'libtimezonemap',
                       'nightingale-git', 'otter-browser', 'pacaur',
                       'package-query-git', 'palemoon-bin', 'atom-editor',
                       'pamac-aur', 'pam_encfs', 'pipelight', 'plymouth',
                       'polkit-gnome-gtk2', 'pyparted-git',
                       'python2-powerline-git', 'python-beautifulsoup4',
                       'python-parted', 'sbackup', 'telegram-desktop-bin',
                       'ttf-ms-fonts', 'v86d', 'vte3-notification',
                       'vte3-notification-common', 'wine', 'wine-silverlight',
                       'yaourt-git']
    yaourt_packages_truncated = ['pyparted-git']
    # yaourt_packages = yaourt_packages_truncated
    apricity_packages = ['apricityassets', 'apricity-vim', 'ice-ssb',
                         'calamares', 'apricity-wallpapers'
                         'apricity-themes-gnome', 'apricity-themes-cinnamon',
                         'apricity-icons', 'apricity-chrome-profile']
    apricity_packages_truncated = ['ice-ssb']
    # apricity_packages = apricity_packages_truncated
    packages = []
    for package_name in yaourt_packages:
        packages.append(YaourtPackage(package_name))
    for package_name in apricity_packages:
        packages.append(ApricityPackage(package_name))
    return packages


def clean():
    try:
        rmtree('build')
        rmtree('repo')
    except Exception as e:
        print(e)


def build_core(packages):
    mkdir('build')
    mkdir('repo')
    for package in packages:
        package.build('build')
        pkgs = glob('build/' + package.pkg + '/' '*.pkg.tar.xz')
        if len(pkgs) > 0:
            for file in pkgs:
                copy(file, 'repo')
        else raise Exception('Makepkg failed')
    with cd('repo'):
        call('repo-add apricity-core.db.tar.gz *.pkg.tar.xz', shell=True)


def main():
    with cd('~/Apricity-OS/apricity-repo'):
        clean()
        packages = get_packages()
        build_core(packages)


if __name__ == '__main__':
    main()
