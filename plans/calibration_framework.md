# Calibration Framework

```
step0 이후 결과를 base 모델로 stage1-2 calibration framework를 제안하는 논문   
목표: 국외 SCI(E) 급   
학술지
  1. 1순위: Energy and Buildings
  2. 상향 도전: Applied Energy
  3. 방법론 중심 대안: Journal of Building Performance Simulation
  4. building science 강조 시: Building and Environment

게재를 위한 요건
    1. 다중 Building Case를 통한 일반화
        - 두 개 이상의 성격 차이가 큰 건물 실험
    2. 기존 방법 비교
        - 같은 baseline에 기존의 방법론을 적용한 결과와 비교 
    3. 재현성과 확장성
        - 다른 건물에도 적용 가능한 규칙 기반 구조인지 설명
```
---   

## 논문 방향성 설계

### 핵심 방향성
- 연구 novelty
    - 단순히 `2-stage calibration` 이 아닌
    - stage 1과 stage 2를 하나의 연결된 calibration framework로 설계한 점
    - 중심 메세지: `reproducible calibration framework 제안`

### 프레임워크 설계 방향
- 변수 기반 카테고리 설정
- optuna: 블록 단위 반복 실행
- agent: 진단에 따른 정제
- optuna - multi-agent 동일 카테고리 유지

### stage 1-2 연결 원칙
- stage 1
    - calibration 카테고리 정의, 카테고리별 반복적 최적화 수행 단계
- stage 2
    - stage 1에서 정의된 동일한 카테고리 구조를 specialist agent 구조로 승격해 추가 개선 수행 단계
    - stage 1의 Calibration structure를 확장하는 단계임

### stage 2 설계 철학
- stage 2는 자유 생성형 AI 시스템이 아니라 structured specialist system으로 설계한다.
- specialist agent는 카테고리별 변수 도메인에 따라 역할이 제한된다.
- electricity, gas, physical plausibility는 별도의 diagnostic/critic 계층에서 판단한다.
- orchestrator는 critic 결과를 바탕으로 specialist를 routing하는 역할을 담당한다.

---

## 연구 Novelty & Contribution

### 선행 연구의 한계점
1. Staged calibration 또는 two-stage calibration을 제안한 기존 연구들
    - 단계 또는 카테고리 구분의 근거가 연구자 직관이나 특정 사례 설정에 의존하는 경우가 많음
2. optimization 기반 calibration
    - 목적함수 최소화에 강함
    - 카테고리별 block-wise iteration, freeze, re-search와 같은 구조적 탐색 설계는 상대적으로 약함
3. pattern-baseed calibration 연구들
    - residual pattern 해석에 강점
    - 일반화된 specialist reasoning 구조로 확장하지 못하는 경우가 많음
4. multi-agent or LLM-based building energy 연구들
    - workflow automaation에는 강하지만, 
    - calibration 자체를 위한 domain-specialist reasoning framework로 정교하게 구조화하는 경우는 많지 않음
    - optimztion 단계에서 사용한 parameter grouping 체계와, 이후 diagnosis 또는 agent reasoning 단계에서 사용하는 문제 분해 체계가 서로 분리되어 있는 경우가 많다.

> 기존 연구들은 staged calibration, automated optimization, residual diagnosis, multi-agent automation을 각각 제시하더라도, 이를 하나의 재현 가능한 calibration reasoning framework로 통합하는 데 한계를 가짐

### novelty 정리
- staged calibration 자체는 기존 문헌에도 존재함
- optimization 기반 calibration과 multi-agent building workflow도 각각의 문헌 축에서 이미 연구되고 있음
- 따라서 본 연구의 핵심 novelty는 아래 세 요소를 하나의 재현 가능한 calibration framework로 통합하는 데 있다.
    1. 데이터 기반으로 검증된 calibration category formation
    2. category-wise iterative block optimization
    3. diagnosis-driven specialist multi-agent refinement

