
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

$env:Path = "$env:USERPROFILE\.local\bin;$env:Path"

git clone https://forgejo.iamnotgerman.de/root/ocr_scanner.git

cd ocr_scanner

uv sync

