# 데이터 전처리 방법론 및 학술적 배경

## 개요

본 문서는 도서 텍스트를 비디오 스크립트로 변환하기 위한 데이터 전처리 파이프라인의 이론적 배경과 구현 방법론을 설명합니다.

---

## 목차

1. [전처리 파이프라인 개요](#1-전처리-파이프라인-개요)
2. [텍스트 정제 (Text Cleaning)](#2-텍스트-정제-text-cleaning)
3. [문서 분할 (Document Segmentation)](#3-문서-분할-document-segmentation)
4. [개체명 인식 (Named Entity Recognition)](#4-개체명-인식-named-entity-recognition)
5. [대화문 추출 (Dialogue Extraction)](#5-대화문-추출-dialogue-extraction)
6. [평가 지표](#6-평가-지표)
7. [참고 문헌 및 리소스](#7-참고-문헌-및-리소스)

---

## 1. 전처리 파이프라인 개요

### 1.1 전체 워크플로우

```
원본 텍스트 (Project Gutenberg)
    ↓
[1] 메타데이터 제거 (Header/Footer Removal)
    ↓
[2] 텍스트 정규화 (Text Normalization)
    ↓
[3] 문서 구조 분석 (Document Structure Analysis)
    ├─ 목차 감지 및 제거
    └─ 챕터 경계 감지
    ↓
[4] 챕터 분할 (Chapter Segmentation)
    ↓
[5] 개체명 추출 (Named Entity Recognition)
    ├─ 인물 (PERSON)
    ├─ 장소 (GPE, LOC)
    └─ 시간 (DATE, TIME)
    ↓
[6] 텍스트 구조화 (Text Structuring)
    ├─ 대화문 추출
    ├─ 서술 분리
    └─ 장면 구조 생성
    ↓
학습 데이터셋 (JSON)
```

### 1.2 설계 원칙

1. **견고성 (Robustness)**: 다양한 형식의 텍스트 처리
2. **확장성 (Scalability)**: 대규모 데이터셋 처리 가능
3. **재현성 (Reproducibility)**: 일관된 결과 보장
4. **모듈성 (Modularity)**: 각 단계의 독립적 실행

---

## 2. 텍스트 정제 (Text Cleaning)

### 2.1 이론적 배경

텍스트 정제는 NLP 파이프라인의 첫 단계로, 노이즈를 제거하고 일관된 형식을 보장합니다.

**관련 연구:**
- Manning, C. D., & Schütze, H. (1999). *Foundations of Statistical Natural Language Processing*. MIT Press.
- Jurafsky, D., & Martin, J. H. (2023). *Speech and Language Processing* (3rd ed.).

### 2.2 구현 방법

#### 2.2.1 메타데이터 제거

**목적**: Project Gutenberg의 저작권 정보 및 라이센스 텍스트 제거

**방법론**:
```python
def remove_gutenberg_header_footer(self, text):
    # 시작 마커: "*** START OF THIS PROJECT GUTENBERG"
    # 종료 마커: "*** END OF THIS PROJECT GUTENBERG"
    # 마커 사이의 실제 콘텐츠만 추출
```

**참고 자료**:
- Project Gutenberg: https://www.gutenberg.org/policy/robot_access.html
- Gerlach, M., & Font-Clos, F. (2018). "A standardized Project Gutenberg corpus for statistical analysis of natural language and quantitative linguistics." *Entropy*, 20(2), 126.

#### 2.2.2 공백 정규화

**방법**:
- 여러 공백 → 단일 공백
- 여러 줄바꿈 → 이중 줄바꿈 (단락 구분)
- 줄 시작/끝 공백 제거

**참고**:
- Unicode 정규화: https://unicode.org/reports/tr15/

---

## 3. 문서 분할 (Document Segmentation)

### 3.1 챕터 감지 알고리즘

본 프로젝트는 **4단계 계층적 접근법**을 사용합니다:

#### 단계 1: 목차 제거

**문제**: 많은 도서에는 챕터 목록이 포함되어 있으며, 이를 실제 챕터로 오인식할 수 있음

**해결책**: 
- 패턴 기반 목차 감지
- "Heading to Chapter", "Contents" 키워드 필터링
- 정규표현식을 사용한 반복 패턴 제거

```python
toc_patterns = [
    r'(CONTENTS|Contents|TABLE OF CONTENTS).*?(?=\n\s*CHAPTER)',
    r'(Heading to Chapter.*?\n.*?\d+\n){5,}',
]
```

**학술적 근거**:
- Sebastiani, F. (2002). "Machine learning in automated text categorization." *ACM Computing Surveys*, 34(1), 1-47.

#### 단계 2: 다중 패턴 매칭

**방법론**: 
여러 정규표현식 패턴을 시도하여 최적의 분할 결과 선택

**지원 형식**:
1. "CHAPTER I", "Chapter 1", "CHAPTER ONE"
2. "BOOK I", "PART I"
3. 로마 숫자 단독 (I, II, III)
4. 아라비아 숫자 단독 (1, 2, 3)

**참고**:
- Hearst, M. A. (1997). "TextTiling: Segmenting text into multi-paragraph subtopic passages." *Computational Linguistics*, 23(1), 33-64.
- Choi, F. Y. (2000). "Advances in domain independent linear text segmentation." *NAACL 2000*.

#### 단계 3: 길이 기반 검증

**원리**: 
- 실제 챕터는 일정 길이 이상의 콘텐츠를 가짐 (최소 500자)
- 짧은 텍스트는 목차 항목일 가능성이 높음

**수식**:
```
valid_chapter = (chapter_length > min_threshold) AND 
                (3 <= total_chapters <= 150)
```

#### 단계 4: Fallback 줄 단위 분석

**방법**: 
- 패턴 매칭 실패 시 각 줄을 순차 분석
- 휴리스틱 규칙 적용:
  - 짧은 줄 (≤60자) 중 챕터 키워드 검색
  - 최소 길이 검증

**관련 연구**:
- Eisenstein, J., & Barzilay, R. (2008). "Bayesian unsupervised topic segmentation." *EMNLP 2008*.

---

## 4. 개체명 인식 (Named Entity Recognition)

### 4.1 이론적 배경

NER은 텍스트에서 명명된 개체(인물, 장소, 조직 등)를 식별하고 분류하는 작업입니다.

**주요 논문**:
1. Tjong Kim Sang, E. F., & De Meulder, F. (2003). "Introduction to the CoNLL-2003 shared task: Language-independent named entity recognition." *CoNLL 2003*.
2. Nadeau, D., & Sekine, S. (2007). "A survey of named entity recognition and classification." *Lingvisticae Investigationes*, 30(1), 3-26.

### 4.2 구현: SpaCy 사용

**선택 이유**:
- 산업 표준 NLP 라이브러리
- 사전 학습된 모델 제공
- 높은 정확도와 빠른 처리 속도

**사용 모델**: `en_core_web_sm`
- 학습 데이터: OntoNotes 5.0
- 지원 개체: PERSON, GPE, LOC, DATE, TIME, ORG, EVENT

**참고 자료**:
- SpaCy 공식 문서: https://spacy.io/usage/linguistic-features#named-entities
- Honnibal, M., & Montani, I. (2017). "spaCy 2: Natural language understanding with Bloom embeddings, convolutional neural networks and incremental parsing."

### 4.3 개체명 통계 및 빈도 분석

**방법**:
```python
# 빈도수 계산
entity_counts = defaultdict(int)
for entity in entities:
    entity_counts[entity] += 1

# 빈도순 정렬
sorted_entities = sorted(entity_counts.items(), 
                        key=lambda x: x[1], 
                        reverse=True)
```

**활용**:
- 주요 등장인물 식별
- 스토리 배경 위치 파악
- 시간적 흐름 분석

---

## 5. 대화문 추출 (Dialogue Extraction)

### 5.1 정규표현식 기반 추출

**패턴**:
```python
dialogue_pattern = r'["\'"]([^"\'"]+)["\'"]'
```

**한계 및 개선 방향**:
- 현재: 따옴표 기반 단순 추출
- 개선 가능: 화자 식별, 대화 턴 분석

**관련 연구**:
- Iosif, E., & Potamianos, A. (2007). "A soft-clustering algorithm for automatic induction of semantic classes." *INTERSPEECH 2007*.
- He, H., et al. (2013). "Learning to extract keyphrase from micro-blogs with multi-granularity features." *WWW 2013*.

### 5.2 서술과 대화의 분리

**목적**: 
스크립트 형식 변환을 위해 대화문과 서술을 구분

**방법**:
1. 대화문 추출 후 원본에서 제거
2. 남은 텍스트를 서술로 간주
3. 공백 정규화

---

## 6. 평가 지표

### 6.1 BLEU (Bilingual Evaluation Understudy)

**목적**: 생성된 텍스트와 참조 텍스트의 유사도 측정

**공식**:
```
BLEU = BP × exp(Σ wn log pn)

where:
- BP: Brevity Penalty
- wn: n-gram 가중치
- pn: n-gram precision
```

**구현**:
```python
from nltk.translate.bleu_score import sentence_bleu

bleu_score = sentence_bleu(
    [reference_tokens],
    candidate_tokens,
    weights=(0.25, 0.25, 0.25, 0.25)  # BLEU-4
)
```

**참고 논문**:
- Papineni, K., et al. (2002). "BLEU: a method for automatic evaluation of machine translation." *ACL 2002*.

**변형**:
- BLEU-1, BLEU-2, BLEU-3, BLEU-4
- Smoothing functions (Chen & Cherry, 2014)

### 6.2 추가 평가 지표 (선택적)

#### FVD (Fréchet Video Distance)
**용도**: 비디오 생성 품질 평가

**참고**:
- Unterthiner, T., et al. (2018). "Towards accurate generative models of video: A new metric & challenges." *arXiv:1812.01717*.

#### CLIPScore
**용도**: 텍스트-이미지 의미적 유사도

**참고**:
- Hessel, J., et al. (2021). "CLIPScore: A reference-free evaluation metric for image captioning." *EMNLP 2021*.
- Radford, A., et al. (2021). "Learning transferable visual models from natural language supervision." *ICML 2021*.

---

## 7. 참고 문헌 및 리소스

### 7.1 핵심 논문

#### 텍스트 전처리
1. **Manning, C. D., & Schütze, H. (1999).** *Foundations of Statistical Natural Language Processing*. MIT Press.
   - 텍스트 정제 및 정규화의 기초

2. **Gerlach, M., & Font-Clos, F. (2018).** "A standardized Project Gutenberg corpus for statistical analysis of natural language and quantitative linguistics." *Entropy*, 20(2), 126.
   - DOI: 10.3390/e20020126
   - Project Gutenberg 데이터 활용 방법론

#### 문서 분할
3. **Hearst, M. A. (1997).** "TextTiling: Segmenting text into multi-paragraph subtopic passages." *Computational Linguistics*, 23(1), 33-64.
   - 텍스트 분할의 고전적 접근법

4. **Choi, F. Y. (2000).** "Advances in domain independent linear text segmentation." *NAACL 2000*.
   - 도메인 독립적 분할 기법

5. **Eisenstein, J., & Barzilay, R. (2008).** "Bayesian unsupervised topic segmentation." *EMNLP 2008*.
   - 비지도 학습 기반 분할

#### 개체명 인식
6. **Tjong Kim Sang, E. F., & De Meulder, F. (2003).** "Introduction to the CoNLL-2003 shared task: Language-independent named entity recognition." *CoNLL 2003*.
   - NER 평가 기준

7. **Nadeau, D., & Sekine, S. (2007).** "A survey of named entity recognition and classification." *Lingvisticae Investigationes*, 30(1), 3-26.
   - NER 종합 서베이

#### 평가 지표
8. **Papineni, K., Roukos, S., Ward, T., & Zhu, W. J. (2002).** "BLEU: a method for automatic evaluation of machine translation." *ACL 2002*.
   - BLEU 스코어 원논문

9. **Chen, B., & Cherry, C. (2014).** "A systematic comparison of smoothing techniques for sentence-level BLEU." *WMT 2014*.
   - BLEU smoothing 기법

### 7.2 오픈소스 도구 및 라이브러리

#### NLP 라이브러리
1. **SpaCy**
   - GitHub: https://github.com/explosion/spaCy
   - 문서: https://spacy.io/
   - 라이센스: MIT
   - 인용: Honnibal, M., & Montani, I. (2017)

2. **NLTK (Natural Language Toolkit)**
   - GitHub: https://github.com/nltk/nltk
   - 문서: https://www.nltk.org/
   - 라이센스: Apache 2.0
   - Bird, S., Klein, E., & Loper, E. (2009). *Natural Language Processing with Python*. O'Reilly.

3. **Transformers (Hugging Face)**
   - GitHub: https://github.com/huggingface/transformers
   - 문서: https://huggingface.co/docs/transformers
   - 라이센스: Apache 2.0
   - Wolf, T., et al. (2020). "Transformers: State-of-the-art natural language processing." *EMNLP 2020*.

#### 데이터 소스
4. **Project Gutenberg**
   - URL: https://www.gutenberg.org/
   - API: https://gutendex.com/
   - 정책: https://www.gutenberg.org/policy/robot_access.html

#### 관련 GitHub 프로젝트
5. **Awesome NLP**
   - https://github.com/keon/awesome-nlp
   - NLP 리소스 큐레이션

6. **Awesome Text Preprocessing**
   - https://github.com/jbesomi/awesome-text-preprocessing
   - 텍스트 전처리 도구 모음

7. **BookNLP**
   - https://github.com/booknlp/booknlp
   - 도서 텍스트 분석 전문 도구
   - Bamman, D., Popat, S., & Shen, S. (2019). "An annotated dataset of literary entities." *NAACL 2019*.

8. **Gutenberg Corpus**
   - https://github.com/pgcorpus/gutenberg
   - Project Gutenberg 데이터셋 도구

### 7.3 추가 학습 자료

#### 온라인 코스
1. **Stanford CS224N: Natural Language Processing with Deep Learning**
   - https://web.stanford.edu/class/cs224n/

2. **fast.ai NLP Course**
   - https://www.fast.ai/

#### 책
1. **Jurafsky, D., & Martin, J. H. (2023).** *Speech and Language Processing* (3rd ed.).
   - 온라인: https://web.stanford.edu/~jurafsky/slp3/

2. **Eisenstein, J. (2019).** *Introduction to Natural Language Processing*. MIT Press.

---

## 8. 구현 세부사항

### 8.1 시스템 요구사항

**소프트웨어**:
- Python 3.8+
- PyTorch 2.0+
- SpaCy 3.0+
- NLTK 3.8+

**하드웨어 (권장)**:
- RAM: 8GB 이상
- GPU: CUDA 지원 (선택적, 속도 향상)
- 저장공간: 10GB 이상

### 8.2 설치 방법

```bash
# 필수 라이브러리 설치
pip install torch transformers datasets nltk spacy beautifulsoup4 requests scikit-learn

# SpaCy 모델 다운로드
python -m spacy download en_core_web_sm

# NLTK 데이터
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

### 8.3 데이터 흐름

```
Input: Raw book text from Project Gutenberg
  ↓
[TextPreprocessor]
  → remove_gutenberg_header_footer()
  → remove_table_of_contents()
  → clean_text()
  → split_into_chapters()
  ↓
[EntityExtractor]
  → extract_entities() (SpaCy NER)
  → get_main_characters()
  → get_main_locations()
  ↓
[ScriptFormatter]
  → extract_dialogues()
  → extract_narrative()
  → create_scene_structure()
  ↓
Output: Structured JSON data for LLM training
```

### 8.4 성능 최적화

**병렬 처리**:
```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=5) as executor:
    results = executor.map(pipeline.process_book, book_ids)
```

**메모리 관리**:
- 배치 처리 (10-20권 단위)
- SpaCy max_length 조정
- 중간 결과 파일 저장

---

## 9. 결론 및 향후 연구

### 9.1 현재 구현의 강점
- ✅ 견고한 챕터 분할 (목차 필터링)
- ✅ 다양한 도서 형식 지원
- ✅ 높은 자동화 수준
- ✅ 확장 가능한 아키텍처

### 9.2 개선 가능 영역
- 화자 식별 (Speaker Identification)
- 감정 분석 (Sentiment Analysis)
- 공지시 해결 (Coreference Resolution)
- 다국어 지원

### 9.3 관련 연구 방향
1. **Transformer 기반 분할**
   - BERT, GPT를 활용한 semantic segmentation
   
2. **Neural NER**
   - BiLSTM-CRF, Transformer-based NER
   
3. **End-to-End 학습**
   - 전처리와 모델 학습 통합

---

## 부록: 코드 예시

### A. 완전한 파이프라인 실행

```python
# 1. 초기화
from data_preprocessing import BookToScriptPipeline

pipeline = BookToScriptPipeline()

# 2. 단일 도서 처리
result = pipeline.process_book(1342)  # Pride and Prejudice

# 3. 결과 확인
print(f"Book ID: {result['book_id']}")
print(f"Chapters: {result['total_chapters']}")
print(f"Characters: {len(result['processed_chapters'][0]['entities']['PERSON'])}")

# 4. 다중 도서 처리
book_ids = [1342, 84, 98, 2701, 2852]
results = pipeline.process_multiple_books(book_ids, output_dir='./processed_data')

# 5. 통계 출력
total_chapters = sum(r['total_chapters'] for r in results)
print(f"Total chapters processed: {total_chapters}")
```

### B. 평가 예시

```python
from evaluation import EvaluationMetrics

metrics = EvaluationMetrics()

# BLEU 점수 계산
reference = "The quick brown fox jumps over the lazy dog"
candidate = "The quick brown fox jumps over a lazy dog"

bleu_scores = metrics.calculate_bleu_variants(reference, candidate)
print(f"BLEU-4: {bleu_scores['BLEU-4']:.4f}")
```

---

**작성일**: 2025-10-12  
**버전**: 2.0  
**라이센스**: MIT  
**저자**: AI Lab Team

**인용 형식**:
```
AI Lab Team (2025). 도서-스크립트 변환 데이터 전처리 방법론.
GitHub: https://github.com/dolphin1404/AI_lab
```
