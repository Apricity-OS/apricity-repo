package_name=google-talkplugin
repo_name=apricity-core
repo_endpoint=apricity-core-signed

while getopts 'P:sdh' arg; do
    case "${arg}" in
        P) package_name="${OPTARG}" ;;
        s) repo_name="apricity-core" repo_endpoint="apricity-core-signed" ;;
        d) repo_name="apricity-core-dev" repo_endpoint="apricity-core-dev" ;;
        *)
           echo "Invalid argument '${arg}'" ;;
    esac
done

mkdir -p ~/chroot32
CHROOT=$HOME/chroot32
mkarchroot -C pacman_i686.conf -M makepkg_i686.conf $CHROOT/root base-devel
arch-nspawn $CHROOT/root pacman -Syu

rm -rf build
mkdir -p build
cd build
yaourt -G ${package_name}
cd ${package_name}
sudo pacman -Syy
# makepkg -sr --sign --clean --needed --noconfirm 2>&1 | tee ${package_name}.log
makechrootpkg -cr $CHROOT -- -s --clean --needed --noconfirm 2>&1 | tee ${package_name}.log

target_dts=$(date -d "$(stat -c %Y $file | awk '{print strftime("%c",$1)}')" +%Y%m%d%H%M.%S)
for pkg_fnm in *.pkg.tar.xz
do
    gpg --detach-sign "${pkg_fnm}"
    touch -t "${target_dts}" "${pkg_fnm}.sig"
done

wget static.apricityos.com/${repo_endpoint}/${repo_name}.db
wget static.apricityos.com/${repo_endpoint}/${repo_name}.db.tar.gz
wget static.apricityos.com/${repo_endpoint}/${repo_name}.files
wget static.apricityos.com/${repo_endpoint}/${repo_name}.files.tar.gz

repo-add --sign ${repo_name}.db.tar.gz *.pkg.tar.xz

scp ${repo_name}.db* server@static.apricityos.com:/mnt/repo/public_html/${repo_endpoint}/
scp ${repo_name}.files* server@static.apricityos.com:/mnt/repo/public_html/${repo_endpoint}/
scp ./*.pkg.tar.xz server@static.apricityos.com:/mnt/repo/public_html/${repo_endpoint}/
scp ./*.pkg.tar.xz.sig server@static.apricityos.com:/mnt/repo/public_html/${repo_endpoint}/
scp ${package_name}.log server@static.apricityos.com:/mnt/repo/public_html/${repo_endpoint}/

cd ../../..
rm -rf build