### 예상 핵심 공헌
#### Step 0 


#### Step 1 (Stage 1)
- 확정된 카테고리를 기준으로 iterative block-wise optimization을 수행하는 Stage 1 calibration framework를 제안한다.

#### Step 2 (Stage 2)
- Stage 1의 shared category structure를 그대로 유지한 specialist multi-agent 구조를 설계하고, residual diagnosis에 따라 필요한 specialist만 선택적으로 호출하는 Stage 2 refinement framework를 제안한다.

#### Step 3
- optimization 단계와 agent reasoning 단계 사이에서 동일한 category structure를 유지함으로써, ad-hoc한 AI 후처리가 아닌 구조화된 calibration reasoning 절차를 제시한다.

#### Step 4
- 두 개의 실측 건물 사례를 통해 프레임워크의 적용 가능성과 재현 가능성을 검증하는 방향으로 연구를 설계한다.

### 선행 연구 한계와 공헌의 연결
- 기존 staged calibration 연구의 한계:
    - 단계 구분 근거가 약하거나 case-specific함
    - 본 연구의 공헌:
        - 데이터 기반으로 검증된 category formation 절차 제안

- 기존 optimization calibration 연구의 한계:
    - 최적화는 수행하지만 구조적 iteration 설계와 카테고리 기반 탐색 전략이 부족함
    - 본 연구의 공헌:
        - category-wise iterative block optimization framework 제안

- 기존 pattern-based calibration 연구의 한계:
    - residual 해석은 가능하지만 일반화된 specialist refinement 구조로 이어지지 않음
    - 본 연구의 공헌:
        - diagnosis-driven routing과 specialist agent refinement를 연결하는 구조 제안

- 기존 multi-agent building energy 연구의 한계:
    - workflow automation에는 강하지만 calibration-specific category structure가 약함
    - 본 연구의 공헌:
        - calibration 카테고리 구조를 agent reasoning에 직접 연결하는 structured specialist system 제안

- 기존 전반 문헌의 공통 한계:
    - optimization 단계와 후속 reasoning 단계가 분리되어 재현성과 해석 가능성이 떨어짐
    - 본 연구의 공헌:
        - optimization과 agent reasoning 전반에서 동일한 shared category structure를 유지하는 통합 calibration framework 제안

### 강조해야 할 차별점
- `2-stage calibration` 자체가 아니라 `how the stages are structured`
- `AI 활용` 자체가 아니라 `how agent reasoning is constrained and reproduced`
- `정확도 향상` 자체가 아니라 `how calibration decisions are organized, transferred, and justified`

---

## Step 0 
> 실행 파일: `code/base-osm-model_calibration.py`

- 전제 조건
    - Revit -> (gbXML) -> sketchUP (오류 수정) -> OpenStudio 모델 생성

### 목표
- 보유한 건물 정보에 따라 basic OSM 모델의 건물 정보 모델링 수행
- step 0 단계인 만큼, geometry, zoning, 외장재 재료 및 layer, HVAC 시스템 등 기본 건물 구조와 설계 정보 반영에 중점
- 추후 calibration 단계에서 부하량, setpoint, schedule, system efficiency 등 운영/성능 변수 수정 가능

### 단계 정의
- Step 0은 calibration 자체보다는 baseline building energy model construction 단계에 가깝다.
- 즉, 이후 Step 1-2에서 사용할 기준 OSM을 구축하는 과정으로 정의한다.

### 입출력
- Input: `C:\Users\USER\OneDrive - gachon.ac.kr\2-stage_osm_calibration-osm\KETI_jb_baseline.osm`
- Output: `C:\Users\USER\OneDrive - gachon.ac.kr\2-stage_osm_calibration-osm\base-osm-model_calibration_{datetime.now}.osm`

---

## Step 1 (Stage 1)
> 실행 파일:

