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

repo-add --sign ${repo_name}.db.tar.gz ${package_name}*.pkg.tar.xz

scp ${repo_name}.db* server@static.apricityos.com:/mnt/static/public_html/${repo_endpoint}/
scp ${repo_name}.files* server@static.apricityos.com:/mnt/static/public_html/${repo_endpoint}/
scp ${package_name}*.pkg.tar.xz server@static.apricityos.com:/mnt/static/public_html/${repo_endpoint}/
scp ${package_name}.log server@static.apricityos.com:/mnt/static/public_html/${repo_endpoint}/

cd ../..
rm -rf build
