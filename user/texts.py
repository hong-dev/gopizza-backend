def message(domain, uidb64, token):
    return f"메일인증 안내입니다.\n 아래 링크를 클릭하면 인증이 완료됩니다. \n\n 인증 링크 : http://{domain}/user/activate/{uidb64}/{token} \n\n 감사합니다."