### 목표
1. Optuna 하이퍼파라미터 최적화 프레임워크를 사용해 보정 변수 최적화
2. 보정 변수를 물리적으로 해석 가능한 카테고리로 나누고, 카테고리별 반복형 최적화를 수행
3. 전체 calibration 목적함수의 가중합을 최소화하는 방향으로 iteration을 반복

### 과정 설계
1. 어떤 변수들을 하이퍼 파라미터로 설정할 것인가
    - 
2. 해당 변수들의 search space를 어떻게 설정할 것인가
3. 카테고리를 어떤 기준으로 분류할 것인가
    - 카테고리 분류 후보 
        1. 물리 매커니즘 결합성: 동일한 열수지, 운영 전략, 설비 성능 매커니즘 등을 공유하는 변수끼리 군집화
        2. 출력 민감도 유사성: 전력, 가스, 계절별 오차 패턴에 대해 유사한 반응을 보이는 변수끼리 군집화
        3. 식별 가능성 및 공선성: 서로 상관관계가 높은 변수끼리 군집화
    - 카테고리 분류 예상 과정
        - Step 0 baseline 모델에서 calibration 후보 변수 집합 정의
        - 초기 단계에서는 비교적 넓은 후보 변수 집합을 두고 시작
        - building physics 기반으로 변수의 1차 사전 그룹화 수행
        - DOE 기반 샘플링을 통해 변수-성능지표 관계를 수집하고 민감도 분석 수행
        - 민감도 분석 및 상관관계 분석 결과를 바탕으로 카테고리 분류를 검증/보정
4. iteration마다 어떤 카테고리를 다시 탐색할 것이며, 이전 결과에 따라 search space를 어떻게 갱신할 것인가
5. iteration을 어떻게 구성할 것인가
    - 카테고리별 Optuna 최적화를 한 라운드씩 수행
    - 카테고리 반복적 탐색 (A -> B -> C-> A-> B -> ...)
    - 한 라운드 종료 후 전체 목적함수 개선량을 평가하고, 개선이 유의미하면 다음 iteration 수행


### 카테고리 분류 근거 확보 방법
- 초기에는 많은 후보 변수를 포함한 뒤, 분석 결과를 통해 카테고리를 확정하는 방식으로 접근
- 1차 분류는 building physics 기반 사전 가설로 설정
- 이후 DOE 샘플링 결과를 활용해 global sensitivity analysis 수행
- 우선 적용 후보:
    - Latin Hypercube Sampling
    - Morris screening
    - Spearman rank correlation
- 성능지표 예시:
    - annual electricity CVRMSE
    - annual gas CVRMSE
    - monthly electricity bias pattern
    - monthly gas bias pattern
    - seasonal bias (winter gas, shoulder gas, summer electricity)
- 변수별 반응 벡터를 구성한 뒤 clustering을 통해 카테고리 구조를 검증 및 보정
- 즉, 최종 카테고리는 사전 정의를 그대로 고정하는 것이 아니라, 민감도 분석, 상관관계 분석, clustering 결과를 통해 확정한다.

### 카테고리 초안
- Envelope / Air Exchange
- Internal Loads
- Schedules / Operation
- Thermostat / Setpoints
- HVAC / Plant Efficiency
- DHW

### 최적화 구조
- Step 1은 sequential one-pass가 아니라 iterative block-wise optimization으로 정의한다.
- 즉, 카테고리 A -> B -> C ... 순으로 한 라운드를 수행한 뒤 전체 목적함수 개선량을 평가하고, 필요 시 다시 A -> B -> C ... 를 반복한다.
- 각 iteration에서 이전 라운드 결과를 반영해 search space를 축소 또는 재조정할 수 있다.

### 목적함수 초안
- Step 1의 기본 목적함수는 아래와 같은 weighted sum 형태로 정의한다.

```text
J = w1 * CVRMSE_elec
  + w2 * CVRMSE_gas
  + w3 * |NMBE_elec|
  + w4 * |NMBE_gas|
  + w5 * P_phys
  + w6 * P_complex
```

