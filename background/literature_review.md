# 2. Literature Review

> Date: 2026.04.24. (Fri)   
> Author: 유도연

- [[#1. Review / Positioning|1. Review / Positioning]]
	- [[#1. Review / Positioning#1) Chong et al. (Energy and Buildings, 2021)|1) Chong et al. (Energy and Buildings, 2021)]]
	- [[#1. Review / Positioning#2) Vera-Piazzini and Scarpa (Journal of Building Engineering, 2024)|2) Vera-Piazzini and Scarpa (Journal of Building Engineering, 2024)]]
- [[#2. Recent Calibration Methodologies|2. Recent Calibration Methodologies]]
	- [[#2. Recent Calibration Methodologies#1) Pachano and Bandera (Energy and Buildings, 2021)|1) Pachano and Bandera (Energy and Buildings, 2021)]]
	- [[#2. Recent Calibration Methodologies#2) Gonzalez and Bandera (Building Simulation, 2022)|2) Gonzalez and Bandera (Building Simulation, 2022)]]
	- [[#2. Recent Calibration Methodologies#3) Baba et al. (Building and Environment, 2022)|3) Baba et al. (Building and Environment, 2022)]]
	- [[#2. Recent Calibration Methodologies#4) Kounni et al. (Energy and Buildings, 2023)|4) Kounni et al. (Energy and Buildings, 2023)]]
	- [[#2. Recent Calibration Methodologies#5) Liang et al. (Applied Thermal Engineering, 2025)|5) Liang et al. (Applied Thermal Engineering, 2025)]]
- [[#3. Recent Pattern-Based / Automated Logic|3. Recent Pattern-Based / Automated Logic]]
	- [[#3. Recent Pattern-Based / Automated Logic#1) Sun et al. (Building Simulation, 2022)|1) Sun et al. (Building Simulation, 2022)]]
- [[#4. Recent Multi-agent / LLM-Based Building Energy Research|4. Recent Multi-agent / LLM-Based Building Energy Research]]
	- [[#4. Recent Multi-agent / LLM-Based Building Energy Research#1) Xiao and Xu (Energy and Buildings, 2024)|1) Xiao and Xu (Energy and Buildings, 2024)]]
	- [[#4. Recent Multi-agent / LLM-Based Building Energy Research#2) Lu et al. (iScience, 2025)|2) Lu et al. (iScience, 2025)]]
	- [[#4. Recent Multi-agent / LLM-Based Building Energy Research#3) Xu et al. (Energy and Buildings, 2025)|3) Xu et al. (Energy and Buildings, 2025)]]
- [[#5. Background Summary & Limitation Statement -> Research Contribution|5. Background Summary & Limitation Statement -> Research Contribution]]
	- [[#5. Background Summary & Limitation Statement -> Research Contribution#최근 문헌에서 이미 충분히 나온 부분|최근 문헌에서 이미 충분히 나온 부분]]
	- [[#5. Background Summary & Limitation Statement -> Research Contribution#아직 차별화 가능한 부분|아직 차별화 가능한 부분]]
	- [[#5. Background Summary & Limitation Statement -> Research Contribution#논문 포지셔닝 메모|논문 포지셔닝 메모]]

---

## 1. Review / Positioning

> review 논문 조사 및 연구 포지셔닝

### 1) Chong et al. (Energy and Buildings, 2021)

> Calibrating building energy simulation models: A review of the basics to guide future work

요약   
- Building Energy Simulation Calibration 분야 review paper    

결론   
- Automatic calibration: optimization, Bayesian 접근이 중심
- Calibration 입/출력, 데이터 해상도, 평가 지표, 재현성 이슈 -> 후속 연구의 기준점을 제공

선행 논문 근거
- `왜 재현 가능한 framework가 필요한가`, `왜 목적 함수와 입출력 정의가 필요하나`를 뒷받침

### 2) Vera-Piazzini and Scarpa (Journal of Building Engineering, 2024)

> Building energy model calibration: A review of the state of the art in approaches, methods, and tools

요약
- calibration 방법론, 데이터 수집, simulation 소프트웨어, 검증 절차 리뷰

결론
- variability analysis와 reproducibility 문제가 여전히 중요하다고 지적

선행 논문 근거
- `표준화된 절차의 필요성 강조` 에 뒷받침 (framework contribution 정당화)

---

## 2. Recent Calibration Methodologies

> 최신 calibration 방법론 조사

### 1) Pachano and Bandera (Energy and Buildings, 2021)

> Multi-step building energy model calibration process based on measured data

요약
- measured data 기반의 multi-step, optimization-driven calibration 절차 제안

결론
- EnergyPlus와 jEplus를 사용해 HVAC 파라미터를 조정, indoor temerature, heat production, electic consumption을 함께 검증
- 독립 테스트 기간에도 강건성 확인

선행 논문 근거
- `multi-step calibration`과 `measured data 기반 validation`의 근거

### 2) Gonzalez and Bandera (Building Simulation, 2022)

> A building energy models calibration methodology based on inverse modelling approach

요약
- EnergyPlus의 `HybridModel:Zone`를 활용해 measured indoor temperature만으로 infiltration과 internal mass를 추정하는 inverse modeling 기반 calibration 방법을 제안

결론
- baseline 대비 실측 적합도 개선

선행 논문 근거
- Step 0 이후 후보 변수를 넓게 두고, 실제 데이터로 식별 가능한 변수부터 정교화하려는 방향과 매칭

### 3) Baba et al. (Building and Environment, 2022)

> Calibration of building model based on indoor temperature for overheating assessment using genetic algorithm: Methodology, evaluation criteria, and case study

요약
- indoor hourly temperature를 기준으로 여러 공간을 동시에 calibration하는 multi-objective genetic algorithm 접근
- variance-based sensitivity analysis로 중요한 파라미터를 먼저 추리고 그 후 calibration 수행

결론
- 평가 기준을 새로 정의해 calibrated model selection 수행

선행 논문 근거
- `민감도 분석` -> `후보 축소` -> `단계적 calibration` 흐름과 연결

### 4) Kounni et al. (Energy and Buildings, 2023)

> Building energy model automated calibration using Pymoo

요약
- detailed modeling 후 optimization-based calibration을 수행하는 `2-stage structure` 제안
- 1단계: infiltration과 convective heat exchange를 포함한 detailed modeling
- 2단계: Pymoo 기반 유전 알고리즘 calibration

선행 논문 근거
- 현재 연구의 `Step 0 baseline model construction + Step 1 automated calibration` 구조와 가장 유사한 최근 논문 중 하나

### 5) Liang et al. (Applied Thermal Engineering, 2025)

> A two-step calibration framework for accurate building energy simulations: Integrating energy and indoor temperature data

요약
- energy consumption만이 아니라 indoor temerature를 함께 쓰는 2-step calibration framework 제안
- 1단계: unoccupied period에서 static parameter를
- 2단계: occupied period에서 occupant behavior와 internal gains 같은 dynamic parameter를 조정

선행 논문 근거
- 현재 staged logic과 유사, agent 구조가 아닌 `정적-동적 파라미터 분리 calibration`에 가까움
- 최신 2-step calibration 사례

## 3. Recent Pattern-Based / Automated Logic

> 최신 Pattern-Based / 자동화 로직 calibration 방법론 조사

### 1) Sun et al. (Building Simulation, 2022)
> Application and evaluation of a pattern-based building energy model calibration method using public building datasets

요약
- 기존 pattern-based calibration logic을 public building dataset에 적용, 평가

결론
- monthly electricity/gas bias pattern을 바탕으로 어떤 파라미터를 우선 조정할지 결정하는 자동화 로직 확장 검증

선행 논문 근거
- Stage 2의 `diagnostic -> specialist routing`과 유사
- 본 논문: 규칙 기반 자동 조정 로직, new: 이를 category-specialist agent 구조로 일반화

---

## 4. Recent Multi-agent / LLM-Based Building Energy Research

> 최신 Multi-agent / LLM 기반 Building Energy 분야 동향 조사

### 1) Xiao and Xu (Energy and Buildings, 2024)

> Exploring automated energy optimization with unstructured building data: A multi-agent based framework leveraging large language models

요약
- 비정형 건물 데이터를 활용해 energy optimizatin 업무를 자동화하는 LLM 기반 multi-agent framework 제안
- planner, researcher, advisor 역할의 agent를 두고 building information processing, performance diagnosis, retrofit recommendation의 3단계 수행

선행 논문 근거
- `agent 역할 분리`, `diagnosis`, `knowledge retrieval` 구조적 아이디어 유사

### 2) Lu et al. (iScience, 2025)

> Automated building energy modeling for energy retrofits using a large language model-based multi-agent framework

요약
- geometry modeling, parameter configuration, calibration, retrofit, evaluation까지 end-to-end 자동화한 LLM multi-agent framwork
- existing University of Cambridge office building 실증
- 전부 자연어로 명령을 기본으로 함 
    1) geometry modeling
        - Information retriever -> Programmer -> Reviewer -> Building energy model 
        - 명령 예시: CAD drawing 자료를 보고 outline 추출, design document 보고 envelope, material 정보 추출해줘, -> 추출된 정보로 geometric model 생성해줘
    2) Parameter configuration
        - HVAC system configuration -> schedule generation -> weather data assignment -> simulation setting
        - System modeling
            - HVAC System composition extraction -> System model developmet -> Component parameter extraction -> Component parameter assignment
            - HVAC 시스템 추가
            - 명령 예시: 이 건물의 heating system은 ~~ 고 ~~~...
    3) Model Calibration
        - calibration parameters integration -> optimization algorithm configuration -> evaluation function definition -> optiization execution
        - 과정
            1) 명령 예시: heating setpoint를 18도에서 24도로 바꿔줘
            2) Information retriever: 프롬프트 분석, 모든 매개변수 및 해당 범위를 포함하는 구조화된 JSON 파일 작성
            3) Reviewer agent: 각 항목이 사용자의 의도와 정확히 일치하는지 확인
            4) Programmer agent: 각 매개변수를 모델 라이브러리의 해당 OpenStudio 측정값에 연결함
            5) Generic algorithm을 통해 최적화 알고리즘 구성 
                - 명령 예시: Use blend crossover with alpha = 0.5, Gaussian mutation (mu = 0, sigma = 1, indpb = 1.0), tournament selection with size 3.
                - Information retriever: JSON 으로 설정값 뽑음
                - Programmer agent: JSON에 맞게 Python 코드 생성
                - 개체 생성: 하나의 개체는 한 모델의 파라미터 세트 
            - 결과: NMBE 2.91%, CV-RMSE 0.139, R² 0.972 (ASHRAE guideline 14에 충족)
            - 한계점: operational schedule은 parameter tuning process에 포함 x
    4) retrofit evaluation
        - equipment replacement -> output modification
결론
- real building에서 calibration benchmark를 달성, 모델링 시간을 크게 절감
- 현재 프레임워크는 모델 보정을 위해 일반적으로 사용되는 알고리즘 GA를 사용한다. 이 접근 방식이 모든 보정 시나리오에 최적일 수는 없다. 연속적인 보정에 더 적합한 대체 방법을 통합하면 프레임워크의 유연성과 성능을 더욱 향상시킬 수 있다.

선행 논문 근거
- 현재 연구와 가장 가까운 최근 multi-agent 문헌이지만, 초점은 전체 BEM workflow 자동화이고, calibration 내부를 `category-specialist + diagnostic critics`로 조직하지는 않음

### 3) Xu et al. (Energy and Buildings, 2025)

> Development of a dynamic multi-agent network for building energy modeling: A case study towards scalable and autonomous energy modeling

요약
- `BEM-AI`라는 dynamic multi-agent framework 제안
- A2A, MCP 기반 specialist agent coordination 구성
- building energy modeling workflow를 동적으로 분해, task orchestration을 통해 효율성을 높이는데 초점
- 요청에 따라 스스로 작업 구조를 만드는 BEM AI 시스템
1) 핵심 구성요소

	- Orchestrator: 전체 작업 흐름 제어
	- Planner Agent: 사용자 요청 해석 및 Task 분해
	- Specialized Agents:
		- Generator Agent (기본 모델 생성)
		- Envelope Agent (외피 수정)
		- Lighting Agent (조명/센서 수정)
		- Simulation Agent (시뮬레이션 실행)
		- Output Analyzer Agent (결과 추출)
	- Summary Agent: 최종 보고서 생성

2) 메모리 구조

	- Blackboard: 모델 경로, 결과값, 설정값 등 공유 데이터 저장
	- Dialogue History: 대화 및 작업 이력 저장

3) 동작 흐름

	예: “탬파의 medium office에서 WWR 10% 줄였을 때 절감량 계산”

4. Planner가 작업 분해
5. Generator가 기준 모델 생성
6. Simulation이 기준안 실행
7. Envelope가 WWR 수정
8. Simulation이 수정안 실행
9. Analyzer가 EUI 비교
10. Summary가 결과 보고

선행 논문 근거
- calibration 전용 논문은 아니지만, 현재 연구의 Step 2에서 구상하는 `orchestrator + specialist` 계층 구조와 유사한 최신 건물 에너지 논문
- 자동 생성에 초점을 두어 calibration(실측 데이터 기반 모델 보정) 과정 없음

## 5. Background Summary & Limitation Statement -> Research Contribution

> 선행 연구 요약 및 한계점 언급 -> 본 연구의 contribution

### 최근 문헌에서 이미 충분히 나온 부분
- optimization 기반 automated calibration
- two-step / multi-step calibration
- indoor temperature와 energy use를 함께 쓰는 calibration
- LLM 또는 multi-agent를 이용한 building energy workflow automation

### 아직 차별화 가능한 부분
- calibration 카테고리를 `physics-informed candidate pool -> sensitivity/correlation/clustering`으로 확정하는 절차
- Step 1의 `iterative block-wise optimization`
- Step 2의 `category-specialist agents + electricity/gas diagnostic agents + reality critic + orchestrator`
- 즉, `residual diagnosis`와 `domain-specialist parameter revision`을 명시적으로 연결하는 framework

### 논문 포지셔닝 메모
- 최신 문헌 기준으로도 `two-stage calibration` 자체는 novelty가 약하다.
- novelty는 `how the stages are structured`와 `how specialist multi-agent refinement is grounded in calibration categories`에서 만들어야 한다.
- 따라서 현재 논문은 `staged calibration framework`에 더해 `diagnosis-driven agent orchestration`을 핵심 contribution으로 밀어야 한다.
