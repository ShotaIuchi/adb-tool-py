./.tool_build_doc.sh

tempdir=$(mktemp -d)
echo "Temporary directory created at: $tempdir"

cp -a ./doc/build/html/* $tempdir
ls -al $tempdir

git switch gh-pages

rm -rf *
cp -a $tempdir/* ./

git add --all
git commit -m update

git switch -

git push origin gh-pages:gh-pages

trap 'rm -rf "$tempdir"' EXIT