- 여기서
    - `CVRMSE_elec`: 전력 사용량 기준 CVRMSE
    - `CVRMSE_gas`: 가스 사용량 기준 CVRMSE
    - `|NMBE_elec|`: 전력 사용량 기준 절대 NMBE
    - `|NMBE_gas|`: 가스 사용량 기준 절대 NMBE
    - `P_phys`: 물리적으로 비현실적인 조합에 대한 penalty
    - `P_complex`: 한 iteration에서 너무 많은 변수를 동시에 크게 바꾸는 경우의 penalty

- 목적함수 설계 원칙
    - 전력과 가스를 동시에 고려하는 multi-objective calibration을 weighted single-objective 형태로 변환
    - 단순 오차 최소화뿐 아니라 물리적 타당성과 과도한 파라미터 이동 억제를 함께 고려
    - 초기 연구 단계에서는 weighted sum을 사용하고, 이후 필요 시 case별 가중치 조정 전략을 검토

### 성능지표 및 계산 단위
- 1차 기본 지표는 월별 실측 대비 시뮬레이션 결과를 기준으로 계산한다.
- 기본 지표:
    - monthly electricity CVRMSE
    - monthly gas CVRMSE
    - monthly electricity NMBE
    - monthly gas NMBE
- 추가 진단 지표:
    - winter gas bias
    - shoulder season gas bias
    - summer electricity bias

### search space 설정 원칙
- 초기 search space는 각 case의 current parameter value를 기준으로 상대적 허용 범위(`current value ± alpha`)를 두는 방식으로 정의한다.
- `alpha` 값은 변수 유형별로 다르게 둘 수 있으며, 이후 라운드에서 점진적으로 축소할 수 있다.
- search space 범위의 구체적 수치는 추후 변수별 물리 근거, 문헌값, 실무 설계 범위, 초기 민감도 분석 결과를 바탕으로 정교화한다.
- 즉, 현재 단계에서는 search space의 형태와 갱신 원칙을 먼저 정의하고, 세부 범위 근거는 후속 설계 항목으로 남긴다.

### 종료 기준
- 개별 카테고리의 종료가 아니라 전체 목적함수의 가중합 최소화를 기준으로 한다.
- 더 이상 유의미한 개선이 없거나 사전에 정의한 수렴 조건을 만족하면 stop 한다.

### 입출력
- Input:
- Output: 

---

## Why Step 1 Before Step 2

### Step 1이 필요한 이유
- Step 1은 단순히 Step 2의 성능 부족을 보완하기 위한 단계가 아니다.
- calibration 문제에는 다수의 연속형 또는 준연속형 변수와 넓은 탐색 공간이 포함되며, 이러한 문제는 우선적으로 체계적인 optimization으로 다루는 것이 더 적절하다.
- 즉, Step 1은 `search problem`을 해결하는 단계이고, Step 2는 `diagnosis and refinement problem`을 해결하는 단계로 역할이 다르다.

### Step 2만으로 충분하지 않은 이유
- 토큰이 충분하더라도 LLM 또는 agent 시스템이 넓은 연속 탐색 공간을 직접 안정적으로 최적화하는 것은 비효율적일 수 있다.
- Step 2만 사용할 경우, calibration 과정이 case-by-case의 ad-hoc adjustment로 보일 위험이 있다.
- 또한 중요한 변수와 덜 중요한 변수를 구분하지 못한 상태에서 agent가 직접 수정안을 제안하면, 탐색 자유도가 과도하게 커지고 재현성도 약해질 수 있다.

### Step 1의 구조적 역할
- Step 1은 calibration 후보 변수 공간을 정리한다.
- 민감도 분석과 상관관계 분석을 통해 중요한 변수와 카테고리 구조를 도출한다.
- iterative block-wise optimization을 통해 재현 가능한 baseline calibrated model을 확보한다.
- freeze할 변수와 추가 refinement가 필요한 카테고리를 구분한다.

