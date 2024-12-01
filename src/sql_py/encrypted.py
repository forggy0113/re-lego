from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
import os
import base64


class AES:
    def __init__(self):
        self.aes_key = os.urandom(32) # AES加密密鑰(32字節=256位元)
    
    def encrypt_aes(self, data):
        try:
            # 隨機生成初始向量(IV) 16字節
            iv = os.urandom(16)
            # 創建AES-CBC填充數據  # CBC(密碼快連結)要求數據輸入長度是密碼塊大小的倍數
            cipher = Cipher(algorithms.AES(self.aes_key), modes.CBC(iv))
            encryptor = cipher.encryptor()
            # 使用PKCS7填充數據
            padder = padding.PKCS7(algorithms.AES.block_size).padder()
            padded_data = padder.update(data) + padder.finalize()
            # 加密數據
            encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
            # 返回 IV 和加密數據，使用 Base64 進行編碼
            return base64.b64encode(iv + encrypted_data).decode()
        except Exception as e:
            print(f"加密失敗:{e}")
    
    def decrypt_aes(self,encrypted_data):
        try:
            # 解碼base64數據
            encrypted_data = base64.b64decode(encrypted_data)
            # 分離iv和加密內容
            iv, encrypted_message= encrypted_data[:16], encrypted_data[16:]
            # 創建AES解碼器
            cipher = Cipher(algorithms.AES(self.aes_key), modes.CBC(iv))
            decryptor = cipher.decryptor()
            # 解密數據
            decryptor_padded_data = decryptor.update(encrypted_message) + decryptor.finalize()
            # 去除PKCS7填充(數位簽章格式)
            unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
            data = unpadder.update(decryptor_padded_data) + unpadder.finalize() 
            return data
        except Exception as e:
            print(f"解密失敗={e}")
            
            
            
# if __name__ == "__main__":
#     ecc = AES()  # 初始化 ECC 类，自动生成 AES 密钥

#     # 待加密数据
#     plain_text = "This is a test UUID."
#     print(f"原始数据: {plain_text}")

#     # 加密数据
#     encrypted = ecc.encrypt_aes(plain_text.encode())
#     print(f"加密后数据: {encrypted}")

#     # 解密数据
#     decrypted = ecc.decrypt_aes(encrypted).decode()
#     print(f"解密后数据: {decrypted}")

    # 验证结果
    # assert plain_text == decrypted
