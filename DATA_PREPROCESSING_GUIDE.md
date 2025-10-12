# 데이터 전처리 가이드 (Data Preprocessing Guide)

## 프로젝트 배경

교수님과의 면담 결과를 바탕으로, 다음 주(10월 27일)까지 데이터 전처리를 완료해야 합니다.

### 주요 피드백
1. **Comment-1**: CLIPScore까지 성능 평가하면 좋지만, 여의치 않다면 BLEU와 FVD만 해도 됨
2. **Comment-2**: 
   - 한 명은 데이터셋 모으는데 집중
   - 나머지는 기본 프레임워크 셋업
   - 병렬적으로 작업 진행

## 이번 주 작업 계획 (교수님 피드백 기반)

### 1일차-2일차: 데이터 수집 집중
**담당**: 데이터 수집 담당자

#### 작업 내용
```python
# data_preprocessing.ipynb 실행

# 1. Project Gutenberg에서 도서 수집
collector = GutenbergCollector()
book_ids = collector.get_popular_books(genre="fiction", limit=50)

# 2. 도서 다운로드 및 저장
for book_id in book_ids:
    book_text = collector.download_book(book_id)
    # 저장 로직
```

#### 목표
- [ ] 최소 50권의 영어 소설 수집
- [ ] 다양한 장르 확보 (소설, 드라마, 미스터리)
- [ ] 원본 텍스트 파일로 저장

### 1일차-2일차: 프레임워크 셋업
**담당**: 나머지 팀원

#### 작업 내용
1. **환경 구축**
   ```bash
   pip install torch transformers datasets nltk spacy
   python -m spacy download en_core_web_sm
   ```

2. **데이터 전처리 파이프라인 테스트**
   - `data_preprocessing.ipynb` 전체 실행
   - 샘플 데이터로 파이프라인 검증
   - 에러 및 개선사항 기록

3. **모델 조사**
   - 텍스트 변환에 적합한 LLM 모델 조사
   - 후보: GPT-2, T5, BART, mBART
   - 각 모델의 장단점 정리

### 3일차-4일차: 대규모 데이터 전처리

#### 전체 파이프라인 실행
```python
# 수집된 모든 도서에 대해 전처리 실행
pipeline = BookToScriptPipeline()
book_ids = [1342, 84, 98, ...]  # 수집된 모든 도서 ID

results = pipeline.process_multiple_books(
    book_ids, 
    output_dir='./processed_data'
)
```

#### 데이터 품질 검증
1. **결측치 확인**
   - 다운로드 실패한 도서 확인
   - 챕터 분할 실패 확인
   - 개체명 추출 누락 확인

2. **이상치 탐지**
   - 너무 짧은 챕터 (< 100 단어)
   - 너무 긴 챕터 (> 10000 단어)
   - 개체명이 전혀 추출되지 않은 챕터

3. **통계 분석**
   ```python
   # 데이터셋 통계 계산
   total_books = len(results)
   total_chapters = sum(r['total_chapters'] for r in results)
   avg_chapter_length = ...
   
   print(f"Total Books: {total_books}")
   print(f"Total Chapters: {total_chapters}")
   print(f"Average Chapter Length: {avg_chapter_length}")
   ```

### 5일차-6일차: 학습 데이터 포맷 정의

#### 입력-출력 쌍 생성
```python
# 도서 텍스트 (입력) → 스크립트 (출력) 형식 정의

training_data = []
for result in results:
    for chapter in result['processed_chapters']:
        # 입력: 원본 도서 텍스트
        input_text = chapter['original_text']
        
        # 출력: 스크립트 형식 (목표)
        # 초기에는 구조화된 정보를 활용
        script_format = {
            'scene': chapter['chapter_title'],
            'characters': chapter['entities']['PERSON'],
            'location': chapter['entities']['GPE'] + chapter['entities']['LOC'],
            'dialogue': chapter['scene_data']['dialogues'],
            'narrative': chapter['scene_data']['narrative_sentences']
        }
        
        training_data.append({
            'input': input_text,
            'output': script_format
        })
```

#### 데이터셋 분할
```python
from sklearn.model_selection import train_test_split

# 80% 학습, 10% 검증, 10% 테스트
train_data, temp_data = train_test_split(training_data, test_size=0.2)
val_data, test_data = train_test_split(temp_data, test_size=0.5)

print(f"Training samples: {len(train_data)}")
print(f"Validation samples: {len(val_data)}")
print(f"Test samples: {len(test_data)}")
```

### 7일차: 문서화 및 점검

#### 진행 상황 보고서 작성
- 수집된 데이터 통계
- 전처리 결과 요약
- 발견된 문제점 및 해결 방법
- 다음 단계 계획

#### 체크리스트
- [ ] 50권 이상의 도서 수집 완료
- [ ] 모든 도서에 대한 전처리 완료
- [ ] 데이터 품질 검증 완료
- [ ] 학습 데이터 포맷 정의 완료
- [ ] 데이터셋 분할 완료
- [ ] 진행 상황 보고서 작성 완료

## 데이터 전처리 상세 가이드

### 1. 노이즈 제거

#### Gutenberg 헤더/푸터 제거
```python
def remove_gutenberg_header_footer(text):
    # Project Gutenberg의 저작권 정보 제거
    # "*** START OF THIS PROJECT GUTENBERG" ~ "*** END OF THIS PROJECT GUTENBERG"
    pass
```

#### 텍스트 정제
- 과도한 공백 제거
- 줄바꿈 정규화
- 특수 문자 정리