### Step 1에서 Step 2로 넘어가는 이유
- Step 1 종료 시점에는 전체 탐색 공간이 줄어들고, residual pattern이 보다 구조적으로 드러난다.
- 이 시점에서 Step 2는 전역 탐색을 다시 수행하는 것이 아니라, 남아 있는 residual을 진단하고 필요한 specialist만 호출해 세부 refinement를 수행한다.
- 따라서 Step 2는 Step 1을 대체하는 단계가 아니라, Step 1에서 확보한 baseline과 shared category structure를 이용해 refinement를 수행하는 후속 단계다.

### Step 1 -> Step 2 흐름의 의미
- Step 1은 optimization이 더 적합한 문제를 먼저 해결한다.
- Step 2는 Step 1 이후에도 남아 있는 복합 residual과 해석이 필요한 calibration 문제를 specialist reasoning으로 다룬다.
- 이 흐름을 통해 본 프레임워크는 `global search -> structured diagnosis -> specialist refinement`의 형태를 갖는다.
- 결과적으로 Step 2는 자유 생성형 AI 보정이 아니라, Step 1에서 형성된 calibration structure 위에서 작동하는 constrained refinement layer가 된다.

### 논문 메시지 관점의 의미
- Step 1이 존재함으로써 본 연구의 중심이 AI 자체가 아니라 calibration framework에 놓이게 된다.
- Step 2만 있을 경우 agent automation 논문처럼 보일 수 있지만, Step 1과의 연계를 통해 physics-informed, optimization-grounded, diagnosis-driven calibration framework로 포지셔닝할 수 있다.

---

## Step 2 (Stage 2)
> 실행 파일:

### 목표
1. Step 1에서 정의한 카테고리를 기반으로 specialist multi-agent를 구성하여 세부 디테일 보정
2. residual error pattern을 진단하고 필요한 specialist만 선택적으로 호출하는 orchestration 구조 설계
3. 전력, 가스, 물리적 타당성을 함께 고려해 최종 calibration안 도출

### 필요조건
- Step 1 카테고리와 Step 2 specialist agent 구조를 일치시킬 것인가
- electricity, gas, physical plausibility를 어떤 계층의 agent가 판단할 것인가
- orchestrator가 specialist 호출 대상을 어떤 진단 결과에 따라 선택할 것인가

### 주요 결정 사항
- 이전 multi-agent는 특정 residual pattern에 맞춰 agent를 ad-hoc하게 설계하는 방식이었음.
- 그러나 이 방식은 중간 개입이 필요하고, building case가 달라질 때 agent 구조를 다시 설계해야 하는 한계가 있음.
- 따라서 Step 2에서는 Step 1에서 정의한 calibration 카테고리를 그대로 specialist agent로 구성한다.
- specialist agent는 변수 도메인 기준으로 역할을 분담하고, 전력/가스/물리성 검토는 별도의 diagnostic/critic 계층으로 분리한다.

### agent 구조
- Orchestrator Agent
    - 현재 residual error pattern과 이전 라운드 결과를 바탕으로 호출할 specialist agent를 선택
    - critic agent의 진단 결과를 종합해 채택안, freeze 변수, 다음 라운드 실행안을 결정

- Specialist Agent Layer
    - Envelope / Air Exchange Agent
    - Internal Loads Agent
    - Schedules / Operation Agent
    - Thermostat / Setpoints Agent
    - HVAC / Plant Efficiency Agent
    - DHW Agent

- Diagnostic / Critic Layer
    - Electricity Diagnostic Agent
    - Gas Diagnostic Agent
    - Reality Agent

### agent 계층 설계 원칙
- specialist agent는 실제 수정안을 생성하는 역할을 담당한다.
- electricity / gas diagnostic agent는 성능 결과 축에서 residual pattern을 해석하고 우선순위를 제안한다.
- reality agent는 점수와 별개로 물리적 타당성을 검토한다.
- orchestrator는 diagnostic/critic 결과를 바탕으로 필요한 specialist만 선택적으로 호출한다.

