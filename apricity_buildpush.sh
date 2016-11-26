package_name=apricityassets
repo_name=apricity-core
repo_endpoint=apricity-core-signed
dev=""

while getopts 'P:sdh' arg; do
    case "${arg}" in
        P) package_name="${OPTARG}" ;;
        s) dev="" repo_name="apricity-core" repo_endpoint="apricity-core-signed" ;;
        d) dev="-dev" repo_name="apricity-core-dev" repo_endpoint="apricity-core-dev" ;;
        *)
           echo "Invalid argument '${arg}'" ;;
    esac
done

rm -rf build
mkdir -p build
cd build
git clone https://github.com/Apricity-OS/apricity-packages${dev}
cd apricity-packages${dev}
cd ${package_name}
sudo pacman -Syu --noconfirm
makepkg -sr --sign --clean --needed --noconfirm 2>&1 | tee ${package_name}.log

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
