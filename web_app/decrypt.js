const SECRET_KEY_STR = '5IzP5qP9GhiN8POP3HvHsuEKEGSaaVBK';

function sha256(str) {
    return CryptoJS.SHA256(str).toString();
}

function getSecretKey() {
    return CryptoJS.SHA256(SECRET_KEY_STR).toString();
}

function hexToWordArray(hex) {
    return CryptoJS.enc.Hex.parse(hex);
}

function decryptUserData(encryptedData) {
    try {
        const decoded = CryptoJS.enc.Base64.parse(encryptedData);
        const decodedStr = decoded.toString(CryptoJS.enc.Hex);
        const jsonSizeHex = decodedStr.substring(0, 8);
        const jsonSize = parseInt(jsonSizeHex, 16);
        const ivHex = decodedStr.substring(8, 40);
        const iv = hexToWordArray(ivHex);
        const ciphertextHex = decodedStr.substring(40);
        const ciphertext = CryptoJS.enc.Hex.parse(ciphertextHex);
        const secretKeyHex = getSecretKey();
        const key = hexToWordArray(secretKeyHex);
        const decrypted = CryptoJS.AES.decrypt(
            {ciphertext: ciphertext},
            key,
            {
                iv: iv,
                mode: CryptoJS.mode.CBC,
                padding: CryptoJS.pad.Pkcs7
            }
        );
        let decryptedStr = decrypted.toString(CryptoJS.enc.Utf8);
        decryptedStr = decryptedStr.substring(0, jsonSize);
        const userData = JSON.parse(decryptedStr);
        return userData;
    } catch (error) {
        console.error('Ошибка расшифровки:', error);
        throw new Error(`Не удалось расшифровать данные: ${error.message}`);
    }
}