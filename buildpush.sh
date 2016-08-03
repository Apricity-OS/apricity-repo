package_name=google-talkplugin
repo_name=apricity-core
repo_endpoint=apricity-core-signed

while getopts 'P:R:E:h' arg; do
    case "${arg}" in
        P) package_name="${OPTARG}" ;;
        R) repo_name="${OPTARG}" ;;
        E) repo_endpoint="${OPTARG}" ;;
        *)
           echo "Invalid argument '${arg}'" ;;
    esac
done

rm -rf build
mkdir -p build
cd build
yaourt -G ${package_name}
cd ${package_name}
sudo pacman -Syy
makepkg -sr --sign --clean --needed --noconfirm 2>&1 | tee ${package_name}.log

wget static.apricityos.com/${repo_endpoint}/${repo_name}.db
wget static.apricityos.com/${repo_endpoint}/${repo_name}.db.tar.gz
wget static.apricityos.com/${repo_endpoint}/${repo_name}.files
wget static.apricityos.com/${repo_endpoint}/${repo_name}.files.tar.gz

repo-add --sign ${repo_name}.db.tar.gz *.pkg.tar.xz

scp ${repo_name}.db* server@static.apricityos.com:/mnt/static/public_html/${repo_endpoint}/
scp ${repo_name}.files* server@static.apricityos.com:/mnt/static/public_html/${repo_endpoint}/
scp ./*.pkg.tar.xz server@static.apricityos.com:/mnt/static/public_html/${repo_endpoint}/
scp ./*.pkg.tar.xz.sig server@static.apricityos.com:/mnt/static/public_html/${repo_endpoint}/
scp ${package_name}.log server@static.apricityos.com:/mnt/static/public_html/${repo_endpoint}/

cd ../..
rm -rf build