### 2. 핵심 요소 추출

#### 인물 (PERSON)
- SpaCy NER을 사용한 인물명 추출
- 빈도수 기반 주요 인물 식별
- 별칭/변형 처리

#### 장소 (GPE, LOC)
- 지명, 장소명 추출
- 주요 배경 식별

#### 시간 (DATE, TIME)
- 시간적 정보 추출
- 스토리 타임라인 구성

### 3. 스크립트 변환 준비

#### 대화문 추출
```python
# 따옴표로 둘러싸인 대화문 추출
dialogue_pattern = r'["\'']([^"\']+)["\'']'
dialogues = re.findall(dialogue_pattern, text)
```

#### 서술 분리
- 대화가 아닌 서술 부분 추출
- 장면 묘사, 인물 심리 등

#### 장면 구조화
- 챕터를 장면(Scene) 단위로 분할
- 각 장면의 메타데이터 정의
  - 등장인물
  - 배경
  - 주요 사건

## 성능 평가 지표

### BLEU Score (필수)
- 생성된 스크립트와 참조 텍스트의 n-gram 중첩 계산
- BLEU-1, BLEU-2, BLEU-3, BLEU-4 모두 계산

```python
from nltk.translate.bleu_score import sentence_bleu

# 예시
reference = "The quick brown fox jumps over the lazy dog".split()
candidate = "The quick brown fox jumps over a dog".split()

bleu_score = sentence_bleu([reference], candidate)
print(f"BLEU Score: {bleu_score}")
```

### FVD (선택적)
- Fréchet Video Distance
- 비디오 프레임의 품질 평가
- I3D 모델을 사용한 임베딩 생성
- **우선순위 낮음** (Comment-1 참고)

### CLIPScore (선택적)
- CLIP 모델을 사용한 텍스트-이미지 유사도
- **우선순위 낮음** (Comment-1 참고)

## 추천 작업 분담

### 역할 1: 데이터 수집 전담
**작업 시간**: 전체의 60%

#### 주요 업무
- Project Gutenberg 도서 대량 다운로드
- 다양한 장르 확보
- 원본 데이터 백업 및 관리
- 국내 디지털 도서관 데이터 수집 방법 연구

#### 세부 작업
1. 도서 ID 리스트 작성 (100권 목표)
2. 자동 다운로드 스크립트 실행
3. 다운로드 실패 재시도
4. 데이터 정리 및 저장

### 역할 2: 프레임워크 & 전처리
**작업 시간**: 전체의 40%

#### 주요 업무
- 전처리 파이프라인 최적화
- 데이터 품질 검증
- 학습 데이터 포맷 정의
- 모델 조사 및 선정

#### 세부 작업
1. 전처리 파이프라인 버그 수정
2. 성능 최적화 (병렬 처리 등)
3. 데이터 통계 분석
4. LLM 모델 후보 조사

## 다음 단계 (10월 28일 이후)

### 모델링 단계 준비
1. **모델 선택**
   - T5 (Text-to-Text Transfer Transformer)
   - BART (Bidirectional and Auto-Regressive Transformer)
   - GPT-2 (Generative Pre-trained Transformer 2)

2. **Fine-tuning 전략**
   - Pre-trained 모델 로드
   - Task-specific 데이터로 학습
   - Hyperparameter 튜닝

3. **학습 환경**
   - GPU 활용 (Tesla T4)
   - 배치 크기 조정
   - 학습 시간 예측

### 예상 타임라인
- **10월 28일 - 11월 3일**: 모델 학습 (1주)
- **11월 4일 - 11월 10일**: 모델 최적화 (1주)
- **11월 11일 이후**: 성능 평가 및 프로토타입 제작

## 참고 자료

### Project Gutenberg
- 웹사이트: https://www.gutenberg.org
- 인기 도서: https://www.gutenberg.org/browse/scores/top
- API 문서: https://www.gutenberg.org/wiki/Gutenberg:Information_About_Robot_Access_to_our_Pages

### 라이브러리 문서
- SpaCy: https://spacy.io/usage/linguistic-features
- NLTK: https://www.nltk.org/
- Transformers: https://huggingface.co/docs/transformers

### 논문
- BLEU: "BLEU: a Method for Automatic Evaluation of Machine Translation"
- T5: "Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer"
- BART: "BART: Denoising Sequence-to-Sequence Pre-training"

## 문제 해결

### Q: 다운로드가 너무 느려요
A: 병렬 다운로드 사용
```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=5) as executor:
    results = executor.map(collector.download_book, book_ids)
```

### Q: 메모리 부족 에러가 발생해요
A: 배치 처리 사용
```python
batch_size = 10
for i in range(0, len(book_ids), batch_size):
    batch = book_ids[i:i+batch_size]
    # 배치별 처리
```

### Q: 챕터 분할이 잘 안 돼요
A: 정규표현식 패턴 수정 또는 수동 검증
```python
# 다양한 챕터 패턴 시도
patterns = [
    r'\n\s*(CHAPTER|Chapter)\s+([IVXLCDM]+|\d+)\s*\n',
    r'\n\s*(\d+)\.\s*\n',
    r'\n\s*Part\s+([IVXLCDM]+|\d+)\s*\n'
]
```

## 연락처 및 협업

- 정기 회의: 주 2회 (화요일, 목요일)
- 진행 상황 공유: 매일 오후 6시
- 문제 발생 시: 즉시 팀 채팅방 공유

---

**마감일**: 2025년 10월 27일
**목표**: 데이터 전처리 완료 및 모델링 준비
