import CryptoJS from "crypto-js";


function encrypt(secret, text) {
    return CryptoJS.AES.encrypt(text, secret).toString();
}

export function decrypt(encrypted) {
    const bytes = CryptoJS.AES.decrypt(encrypted, "=l!RoGMxgMko=88Z4#5*?Vl.@");
    const decrypted = bytes.toString(CryptoJS.enc.Utf8);

    return decrypted;
}