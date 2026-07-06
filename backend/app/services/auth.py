from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from ..config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

WEAK_PASSWORDS = {
    "password", "123456", "12345678", "qwerty", "abc123", "monkey", "1234567",
    "letmein", "trustno1", "dragon", "baseball", "iloveyou", "master", "sunshine",
    "ashley", "bailey", "shadow", "123123", "654321", "superman", "qazwsx",
    "michael", "football", "password1", "password123", "welcome", "welcome1",
    "welcome123", "admin", "admin123", "root", "root123", "toor", "test",
    "test123", "guest", "guest123", "master123", "changeme", "changeme123",
    "1q2w3e", "1q2w3e4r", "zxcvbn", "asdfgh", "asdfghjkl", "qwerty123",
    "123qwe", "abcdef", "abcdefg", "abcd1234", "xyz123", "000000", "111111",
    "222222", "333333", "444444", "555555", "666666", "777777", "888888",
    "999999", "121212", "123321", "12121212", "66666666", "88888888",
    "password0", "password01", "password012", "password0123", "p@ssword",
    "p@ssword1", "pa$$word", "pa$$word1", "password!", "password@", "password#",
    "password$", "password%", "password^", "password&", "password*",
    "Password", "PASSWORD", "Password1", "PASSWORD1", "P@ssword", "P@SSWORD",
    "qwertyuiop", "azerty", "1234", "0000", "123", "12", "1", "a", "aa",
    "aaa", "aaaa", "aaaaa", "aaaaaa", "aaaaaaa", "aaaaaaaa", "ab", "abc",
    "abcd", "abcde", "abcdef", "abcdefg", "abcdefgh", "12345", "123456789",
    "1234567890", "987654321", "0987654321", "qwerty1", "qwerty12",
    "qwerty1234", "asdf123", "asdf1234", "zxcv123", "zxcv1234", "1234qwerty",
    "qwerty123456", "123456qwerty", "asdfghjkl;", "zxcvbnm,.", "qazwsxedc",
    "edcrfv", "rfvtgb", "tgbnhy", "yhnujm", "ujmikolp", "ikolp;", ";p0o9i8",
    "0o9i8u7", "9i8u7y6", "8u7y6t5", "7y6t5r4", "6t5r4e3", "5r4e3w2",
    "4e3w2q1", "3w2q10", "2q10-=", "10-=[]", "0-=[]\\", "-=[]\\;", "=[]\\;'",
    "[]\\;'", "\\;'/", ";'/.", "'/,", "/.,", ",./", ".//", "//,", "//.",
}


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


def validate_password(password: str) -> tuple[bool, str]:
    if len(password) < 8:
        return False, "密码长度至少8位"
    
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*()_+-=[]{}|;':\",./<>?" for c in password)
    
    if not has_upper:
        return False, "密码必须包含大写字母"
    if not has_lower:
        return False, "密码必须包含小写字母"
    if not has_digit:
        return False, "密码必须包含数字"
    if not has_special:
        return False, "密码必须包含特殊字符"
    
    if password.lower() in WEAK_PASSWORDS:
        return False, "密码过于简单，请勿使用常见密码"
    
    return True, ""