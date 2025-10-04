from zipfile import ZipFile

with ZipFile("exploit.zip",  mode="r") as archive:
    archive.extractall(path="./")