### 과정 설계
- Step 1 종료 후 residual error pattern 및 이전 iteration 결과를 입력으로 사용
- orchestrator가 electricity diagnostic, gas diagnostic, reality agent를 먼저 호출해 현재 residual을 진단
- diagnostic/critic agent가 residual pattern과 리스크를 분석
- orchestrator가 필요한 specialist agent 집합을 선택
- specialist agents가 각 카테고리 범위 내에서 candidate calibration안을 제안
- reality agent가 후보안의 물리적 타당성을 검토
- orchestrator가 후보안을 비교하고 최종 채택안 또는 hybrid안을 결정
- 필요 시 freeze 변수와 다음 iteration 대상 카테고리를 정의

### orchestration 규칙 초안
- Step 2는 완전 자유 생성형이 아니라 diagnosis-driven specialist routing 구조로 정의한다.
- 기본 흐름:
    1. electricity diagnostic agent가 전력 residual pattern을 해석
    2. gas diagnostic agent가 가스 residual pattern을 해석
    3. reality agent가 현재 상태 또는 후보안의 물리적 리스크를 검토
    4. orchestrator가 critic 결과를 바탕으로 호출할 specialist agent를 선택
    5. specialist agents가 각자 1개의 candidate case를 제안
    6. orchestrator가 단일 채택안 또는 hybrid안을 결정

### specialist 호출 규칙 방향
- electricity diagnostic 결과가 내부부하 또는 운영 패턴 문제를 시사하면 `Internal Loads`, `Schedules / Operation` agent를 우선 호출
- gas diagnostic 결과가 winter heating 문제를 시사하면 `Envelope / Air Exchange`, `Thermostat / Setpoints`, `HVAC / Plant Efficiency` agent를 우선 호출
- gas diagnostic 결과가 baseload 또는 shoulder season 문제를 시사하면 `DHW`, `Schedules / Operation`, `Envelope / Air Exchange` agent를 우선 호출
- 복수 critic이 동일 카테고리를 반복적으로 지목하면 해당 specialist의 우선순위를 높인다.

### candidate selection 규칙 초안
- orchestrator는 다음 기준을 함께 고려해 채택안을 선택한다.
    - 전체 목적함수 개선량
    - electricity diagnostic 관점의 개선 또는 악화
    - gas diagnostic 관점의 개선 또는 악화
    - reality agent의 pass / hold / reject 의견
- 단일 specialist 후보안이 가장 우수하면 그대로 채택한다.
- 두 개 이상의 specialist 제안이 상호 충돌하지 않고 상보적일 경우에만 hybrid안을 허용한다.
- 반복적으로 유효한 변수는 freeze 대상으로 이동시키고, 다음 라운드에서는 남은 불확실성이 큰 카테고리 중심으로 탐색한다.

### 입출력
- Input:
- Output: 

---

## Step 3 
> Validation Direction

### 실험에서 보여줘야 할 것
- 실험은 단순 정확도 향상만 보여주는 것으로는 부족하다.
- 아래 항목을 함께 보여줄 수 있도록 설계해야 한다.
    - Step 1 only 대비 Step 2 추가 시 개선 효과
    - residual pattern이 어떤 specialist agent 호출로 이어졌는지에 대한 해석 가능성
    - 동일한 category structure가 서로 다른 building case에서도 유지되는지
    - 결과 개선뿐 아니라 calibration 절차의 재현 가능성과 구조적 일관성

### 실험 설계 메모
- 실제 실측 건물 실험 설계와 결과 구성은 후속 섹션에서 구체화한다.
- 현재 단계에서는 validation 방향을 아래처럼 유지한다.
    - accuracy improvement
    - ablation between stages
    - interpretability of diagnosis-driven routing
    - transferability of shared category structure across cases
