import httpx
from urllib3 import encode_multipart_formdata
import random
import hashlib
import filetype


def gen_file_md5(file_bytes):
  md5 = hashlib.md5()
  md5.update(file_bytes)
  return md5.hexdigest()

async def upload(image_path):
  if type(image_path) != bytes:
    file_bytes = open(image_path, 'rb').read()
  else:
    file_bytes = image_path
  url = "https://bbs-api.miyoushe.com/apihub/sapi/getUploadParams"

  param= {
    "ext":filetype.guess_extension(file_bytes),
    'md5': gen_file_md5(file_bytes),
    'support_content_type': '1',
    'upload_source': '2'
  }

  headers = {
    'x-rpc-verify_key': 'bll8iq97cem8',
    'Accept': '*/*',
    'x-rpc-client_type': '1',
    'x-rpc-channel': 'appstore',
    'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
    'x-rpc-sys_version': '15.7.1',
    'Referer': 'https://app.mihoyo.com',
    'x-rpc-device_name': '',
    'x-rpc-app_version': '2.51.1',
    'User-Agent': 'Hyperion/318 CFNetwork/1335.0.3 Darwin/21.6.0',
    'Connection': 'keep-alive',
    'Cookie': 'set you own cookie here',
  }

  async with httpx.AsyncClient(proxies={"all://":None},verify=False) as client:
    res = await client.get(url, headers=headers, params=param)

    data=res.json()["data"]

    url = "https://mihoyo-community-web.oss-cn-shanghai.aliyuncs.com/"

    headers = {
      'Connection': 'keep-alive',
      'Accept': '*/*',
      'User-Agent': 'Hyperion/318 CFNetwork/1335.0.3 Darwin/21.6.0',
      'Accept-Language': 'zh-CN,zh-Hans;q=0.9'
    }
    boundary = 'alamofire.boundary.'+"".join(random.choices('0123456789abcdef', k=16))
    data = [
        ('key', (data["file_name"])),
        ('policy', (data["params"]["policy"])),
        ('OSSAccessKeyId', (data["params"]["accessid"])),
        ('x:extra', (data["params"]["callback_var"]["x:extra"])),
        ('signature', (data["params"]["signature"])),
        ('callback', (data["params"]["callback"])),
        ('name', (data["file_name"])),
        ('success_action_status', ('200')),
        ('x-oss-content-type', (data["params"]["x_oss_content_type"])),
        ('file', ('image', file_bytes, 'image/*'))
    ]
    body, content_type = encode_multipart_formdata(data, boundary=boundary)
    headers['Content-Type'] = content_type
    res=await client.post(url, headers=headers, data=body,timeout=60)
  print(res.text)
  return res.json()["data"]

if __name__ == '__main__':
  import asyncio
  asyncio.run(upload("o2.webp"))
