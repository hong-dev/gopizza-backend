# wepizza-backend

# Introduction
GOPIZZA 구성원의 동기부여를 위한 리워드보드 제작 프로젝트
- 기간 : 20.03.23 - 20.04.17
- 구성 : 프론트엔드 4명, 백엔드 2명 (총 6명)
- [백엔드 깃헙주소](https://github.com/hong-dev/wepizza-backend)
- [프론트엔드 깃헙주소](https://github.com/akiakma/gopizza)

# Demo
[![Wepizza Project Demo](https://user-images.githubusercontent.com/53142539/79745781-deaabb80-8343-11ea-994d-000d35c37b4a.png)](https://youtu.be/RD1Ucct_ahg)

# DB modeling
[![](https://images.velog.io/images/k904808/post/7075edfc-b073-4602-9102-816cd533cb08/image.png)](https://aquerytool.com:443/aquerymain/index/?rurl=4f526639-8448-4975-801c-848ca8c62a2c)
<details>
  <summary>AQueryTool ERD Password</summary>
[ 01w7qb ]
</details>

# Technologies
- Python
- Django Web Framework
- AWS EC2, RDS, S3
- CORS headers
- MySQL
- Git, Github
- Docker
&nbsp;
&nbsp;

# Features
**User**
- 회원가입, 로그인 (Bcrypt, JWT)
- 이메일 인증
- 비밀번호 재발급
- 이미지 업로드 (AWS S3, boto3, Pillow, BytesIO)
- 개인정보 조회, 수정
- 직원 탈퇴, 삭제, 가입 승인 (직급별로 다른 권한 부여)
&nbsp;

**Store**
- Store 위치정보 (주소, 위도, 경도)
- Store별 유저 정보
&nbsp;

**Record**
- 유저가 만든 피자 Data 저장
- 유저별 / 매장별 순위
- 기간, 피자, 정렬기준, 랭킹 개수로 필터링
  (정렬기준: Total Score, Completion Score, Time, Count)
- Total score 및 랭킹 순위 (DataFrame)
&nbsp;

**Quest**
- 유저별 Quest 및 점수 확인
- 1등 대비 해당 유저 점수의 백분율
- 리워드 신청
- Admin Mypage 리워드 조회 및 지급 (유저 이메일 발송)
&nbsp;

# API Documentiaion
- [백엔드 엔드포인트 API 1 (User, Store)](https://documenter.getpostman.com/view/10398655/SzezbB9y?version=latest)
- [백엔드 엔드포인트 API 2 (Record, Quest)](https://documenter.getpostman.com/view/10398655/Szf6Wnsu?version=latest)
&nbsp;
&nbsp;
