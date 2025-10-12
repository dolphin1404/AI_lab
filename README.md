# AI_lab
- Kyu-Min Lee 2021039002
- 2025-2 Artificial intelligence

## 프로젝트 개요 (Project Overview)

### 주제: 도서 텍스트의 비디오 스크립트 변환 LLM 연구
**목표**: 도서 내용을 비디오 스크립트 형식으로 변환하는 LLM 모델 개발

**변경 사항**:
- 기존: 도서 → 스크립트 → 비디오 생성
- 현재: 비디오 생성 API 배제, **스크립트 변환 LLM 연구에 집중**

### 프로젝트 일정

#### Phase 1: 데이터 수집 및 전처리 (~ 10월 27일)
- [x] 데이터 수집 모듈 개발 (Project Gutenberg)
- [x] 텍스트 전처리 파이프라인 구축
- [x] 개체명 추출 (인물, 장소, 시간)
- [x] 스크립트 변환용 데이터 구조화
- [ ] 대규모 데이터셋 수집 및 검증

#### Phase 2: 모델링 (2주, 10월 28일 ~ 11월 10일 예상)
- [ ] LLM 모델 선택 및 구조 설계
- [ ] Fine-tuning 전략 수립
- [ ] 학습 데이터 포맷 정의
- [ ] 모델 학습 및 최적화

#### Phase 3: 성능 평가 (10월 29일 ~ 12월 3일)
- [x] BLEU Score 구현 (텍스트 유사도)
- [ ] FVD (Fréchet Video Distance) - 선택적
- [ ] CLIPScore - 선택적
- [ ] 프로토타입 제작

### 역할 분담
교수님 피드백에 따라:
- **1명**: 데이터셋 수집에 집중
- **나머지**: 기본 프레임워크 셋업
- **전체**: 병렬적으로 작업 진행

### 데이터 소스
1. **Project Gutenberg**: 영어 고전 도서
2. **국내 디지털 도서관**: 한국어 도서 (연구 중)
3. **장르**: 소설, 드라마, 미스터리 등

### 주요 파일
- `data_preprocessing.ipynb`: 데이터 수집 및 전처리 파이프라인
- `week2.ipynb`: PyTorch 환경 확인

## Development Environment

### Hardware
- **GPU**: Tesla T4
- **CUDA Support**: Available (1 device)

### Software Stack
- **Python**: 3.12.11
- **PyTorch**: 2.8.0+cu126 (CUDA-enabled)
- **Jupyter Notebook**: Configured and operational
- **NLP Libraries**: SpaCy, NLTK, Transformers

### Environment Status
- ✅ PyTorch successfully imported and functional
- ✅ CUDA acceleration available
- ✅ Tensor operations working correctly
- ✅ GPU-accelerated deep learning ready
- ✅ Data preprocessing pipeline implemented

### Quick Start
1. **Environment Check**: Run `week2.ipynb` to verify PyTorch installation
2. **Data Preprocessing**: Open `data_preprocessing.ipynb` to start data collection and preprocessing

## 📖 문서 네비게이션 (Document Navigation)

### 🎯 처음 시작하는 경우
1. **`PROJECT_SUMMARY.md`** ⭐⭐⭐ - 전체 프로젝트 요약 및 시작 방법
2. **`HOW_TO_PROCEED.md`** ⭐⭐⭐ - "어떻게 진행할까?" 질문에 대한 답변
3. **`QUICK_START.md`** ⭐⭐ - 5분 만에 시작하기

### 📅 일정 및 계획
- **`WEEKLY_TIMELINE.md`** - Day-by-day 상세 일정
- **`WORKFLOW.md`** - 프로세스 다이어그램 및 흐름도

### 🔧 기술 문서
- **`DATA_PREPROCESSING_GUIDE.md`** - 데이터 전처리 상세 가이드
- **`data_preprocessing.ipynb`** - 실제 작업 노트북

### 🛠️ 도구
- **`track_progress.py`** - 진행 상황 추적 도구

## 다음 주까지 할 일 (Tasks by Next Week - Oct 27)

### 데이터 수집
- [ ] Project Gutenberg에서 최소 50권 이상 다운로드
- [ ] 다양한 장르 확보 (소설, 드라마, 미스터리)
- [ ] 국내 디지털 도서관 접근 방법 연구

### 데이터 전처리
- [ ] 수집된 모든 도서에 대해 전처리 파이프라인 실행
- [ ] 결측치 및 이상치 검사
- [ ] 데이터 품질 검증 및 통계 분석
- [ ] 챕터/장면 분할 정확도 향상

### 프레임워크 셋업
- [ ] 모델 학습을 위한 데이터 포맷 정의
- [ ] 학습/검증/테스트 데이터셋 분할
- [ ] 베이스라인 모델 조사

### 문서화
- [ ] 진행 상황 정리 및 보고서 작성
- [ ] 중간 점검 준비