from subprocess import call, check_call
from os import mkdir
from shutil import copy, copytree, rmtree
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
    # yaourt_packages = ['yaourt-git']
    apricity_packages = ['apricityassets', 'apricity-vim', 'ice-ssb',
                         'calamares', 'apricity-wallpapers',
                         'apricity-themes-gnome', 'apricity-themes-cinnamon',
                         'apricity-icons', 'apricity-keyring']
    # apricity_packages = ['apricityassets']
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


def clean():
    try:
        call(['chmod', '-R', '755', 'build'])
        rmtree('build')
    except Exception as e:
        print(e)
    try:
        rmtree('core-backup')
    except Exception as e:
        print(e)
    try:
        copytree('core', 'core-backup')
        call(['chmod', '-R', '755', 'core'])
        rmtree('core')
    except Exception as e:
        print(e)


def sync_core(signed=False, max_attempts=10):
    if signed:
        dest = 'apricity-core-signed'
    else:
        dest = 'apricity-core'
    attempts = 0
    while attempts < max_attempts:
        try:
            check_call('rsync -aP --exclude="apricity-core*" --checksum core/ \
                       apricity@apricityos.com:public_html/' + dest, shell=True)
            break
        except:
            attempts += 1
    attempts = 0
    while attempts < max_attempts:
        try:
            check_call('rsync -aP core/apricity-core.db.tar.gz* --ignore-times \
                       core/apricity-core.db* \
                       core/apricity-core.files* \
                       core/apricity-core.files.tar.gz* \
                       apricity@apricityos.com:public_html/' + dest,
                       shell=True)
            break
        except:
            attempts += 1


def prepare(build_dir, repo_dir, max_attempts=10):
    mkdir(build_dir)
    mkdir(repo_dir)
    attempts = 0
    while attempts < max_attempts:
        try:
            check_call('rsync -aP \
                       apricity@apricityos.com:public_html/apricity-core/apricity-core.db.tar.gz \
                       apricity@apricityos.com:public_html/apricity-core/apricity-core.db \
                       apricity@apricityos.com:public_html/apricity-core/apricity-core.files.tar.gz \
                       apricity@apricityos.com:public_html/apricity-core/apricity-core.files \
                       core',
                       shell=True)
            break
        except:
            attempts += 1


def build_core(packages, install_makedeps=True, verbose=True, max_attempts=10, signed=False):
    build_dir = 'build'
    repo_dir = 'core'
    prepare(build_dir, repo_dir)
    failed = []
    for package in packages:
        attempts = 0
        while attempts < max_attempts:
            try:
                if install_makedeps:
                    package.install_makedeps(verbose=verbose)
                package.build(build_dir, verbose=verbose, signed=signed)
                pkgs = glob(build_dir + '/' + package.name + '/*.pkg.tar.xz')
                if len(pkgs) > 0:
                    for file in pkgs:
                        copy(file, repo_dir)
                else:
                    raise Exception('Makepkg failed')
                if signed:
	            sigs = glob(build_dir + '/' + package.name + '/*.pkg.tar.xz.sig')
	            if len(sigs) > 0:
	                for file in pkgs:
	                    copy(file, repo_dir)
	            else:
	                raise Exception('Makepkg signing failed')
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
        if signed:
            call('repo-add --sign apricity-core.db.tar.gz *.pkg.tar.xz', shell=True)
        else:
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
    parser.add_argument('-s', '--signed',
                        help='sign packages',
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
        clean()
        packages = get_packages(yaourt_spot_fix=args.aur_spot_fix,
                                apricity_spot_fix=args.apricity_spot_fix)
        failed_packages = build_core(packages,
                                     install_makedeps=args.install_makedeps,
                                     verbose=args.verbose,
                                     signed=args.signed)
        sync_core(args.signed)
        if len(failed_packages) > 0:
            print('Failed packages:')
            for package_name in failed_packages:
                print(package_name)


if __name__ == '__main__':
    main()
