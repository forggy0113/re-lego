from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import base64
import binascii
import uuid

class Encrypted:
    def __init__ (self, private_key_path, public_key_path):
        self.private_key = None
        self.public_key = None
        self.private_key_path = private_key_path
        self.public_key_path = public_key_path

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
    
    def decrypt(self, data):
        try:
            # 加載私鑰
            if not self.private_key:
                with open(self.private_key_path, "rb") as f:
                    self.private_key = RSA.import_key(f.read())
            
            # 補全Base64字符串填充
            missing_padding = len(data) % 4
            if missing_padding:
                data += '=' * (4 - missing_padding)
            # 解密
            cipher = PKCS1_OAEP.new(self.private_key)
            decrypted_data = cipher.decrypt(base64.b64decode(data)).decode()
            return decrypted_data
        except (binascii.Error, ValueError, TypeError):
            # 捕獲Base64解碼失敗或RSA解密失敗的異常
            return None
        
# ## 測試加解密效果
# test_uuid = str(uuid.uuid4())
# print(f"原始資料: {test_uuid}")
# Encrypted( private_key_path= "./sql/private.pem", public_key_path = "./sql/public.pem").generate_keys()
# encrypted_data = Encrypted( private_key_path= "./sql/private.pem", public_key_path = "./sql/public.pem").encrypt('73407d38-7601-4b4c-8c25-c4c03427c0ed')
# print(f"加密後: {encrypted_data}")
# decrypted_data = Encrypted( private_key_path= "./sql/private.pem", public_key_path = "./sql/public.pem").decrypt('gRWz9Gb6YbZPtC7h3Rbfx9MbK9PPKFF9ig64dARBTSMiAlV5t+po+s6QK/q+jFDOtubwFVbiOFzAZVvq0Ejy1N33Yf9bHM95MU4TvjYo00KKbyrZL20xrCS6DsRYnrcHlZ4I6JcUb5uE45R2iK9+9X8k2butI0ex6etDsoJ+kmpfis7v03TS9NGqiadwTjGwzVJ8l33rASjBcXZRExDp0RpY8WwoRWPlskH2zdCUSUpDsL+AbX2u3arQa3ivCAOVg0K7ITLkUF+cTGpooeu3uuypYB1XzNE665Y/7mCJKhtXqvWv9bTOLWJubke7PM6iHVP6rJ3l43xdRlscM0thgQ==')
# print(f"解密後: {decrypted_data}")
