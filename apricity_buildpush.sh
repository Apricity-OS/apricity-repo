package_name=apricityassets
repo_name=apricity-core
repo_endpoint=apricity-core-signed
dev=""

while getopts 'P:R:E:dh' arg; do
    case "${arg}" in
        P) package_name="${OPTARG}" ;;
        R) repo_name="${OPTARG}" ;;
        E) repo_endpoint="${OPTARG}" ;;
        d) dev="-dev" ;;
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
makepkg -s --sign --clean --noconfirm 2>&1 | tee ${package_name}.log

wget static.apricityos.com/${repo_endpoint}/${repo_name}.db
wget static.apricityos.com/${repo_endpoint}/${repo_name}.db.tar.gz
wget static.apricityos.com/${repo_endpoint}/${repo_name}.files
wget static.apricityos.com/${repo_endpoint}/${repo_name}.files.tar.gz

repo-add --sign ${repo_name}.db.tar.gz ${package_name}*.pkg.tar.xz

scp ${repo_name}.db* ${repo_name}.files* ${package_name}*.pkg.tar.xz server@static.apricityos.com:/mnt/static/public_html/${repo_endpoint}/
scp ${package_name}.log server@static.apricityos.com:/mnt/static/public_html/${repo_endpoint}/

cd ../../..
rm -rf build
