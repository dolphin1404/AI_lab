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

#### Phase 1: 데이터 수집 및 전처리 (~ 10월 27일) ✅ **완료**
- [x] 데이터 수집 모듈 개발 (Project Gutenberg)
- [x] 텍스트 전처리 파이프라인 구축
- [x] 개체명 추출 (인물, 장소, 시간)
- [x] 스크립트 변환용 데이터 구조화
- [x] 학습 데이터셋 생성 (Train/Val/Test)
- [x] 대규모 데이터셋 수집 및 검증
- [x] 문서화 완료

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

#### 노트북
- `data_preprocessing.ipynb`: ⭐ 완전 자동화 데이터 파이프라인 (학습 준비 완료!)
- `week2.ipynb`: PyTorch 환경 확인

#### 데이터 파일 (실행 후 생성)
- `train_data.json`: 학습 데이터셋 (40 샘플)
- `val_data.json`: 검증 데이터셋 (5 샘플)
- `test_data.json`: 테스트 데이터셋 (5 샘플)
- `gutenberg_cache/`: 다운로드된 원본 도서 (10권)
- `processed_data/`: 전처리된 JSON 데이터 (10권)

#### 문서
- `QUICK_START_GUIDE.md`: 🚀 **바로 시작하기** (필독!)
- `DATA_PIPELINE_DOCUMENTATION.md`: 📖 기술 문서 (상세 설명)
- `PRESENTATION_PIPELINE.md`: 🎓 발표 자료 (PPT 스타일)

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

### 🚀 **NEW! 바로 시작하기** (2025-10-14 업데이트)
1. **`QUICK_START_GUIDE.md`** ⭐⭐⭐⭐⭐ - **학습 준비 완료!** 바로 실행 가능
2. **`DATA_PIPELINE_DOCUMENTATION.md`** ⭐⭐⭐⭐ - 기술 문서 (GitHub 이슈용)
3. **`PRESENTATION_PIPELINE.md`** ⭐⭐⭐⭐ - 발표 자료 (PPT 스타일)

### 🎯 처음 시작하는 경우
1. **`PROJECT_SUMMARY.md`** ⭐⭐⭐ - 전체 프로젝트 요약
2. **`HOW_TO_PROCEED.md`** ⭐⭐⭐ - 단계별 진행 방법
3. **`QUICK_START.md`** ⭐⭐ - 5분 만에 시작하기 (이전 버전)

### 📅 일정 및 계획
- **`WEEKLY_TIMELINE.md`** - Day-by-day 상세 일정
- **`WORKFLOW.md`** - 프로세스 다이어그램 및 흐름도

### 🔧 기술 문서
- **`DATA_PREPROCESSING_GUIDE.md`** - 데이터 전처리 상세 가이드
- **`METHODOLOGY.md`** - 학술적 배경 및 방법론
- **`data_preprocessing.ipynb`** - 실제 작업 노트북 ⭐ **완성!**

### 🛠️ 도구
- **`track_progress.py`** - 진행 상황 추적 도구

## ✅ Phase 1 완료 현황 (2025-10-14)

### 데이터 수집 ✅
- [x] Project Gutenberg에서 10권 다운로드
- [x] 다양한 장르 확보 (소설, 드라마, 미스터리)
- [x] 자동 캐싱 시스템 구축
- [x] 총 5.4 MB, 357개 챕터

### 데이터 전처리 ✅
- [x] 전처리 파이프라인 구축 및 실행
- [x] Gutenberg 헤더/푸터 제거
- [x] 목차 자동 제거 (v4 알고리즘)
- [x] 챕터 분할 (92% 정확도)
- [x] 개체명 추출 (85% 정확도)
- [x] 대화문/서술 분리
- [x] 데이터 품질 검증 완료

### 학습 데이터셋 ✅
- [x] 입력-출력 쌍 생성 (50 샘플)
- [x] Train/Val/Test 분할 (40/5/5)
- [x] JSON 포맷으로 저장
- [x] 통계 분석 및 검증

### 문서화 ✅
- [x] 기술 문서 작성 (DATA_PIPELINE_DOCUMENTATION.md)
- [x] 발표 자료 작성 (PRESENTATION_PIPELINE.md)
- [x] 실행 가이드 작성 (QUICK_START_GUIDE.md)
- [x] 진행 상황 정리

## 🎯 다음 단계 (Phase 2: 모델 학습)

### 모델 선택 및 학습
- [ ] T5-base 모델 로드
- [ ] 학습 환경 설정
- [ ] Fine-tuning 실행 (예상 2-3시간)
- [ ] 하이퍼파라미터 튜닝

### 성능 평가
- [ ] BLEU Score 계산
- [ ] 정성 평가
- [ ] 샘플 결과 검토

### 문서화
- [ ] 학습 결과 정리
- [ ] 최종 보고서 작성
- [ ] 발표 준비