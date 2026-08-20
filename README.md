# IS- (Intelligent Supply Chain Optimization)

대형 화물차 물류운송 효율 및 에너지 비용 최적화 솔루션

## 📋 프로젝트 개요

### 타겟 고객
- 대형 화물차를 운행하는 물류회사

### 제공 솔루션
- 모바일/웹 기반 서비스
- 데이터 기반 연비/경로 최적화

### 1차 목표
- 데이터 기반 연비/경로 최적화 알고리즘 구현

## 🛠️ 기술 스택

### 백엔드
- **프레임워크**: FastAPI (Python)
- **경로 최적화**: Google OR-Tools
- **데이터베이스**: PostgreSQL
- **API 문서**: OpenAPI/Swagger

### 프론트엔드 (예정)
- 웹: React.js
- 모바일: React Native

## 📁 프로젝트 구조

```
IS-/
├── backend/                 # 백엔드 API
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py         # FastAPI 메인 앱
│   │   ├── models/         # 데이터 모델
│   │   ├── routes/         # API 라우트
│   │   ├── services/       # 비즈니스 로직
│   │   ├── utils/          # 유틸리티
│   │   └── config.py       # 설정
│   ├── tests/              # 테스트
│   ├── requirements.txt    # 의존성
│   ├── .env.example        # 환경변수 예제
│   └── Dockerfile          # Docker 설정
├── frontend/               # 프론트엔드 (웹/모바일)
├── docs/                   # 문서
└── .gitignore
```

## 🚀 빠른 시작

### 백엔드 설치

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

API 문서는 `http://localhost:8000/docs`에서 확인할 수 있습니다.

## 📝 라이선스

MIT
