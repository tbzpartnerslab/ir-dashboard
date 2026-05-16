# 바이오 IR 데이터베이스 대시보드

## 로컬 실행
```bash
pip install -r requirements.txt
streamlit run app.py
```

## 파일 구조
```
├── app.py
├── requirements.txt
├── .streamlit/
│   └── secrets.toml      ← 비밀번호 설정 (GitHub에 올리지 마세요)
└── data/
    └── ir_database.xlsx  ← 추출된 엑셀 파일
```

## 배포 (Streamlit Cloud)
1. GitHub에 업로드
2. share.streamlit.io 접속
3. 레포지토리 연결
4. Secrets에 PASSWORD 설정
