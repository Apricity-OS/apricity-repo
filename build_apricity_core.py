from subprocess import call, CalledProcessError
from os import mkdir
from shutil import copy, rmtree
from glob import glob
from lib import cd
from packages import YaourtPackage, ApricityPackage
from argparse import ArgumentParser


def get_packages():
    yaourt_packages = ['broadcom-wl', 'broadcom-wl-dkms', 'btsync',
                       'btsync-gui', 'cower', 'expac-git',
                       'firefox-extension-shumway', 'google-chrome',
                       'google-talkplugin', 'gst-plugin-libde265',
                       'kpmcore-git', 'libde265', 'libtimezonemap',
                       'otter-browser', 'pacaur',
                       'package-query-git', 'palemoon-bin', 'atom-editor',
                       'pamac-aur', 'pam_encfs', 'plymouth',
                       'polkit-gnome-gtk2', 'pyparted-git',
                       'python2-powerline-git', 'python-beautifulsoup4',
                       'sbackup', 'telegram-desktop-bin',
                       'ttf-ms-fonts', 'v86d',  # 'vte3-notification',
                       'wine', 'wine-silverlight',
                       'yaourt-git']
    apricity_packages = ['apricityassets', 'apricity-vim', 'ice-ssb',
                         'calamares', 'apricity-wallpapers',
                         'apricity-themes-gnome', 'apricity-themes-cinnamon',
                         'apricity-icons', 'apricity-chrome-profile']
    packages = []
    for package_name in yaourt_packages:
        packages.append(YaourtPackage(package_name))
    for package_name in apricity_packages:
        packages.append(ApricityPackage(package_name))
    return packages


def clean():
    try:
        rmtree('build')
    except Exception as e:
        print(e)
    try:
        rmtree('core')
    except Exception as e:
        print(e)


def sync_core():
    call(['rsync', '-aP', 'core', 'apricity@apricityos.com/public_html/apricity-core'])


def build_core(packages, install_makedeps=True, verbose=True, max_attempts=5):
    build_dir = 'build'
    repo_dir = 'core'
    mkdir(build_dir)
    mkdir(repo_dir)
    failed = []
    for package in packages:
        attempts = 0
        while attempts < max_attempts:
            try:
                if install_makedeps:
                    package.install_makedeps(verbose=verbose)
                package.build(build_dir, verbose=verbose)
                pkgs = glob(build_dir + '/' + package.name + '/*.pkg.tar.xz')
                if len(pkgs) > 0:
                    for file in pkgs:
                        copy(file, repo_dir)
                else:
                    raise Exception('Makepkg failed')
                break
            except Exception as e:
                print('Unexpected Error:' + str(e))
                attempts += 1
                if attempts < max_attempts:
                    print('Trying again...')
                    rmtree('build/' + package.name, ignore_errors=True)
                else:
                    failed.append(package.name)
    with cd(repo_dir):
        call('repo-add apricity-core.db.tar.gz *.pkg.tar.xz', shell=True)
    return failed


def get_args():
    parser = ArgumentParser()
    parser.add_argument('-m', '--install_makedeps',
                        help='install make dependencies',
                        action='store_true')
    parser.add_argument('-v', '--verbose',
                        help='increase verbosity',
                        action='store_true')
    args = parser.parse_args()
    return args


def main():
    args = get_args()
    print('Verbosity: ' + str(args.verbose))
    with cd('~/Apricity-OS/apricity-repo'):
        clean()
        packages = get_packages()
        failed_packages = build_core(packages,
                                     install_makedeps=args.install_makedeps,
                                     verbose=args.verbose)
        sync_core()
        if len(failed_packages) > 0:
            print('Failed packages:')
            for package_name in failed_packages:
                print(package_name)


if __name__ == '__main__':
    main()
