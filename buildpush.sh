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
makepkg -s --sign --clean 2>&1 | tee ${package_name}.log

wget 192.241.147.116/${repo_endpoint}/${repo_name}.db
wget 192.241.147.116/${repo_endpoint}/${repo_name}.db.tar.gz
wget 192.241.147.116/${repo_endpoint}/${repo_name}.files
wget 192.241.147.116/${repo_endpoint}/${repo_name}.files.tar.gz

repo-add --sign ${repo_name}.db.tar.gz ${package_name}*.pkg.tar.xz

scp ${repo_name}.db* ${repo_name}.files* ${package_name}*.pkg.tar.xz server@192.241.147.116:/mnt/static/public_html/${repo_endpoint}/
scp ${package_name}.log server@192.241.147.116:/mnt/static/public_html/${repo_endpoint}/

cd ../..
rm -rf build
