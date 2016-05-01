from subprocess import call, check_call
from os import mkdir
from shutil import copy, rmtree
from glob import glob
from lib import cd
from packages import YaourtPackage, ApricityPackage
from argparse import ArgumentParser


def get_packages(yaourt_spot_fix='', apricity_spot_fix=''):
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
                       # 'wine', 'wine-silverlight',
                       'yaourt-git']
    # yaourt_packages = ['broadcom-wl-dkms', 'kpmcore-git', 'google-chrome', 'pamac-aur', 'yaourt-git', 'python2-powerline-git']
    apricity_packages = ['apricityassets', 'apricity-vim', 'ice-ssb',
                         'calamares', 'apricity-wallpapers',
                         'apricity-themes-gnome', 'apricity-themes-cinnamon',
                         'apricity-icons', 'apricity-keyring']
    # apricity_packages = ['calamares']
    if len(yaourt_spot_fix) > 0 and len(apricity_spot_fix) == 0:
        yaourt_packages = [yaourt_spot_fix]
        apricity_packages = []
    elif len(yaourt_spot_fix) == 0 and len(apricity_spot_fix) > 0:
        apricity_packages = [apricity_spot_fix]
        yaourt_packages = []
    elif len(yaourt_spot_fix) > 0 and len(apricity_spot_fix) > 0:
        apricity_packages = [apricity_spot_fix]
        yaourt_packages = [yaourt_spot_fix]
    packages = []
    for package_name in yaourt_packages:
        packages.append(YaourtPackage(package_name))
    for package_name in apricity_packages:
        packages.append(ApricityPackage(package_name))
    return packages


def clean(folders):
    for folder in folders:
        try:
            call(['chmod', '-R', '755', folder])
            rmtree(folder)
        except Exception as e:
            print(e)


def sync_repo(repo_name, repo_dir, dest, max_attempts=10):
    attempts = 0
    while attempts < max_attempts:
        try:
            check_call('rsync -aP --exclude="apricity-core*" --checksum ' + repo_dir + '/ \
                       apricity@apricityos.com:public_html/' + dest, shell=True)
            break
        except:
            attempts += 1
    attempts = 0
    while attempts < max_attempts:
        try:
            check_call('rsync -aP --ignore-times ' + repo_dir + '/' + repo_name + '.db* ' +
                       repo_dir + '/' + repo_name + '.files* \
                       apricity@apricityos.com:public_html/' + dest,
                       shell=True)
            break
        except:
            attempts += 1


def sync_core_nonsigned():
    sync_repo('apricity-core', 'core', 'apricity-core')


def sync_core_signed():
    sync_repo('apricity-core', 'core-signed', 'apricity-core-signed')


def sync_core_dev():
    sync_repo('apricity-core-dev', 'core-dev', 'apricity-core-dev')


def prepare(dest_dir, repo_name, build_dir, repo_dir, max_attempts=10):
    clean([build_dir, repo_dir])
    mkdir(build_dir)
    mkdir(repo_dir)
    attempts = 0
    while attempts < max_attempts:
        try:
            check_call('rsync -aP \
                       apricity@apricityos.com:public_html/' + dest_dir + '/' + repo_name + '.db* \
                       apricity@apricityos.com:public_html/' + dest_dir + '/' + repo_name + '.files* ' +
                       repo_dir,
                       shell=True)
            break
        except:
            attempts += 1


def build_repo(packages, install_makedeps=True, max_attempts=10, signed=False, dest_dir='apricity-core', repo_name='apricity-core', build_dir='build', repo_dir='repo', dev=False):
    prepare(dest_dir, repo_name, build_dir, repo_dir)
    failed = []
    for package in packages:
        attempts = 0
        while attempts < max_attempts:
            try:
                if install_makedeps:
                    package.install_makedeps(verbose=True)
                package.build(build_dir, verbose=True, signed=signed, dev=dev)
                pkgs = glob(build_dir + '/' + package.name + '/*.pkg.tar.xz')
                if len(pkgs) > 0:
                    for file in pkgs:
                        copy(file, repo_dir)
                else:
                    raise Exception('Makepkg failed')
                if signed:
                    sigs = glob(build_dir + '/' + package.name + '/*.pkg.tar.xz.sig')
                    if len(sigs) > 0:
                        for file in sigs:
                            copy(file, repo_dir)
                    else:
                        raise Exception('Makepkg signing failed')
                break
            except Exception as e:
                print('Unexpected Error:' + str(e))
                attempts += 1
                if attempts < max_attempts:
                    print('Trying again...')
                    rmtree(build_dir + '/' + package.name, ignore_errors=True)
                else:
                    failed.append(package.name)
    with cd(repo_dir):
        if signed:
            call('repo-add --sign ' + repo_name + '.db.tar.gz *.pkg.tar.xz', shell=True)
        else:
            call('repo-add ' + repo_name + '.db.tar.gz *.pkg.tar.xz', shell=True)
    return failed


def build_core_nonsigned(packages, install_makedeps):
    return build_repo(packages, install_makedeps=install_makedeps, signed=False, dest_dir='apricity-core', repo_name='apricity-core', build_dir='build', repo_dir='core')


def build_core_signed(packages, install_makedeps):
    return build_repo(packages, install_makedeps=install_makedeps, signed=True, dest_dir='apricity-core-signed', repo_name='apricity-core', build_dir='build-signed', repo_dir='core-signed')


def build_core_dev(packages, install_makedeps):
    return build_repo(packages, install_makedeps=install_makedeps, signed=True, dest_dir='apricity-core-dev', repo_name='apricity-core-dev', build_dir='build-dev', repo_dir='core-dev', dev=True)


def get_args():
    parser = ArgumentParser()
    parser.add_argument('-m', '--install_makedeps',
                        help='install make dependencies',
                        action='store_true')
    parser.add_argument('-v', '--verbose',
                        help='increase verbosity',
                        action='store_true')
    parser.add_argument('-s', '--signed',
                        help='build apricity-core-signed',
                        action='store_true')
    parser.add_argument('-n', '--nonsigned',
                        help='build apricity-core',
                        action='store_true')
    parser.add_argument('-d', '--dev',
                        help='build apricity-dev',
                        action='store_true')
    parser.add_argument('-a', '--apricity_spot_fix',
                        default='',
                        help='only update a single apricity package')
    parser.add_argument('-y', '--aur_spot_fix',
                        default='',
                        help='only update a single AUR package')
    args = parser.parse_args()
    return args


def main():
    args = get_args()
    print('Verbosity: ' + str(args.verbose))
    with cd('~/Apricity-OS/apricity-repo'):
        packages = get_packages(yaourt_spot_fix=args.aur_spot_fix,
                                apricity_spot_fix=args.apricity_spot_fix)
        failed_packages = []
        if args.nonsigned:
            failed_packages += build_core_nonsigned(packages, args.install_makedeps)
        if args.signed:
            failed_packages += build_core_signed(packages, args.install_makedeps)
        if args.dev:
            failed_packages += build_core_dev(packages, args.install_makedeps)
        if args.nonsigned:
            sync_core_nonsigned()
        if args.signed:
            sync_core_signed()
        if args.dev:
            sync_core_dev()
        if len(failed_packages) > 0:
            print('Failed packages:')
            for package_name in failed_packages:
                print(package_name)


if __name__ == '__main__':
    main()
