

mkdir python

pip3 install -r daftar_common/requirements.txt -t python/

cp -r daftar_common python
zip -r daftar_common.zip python

aws lambda publish-layer-version --layer-name daftar_common \
    --description "Common methods" \
    --zip-file "fileb://$(pwd)/daftar_common.zip"\
    --compatible-runtimes python3.10 \
    --compatible-architectures "x86_64" \
    --profile daftar

rm -rf python
rm daftar_common.zip