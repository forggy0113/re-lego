from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import base64
import binascii
import uuid

class Encrypted:
    def __init__ (self):
        self.private_key = None
        self.public_key = None
        self.private_key_path = r"./src/sql_py/private.pem"
        self.public_key_path = r"./src/sql_py/public.pem"
    # 生成公鑰和私鑰
    def generate_keys(self):
        self.private_key = RSA.generate(2048)
        self.public_key = self.private_key.publickey()
        with open(self.private_key_path, "wb") as f:
            f.write(self.private_key.export_key())
        with open(self.public_key_path, "wb") as f:
            f.write(self.public_key.export_key())
    
    # 加密
    def encrypt(self, data):
        if not self.public_key:
            with open(self.public_key_path, "rb") as f:
                self.public_key = RSA.import_key(f.read())
        cipher = PKCS1_OAEP.new(self.public_key)
        return base64.b64encode(cipher.encrypt(data.encode())).decode()
    # 解密
    # def decrypt(self, data):
    #     if not self.private_key:
    #         with open(self.private_key_path, "rb") as f:
    #             self.private_key = RSA.import_key(f.read())
    #     cipher = PKCS1_OAEP.new(self.private_key)
    #     return cipher.decrypt(base64.b64decode(data)).decode()
    def decrypt(self, data):
        try:
            # 如果没有加载私钥，加载私钥
            if not self.private_key:
                with open(self.private_key_path, "rb") as f:
                    self.private_key = RSA.import_key(f.read())
            
            # 补全Base64字符串填充
            missing_padding = len(data) % 4
            if missing_padding:
                data += '=' * (4 - missing_padding)
            
            # 解密
            cipher = PKCS1_OAEP.new(self.private_key)
            decrypted_data = cipher.decrypt(base64.b64decode(data)).decode()
            return decrypted_data
        except (binascii.Error, ValueError, TypeError):
            # 捕获Base64解码失败或RSA解密失败的异常
            return None

## 測試加解密效果
# test_uuid = str(uuid.uuid4())
# print(f"原始資料: {test_uuid}")
# Encrypted().generate_keys()
# encrypted_data = Encrypted().encrypt(test_uuid)
# print(f"加密後: {encrypted_data}")
# decrypted_data = Encrypted().decrypt(encrypted_data)
# print(f"解密後: {decrypted_data}")
