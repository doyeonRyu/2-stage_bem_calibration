# References

## 작업 상태

- 상태: draft

## 참고문헌 목록

# Background Literature 

- 포함 기준
  - 2020년 이후 발표
  - 실제 존재하는 논문
  - calibration framework, multi-step / two-step calibration, high-resolution calibration, multi-agent / LLM-based building energy workflow와 직접 연결되는 연구 우선

## 1. Review / Positioning

### 1) Calibrating building energy simulation models: A review of the basics to guide future work
- 저자: Adrian Chong, Yaonan Gu, Hongyuan Jia
- 학술지: Energy and Buildings
- 연도: 2021
- DOI: `10.1016/j.enbuild.2021.111533`
- 요약:
  - building energy simulation calibration 분야의 체계적 리뷰다.
  - 자동 calibration에서는 optimization과 Bayesian 접근이 중심이라고 정리한다.
  - calibration 입력/출력, 데이터 해상도, 평가 지표, 재현성 이슈를 정리해 후속 연구의 기준점을 제공한다.
  - 현재 연구에서는 `왜 재현 가능한 framework가 필요한가`, `왜 목적함수와 입출력 정의가 중요하나`를 뒷받침하는 배경 문헌이다.

### 2) Building energy model calibration: A review of the state of the art in approaches, methods, and tools
- 저자: Ofelia Vera-Piazzini, Massimiliano Scarpa
- 학술지: Journal of Building Engineering
- 연도: 2024
- DOI: `10.1016/j.jobe.2023.108287`
- 요약:
  - calibration 방법론, 데이터 수집, 시뮬레이션 소프트웨어, 검증 절차를 폭넓게 리뷰한다.
  - variability analysis와 reproducibility 문제가 여전히 중요하다고 지적한다.
  - 표준화된 절차의 필요성을 강조해, 현재 연구의 `framework contribution`을 정당화하기 좋은 최신 리뷰다.

## 2. Recent Calibration Methodologies

### 3) Building energy model calibration: A detailed case study using sub-hourly measured data
- 저자: Dimitri Guyot, Florine Giraud, Florian Simon, David Corgier, Christophe Marvillet, Brice Tremeac
- 학술지: Energy and Buildings
- 연도: 2020
- DOI: `10.1016/j.enbuild.2020.110189`
- 요약:
  - 5분 간격 실측 데이터를 활용한 고해상도 manual calibration 사례다.
  - 월별 통계지표만으로는 모델 성능을 충분히 설명할 수 없고, 동적 물리 분석이 필요하다고 주장한다.
  - 현재 연구의 관점에서는 `월별 에너지 오차 외에 패턴 해석과 동적 진단이 필요하다`는 근거가 된다.

### 4) Multi-step building energy model calibration process based on measured data
- 저자: José Eduardo Pachano, Carlos Fernández Bandera
- 학술지: Energy and Buildings
- 연도: 2021
- DOI: `10.1016/j.enbuild.2021.111380`
- 요약:
  - measured data 기반의 multi-step, optimization-driven calibration 절차를 제안한다.
  - EnergyPlus와 jEPlus를 사용해 HVAC 파라미터를 조정하고, indoor temperature, heat production, electric consumption을 함께 검증한다.
  - 독립 테스트 기간에서도 강건성을 확인했다.
  - 현재 연구와 가장 직접적으로 닿는 최신 선행 중 하나로, `multi-step calibration`과 `measured data 기반 validation`의 강한 근거다.

### 5) A building energy models calibration methodology based on inverse modelling approach
- 저자: Vicente Gutiérrez González, Carlos Fernández Bandera
- 학술지: Building Simulation
- 연도: 2022
- DOI: `10.1007/s12273-022-0900-5`
- 요약:
  - EnergyPlus의 `HybridModel:Zone`를 활용해 measured indoor temperature만으로 infiltration과 internal mass를 추정하는 inverse modelling 기반 calibration 방법을 제안한다.
  - baseline 대비 실측 적합도를 의미 있게 개선했다고 보고한다.
  - 현재 연구에서 Step 0 이후 후보 변수를 넓게 두고, 실제 데이터로 식별 가능한 변수부터 정교화하려는 방향과 잘 맞는다.

### 6) Calibration of building model based on indoor temperature for overheating assessment using genetic algorithm: Methodology, evaluation criteria, and case study
- 저자: Fuad Mutasim Baba, Hua Ge, Radu Zmeureanu, Liangzhu Wang
- 학술지: Building and Environment
- 연도: 2022
- DOI: `10.1016/j.buildenv.2021.108518`
- 요약:
  - indoor hourly temperature를 기준으로 여러 공간을 동시에 calibration하는 multi-objective genetic algorithm 접근이다.
  - variance-based sensitivity analysis로 중요한 파라미터를 먼저 추리고, 그 후 calibration을 수행한다.
  - 평가 기준을 새로 정의해 calibrated model selection을 수행했다.
  - 현재 연구의 `민감도 분석 -> 후보 축소 -> 단계적 calibration` 흐름과 잘 연결된다.

### 7) Energy model calibration in an office building by an optimization-based method
- 저자: Jinjin Guo, Runzong Liu, Tongshui Xia, Somayeh Pouramini
- 학술지: Energy Reports
- 연도: 2021
- DOI: `10.1016/j.egyr.2021.07.031`
- 요약:
  - office building 사례에서 optimization-based calibration을 수행한 논문이다.
  - Slime Mold Optimization을 이용해 hourly precision을 확보했고, calibrated model의 MBE와 CV(RMSE)를 제시했다.
  - novelty 자체는 상대적으로 약하지만, 최신 optimization-based calibration 사례로서 baseline literature에 넣을 수 있다.

### 8) Building energy model automated calibration using Pymoo
- 저자: Abdelkader El Kounni, Abdelkader Outzourhit, Hicham Mastouri, Hassan Radoine
- 학술지: Energy and Buildings
- 연도: 2023
- DOI: `10.1016/j.enbuild.2023.113524`
- 요약:
  - detailed modeling 후 optimization-based calibration을 수행하는 two-stage structure를 제안한다.
  - 1단계는 infiltration과 convective heat exchange를 포함한 detailed modeling, 2단계는 Pymoo 기반 유전알고리즘 calibration이다.
  - 현재 연구의 `Step 0 baseline model construction + Step 1 automated calibration` 구조와 가장 유사한 최근 논문 중 하나다.

### 9) A deep learning-based Bayesian framework for high-resolution calibration of building energy models
- 저자: Gang Jiang, Yixing Chen, Zhe Wang, Kody Powell, Blake Billings, Jianli Chen
- 학술지: Energy and Buildings
- 연도: 2024
- DOI: `10.1016/j.enbuild.2024.114755`
- 요약:
  - hourly / sub-hourly resolution calibration을 위해 deep learning surrogate와 Bayesian calibration을 결합한 framework다.
  - pre-calibration, LSTM surrogate, likelihood simplification을 통해 계산비용을 줄이고 정확도를 높였다.
  - 현재 연구와 직접 같은 방법은 아니지만, `high-resolution calibration`, `pre-calibration`, `over-parameterization 완화`라는 문제의식이 매우 유사하다.

### 10) A two-step calibration framework for accurate building energy simulations: Integrating energy and indoor temperature data
- 저자: Xiguan Liang, Jisoo Shim, Doosam Song
- 학술지: Applied Thermal Engineering
- 연도: 2025
- DOI: `10.1016/j.applthermaleng.2025.128474`
- 요약:
  - energy consumption만이 아니라 indoor temperature를 함께 쓰는 two-step calibration framework를 제안한다.
  - 1단계에서는 unoccupied period에서 static parameter를, 2단계에서는 occupied period에서 occupant behavior와 internal gains 같은 dynamic parameter를 조정한다.
  - 현재 연구의 staged logic과 유사하지만, agent 구조보다는 `정적-동적 파라미터 분리 calibration`에 가깝다.
  - 최신 two-step calibration 사례로서 직접 비교 문헌으로 유용하다.

## 3. Recent Pattern-Based / Automated Logic

### 11) Application and evaluation of a pattern-based building energy model calibration method using public building datasets
- 저자: Kaiyu Sun, Tianzhen Hong, Janghyun Kim, Barry Hooper
- 학술지: Building Simulation
- 연도: 2022
- DOI: `10.1007/s12273-022-0891-2`
- 요약:
  - 기존 pattern-based calibration logic을 public building dataset에 적용하고 평가한 논문이다.
  - monthly electricity/gas bias pattern을 바탕으로 어떤 파라미터를 우선 조정할지 결정하는 자동화 로직을 확장 검증했다.
  - 현재 Step 2의 `diagnostic -> specialist routing`과 가장 철학적으로 가까운 최근 문헌이다.
  - 차이는 이 논문이 규칙 기반 자동 조정 로직인 반면, 현재 연구는 이를 category-specialist agent 구조로 일반화하려는 점이다.

## 4. Recent Multi-Agent / LLM-Based Building Energy Research

### 12) Exploring automated energy optimization with unstructured building data: A multi-agent based framework leveraging large language models
- 저자: Tong Xiao, Peng Xu
- 학술지: Energy and Buildings
- 연도: 2024
- DOI: `10.1016/j.enbuild.2024.114691`
- 요약:
  - 비정형 건물 데이터를 활용해 energy optimization 업무를 자동화하는 LLM 기반 multi-agent framework를 제안한다.
  - planner, researcher, advisor 역할의 agent를 두고 building information processing, performance diagnosis, retrofit recommendation의 3단계를 수행한다.
  - 현재 연구와 직접 같은 calibration 프레임워크는 아니지만, `agent 역할 분리`, `diagnosis`, `knowledge retrieval`이라는 구조적 아이디어가 매우 유사하다.

### 13) Automated building energy modeling for energy retrofits using a large language model-based multi-agent framework
- 저자: Jie Lu, Zeyu Zheng, Max Langtry, Monty Jackson, Yang Zhao, Chenxin Feng, Ruqian Zhang, Chaobo Zhang, Jian Zhang, Ruchi Choudhary
- 학술지: iScience
- 연도: 2025
- DOI: `10.1016/j.isci.2025.113867`
- 요약:
  - geometry modeling, parameter configuration, calibration, retrofit evaluation까지 end-to-end 자동화한 LLM multi-agent framework다.
  - real building에서 calibration benchmark를 달성했고, 모델링 시간을 크게 줄였다고 보고한다.
  - 현재 연구와 가장 가까운 최근 multi-agent 문헌이지만, 초점은 전체 BEM workflow 자동화이고, calibration 내부를 `category-specialist + diagnostic critics`로 조직하지는 않는다.

### 14) Development of a dynamic multi-agent network for building energy modeling: A case study towards scalable and autonomous energy modeling
- 저자: Weili Xu, Hanlong Wan, Chrissi Antonopoulos, Supriya Goel
- 학술지: Energy and Buildings
- 연도: 2025
- DOI: `10.1016/j.enbuild.2025.116712`
- 요약:
  - BEM-AI라는 dynamic multi-agent framework를 제안하며, A2A와 MCP 기반으로 specialist agent coordination을 구성한다.
  - building energy modeling workflow를 동적으로 분해하고, task orchestration을 통해 효율성을 높이는 데 초점을 둔다.
  - calibration 전용 논문은 아니지만, 현재 연구의 Step 2에서 구상하는 `orchestrator + specialists` 계층 구조와 가장 닮은 최신 건물 에너지 논문이다.

## 5. 현재 프레임워크와의 연결

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

## 6. 추가 후보 논문 (2020+ / non-MDPI, non-KCI 우선)

> 목적: introduction / literature review / variables setting에서 기존 12편 반복을 줄이기 위한 보강용 후보군.
> 원칙: 2020년 이후, 실제 존재 확인, 가능하면 Elsevier / Springer / Taylor & Francis / iScience 계열 우선.

### 6.1 Introduction / Positioning 보강

#### 15) Bayesian calibration of building energy models for uncertainty analysis through test cells monitoring
- 저자: Carmen Maria Calama-Gonzalez, Phil Symonds, Giorgos Petrou, Rafael Suarez, Angel Luis Leon-Rodriguez
- 학술지: Applied Energy
- 연도: 2021
- DOI: `10.1016/j.apenergy.2020.116118`
- 왜 추가하나:
  - calibration과 uncertainty quantification을 함께 다루는 비교적 정석적인 Applied Energy 논문이다.
  - sensitivity analysis가 calibration 계산 부담을 줄이는 핵심 단계라는 점을 분명히 보여준다.
  - introduction에서는 `왜 calibration 전에 변수 축소/우선순위화가 필요한가`를 받쳐주기 좋다.

#### 16) Building energy model calibration using a surrogate neural network
- 저자: Florent Herbinger, Colin Vandenhof, Michael Kummert
- 학술지: Energy and Buildings
- 연도: 2023
- DOI: `10.1016/j.enbuild.2023.113057`
- 왜 추가하나:
  - hourly 데이터와 surrogate ANN을 결합해 calibration 계산비용과 식별력을 동시에 다룬다.
  - weather와 schedule을 함께 입력해야 calibration이 더 robust해진다는 메시지가 분명하다.
  - introduction과 literature review 모두에서 `high-resolution / computational burden / surrogate-based calibration` 축 보강에 유용하다.

#### 17) Calibration of building energy computer models via bias-corrected iteratively reweighted least squares method
- 저자: Cheoljoon Jeong, Eunshin Byon
- 학술지: Applied Energy
- 연도: 2024
- DOI: `10.1016/j.apenergy.2024.122753`
- 왜 추가하나:
  - 단순 parameter tuning이 아니라 bias correction과 heteroskedasticity까지 calibration 문제에 포함시킨다.
  - `모델-실측 간 residual 구조를 해석해야 한다`는 현재 논문의 diagnostic orientation과 잘 맞는다.
  - introduction에서 `단순 오차 최소화만으로는 부족하다`는 문제의식 강화에 적합하다.

### 6.2 Literature Review 보강: Calibration / Diagnostic Logic 계층

#### 18) Calibrated models for effective clustering: Discriminating operation schedules in occupied buildings
- 저자: Karla Guerrero Ramirez, Cristina Nuevo-Gallardo, Jesus Miguel Santamaria Ulecia, Beatriz Montalban Pozas, Carlos Fernandez Bandera
- 학술지: Building Simulation
- 연도: 2025
- DOI: `10.1007/s12273-024-1200-z`
- 왜 추가하나:
  - calibrated white-box model의 출력에 clustering을 적용해 operation schedule, free oscillation, non-recurrent event를 식별한다.
  - Step 2에서 구상하는 `residual/pattern diagnosis -> specialist revision` 논리와 상당히 가깝다.
  - 기존 Sun et al. (2022)가 monthly pattern 중심이라면, 이 논문은 operation pattern / clustering 쪽으로 확장된 근거가 된다.

#### 19) UBEM calibration method by energy consumption disaggregation using a change-point model
- 저자: Hye Gi Kim, Sun Sook Kim
- 학술지: Journal of Building Performance Simulation
- 연도: 2025
- DOI: `10.1080/19401493.2024.2412135`
- 왜 추가하나:
  - 총 에너지 사용량을 heating / cooling / baseload로 분해한 뒤 calibration하는 접근이다.
  - 단일 aggregate error보다 `구성요소별 residual 해석`이 더 유의미하다는 근거로 활용할 수 있다.
  - 비록 UBEM 맥락이지만, diagnostic decomposition 논리 때문에 Step 2 서술에 직접 연결 가능하다.

### 6.3 Literature Review 보강: Multi-agent / LLM Workflow 계층

#### 20) EPlus-LLM: A large language model-based computing platform for automated building energy modeling
- 저자: Gang Jiang, Zhihao Ma, Liang Zhang, Jianli Chen
- 학술지: Applied Energy
- 연도: 2024
- DOI: `10.1016/j.apenergy.2024.123431`
- 왜 추가하나:
  - 자연어를 EnergyPlus 모델로 직접 변환하는 auto-modeling platform이다.
  - calibration 자체보다는 Step 0의 baseline model generation / parameter configuration automation 근거로 적합하다.
  - 기존 multi-agent 문헌과 달리 `LLM이 BEM 입력 구성 자체를 어떻게 자동화하는가`를 보여준다.

#### 21) Automatic building energy model development and debugging using large language models agentic workflow
- 저자: Liang Zhang, Vitaly Ford, Zhelun Chen, Jianli Chen
- 학술지: Energy and Buildings
- 연도: 2025
- DOI: `10.1016/j.enbuild.2024.115116`
- 왜 추가하나:
  - LLM planning 기반 agentic workflow로 EnergyPlus 모델 생성과 debugging을 자동화한다.
  - 단순 Q&A형 LLM이 아니라 planner-style workflow를 다뤄, orchestrator 개념의 근거가 된다.
  - current framework의 `orchestrator + specialist sequence`를 설명할 때 Xiao/Xu, Xu et al. 외 보강 문헌으로 좋다.

#### 22) Large language model-based agent Schema and library for automated building energy analysis and modeling
- 저자: Liang Zhang, Xiaoqin Fu, Yanfei Li, Jianli Chen
- 학술지: Automation in Construction
- 연도: 2025
- DOI: `10.1016/j.autcon.2025.106244`
- 왜 추가하나:
  - building energy agent를 재사용 가능한 schema와 library 관점에서 정리한 논문이다.
  - 현재 논문의 agent 구조를 `임의의 프롬프트 집합`이 아니라 `역할이 분명한 모듈형 체계`로 기술할 때 유용하다.
  - literature review에서 `agent architecture formalization` 축을 보강한다.

### 6.4 Variables Setting 보강: 변수 계층별 근거

#### 23) Evaluating the sensitivity and robustness of occupancy models for building energy simulation during design
- 학술지: Building and Environment
- 연도: 2024
- DOI: `10.1016/j.buildenv.2024.111739`
- 핵심 변수 근거:
  - occupancy density
  - start / end time
  - schedule fractions
- 왜 추가하나:
  - occupancy 관련 변수 중 무엇이 실제 hourly energy prediction에 민감한지 직접 보여준다.
  - current variables setting의 `occupancy / schedule` 계층에 최신 근거를 추가할 수 있다.

#### 24) Occupancy and equipment usage prototype schedules for building energy simulations of office building types in China
- 저자: Zefeng Huang, Zhonghua Gou
- 학술지: Journal of Building Performance Simulation
- 연도: 2025
- DOI: `10.1080/19401493.2024.2422919`
- 핵심 변수 근거:
  - occupancy schedule
  - equipment schedule
  - lighting / HVAC operation schedule
- 왜 추가하나:
  - 표준 schedule 대신 building-type-specific schedule을 써야 에너지 결과가 크게 달라질 수 있음을 보인다.
  - office building 맥락이라 현재 연구와도 잘 맞는다.
  - `운영 스케줄은 calibration 변수 후보에서 빼면 안 된다`는 근거로 매우 직접적이다.

### 6.5 Variables Setting 보강: HVAC scheduling / setback 근거

#### 25) An automated process to calibrate building energy model based on schedule tuning and signed directed graph method
- 저자: Yan Lyu, Yiqun Pan, Tao Yang, Yuming Li, Zhizhong Huang, Risto Kosonen
- 학술지: Journal of Building Engineering
- 연도: 2021
- DOI: `10.1016/j.jobe.2020.102058`
- 핵심 변수 근거:
  - HVAC operation schedule tuning
  - short-term monitored schedule correction
  - schedule-based calibration logic
- 왜 추가하나:
  - calibration 과정에서 schedule tuning 자체를 핵심 contribution으로 둔 드문 논문이다.
  - internal load schedule과 별도로 `운전 스케줄`을 보정할 수 있다는 직접 근거를 제공한다.
  - 현재 논문에서 `HVAC availability / scheduling`을 2차 채택 변수로 넣는 가장 강한 calibration 문헌이다.

#### 26) Calibrated models for effective clustering: Discriminating operation schedules in occupied buildings
- 저자: Karla Guerrero Ramirez, Cristina Nuevo-Gallardo, Jesus Miguel Santamaria Ulecia, Beatriz Montalban Pozas, Carlos Fernandez Bandera
- 학술지: Building Simulation
- 연도: 2025
- DOI: `10.1007/s12273-024-1200-z`
- 핵심 변수 근거:
  - HVAC system operation schedule
  - free oscillation period
  - non-recurrent operational event
- 왜 추가하나:
  - calibrated model로부터 HVAC operation schedule을 식별하는 접근을 제시한다.
  - Step 2의 진단뿐 아니라, `HVAC schedule`이 실질적인 분석 대상이 될 수 있음을 뒷받침한다.

#### 27) Investigating the influence of uncertainty on office building energy simulation through occupant-centric control and thermal comfort integration
- 학술지: Energy and Buildings
- 연도: 2024
- DOI: `10.1016/j.enbuild.2024.114741`
- 핵심 변수 근거:
  - occupancy schedule
  - setpoint schedule
  - occupant-driven HVAC operation
- 왜 추가하나:
  - occupied/unoccupied 상태와 연계된 setpoint schedule의 에너지 민감도를 보여준다.
  - `thermostat setback schedule`을 독립적인 control/schedule 변수로 다루는 근거로 적절하다.

#### 28) Nationwide HVAC energy-saving potential quantification for office buildings with occupant-centric controls in various climates
- 학술지: Applied Energy
- 연도: 2020
- DOI: `10.1016/j.apenergy.2020.115727`
- 핵심 변수 근거:
  - unoccupied temperature setpoint reset
  - minimum outdoor airflow reset
  - occupancy-driven HVAC operation
- 왜 추가하나:
  - calibration 논문은 아니지만, occupied/unoccupied HVAC control schedule이 에너지 성능에 강하게 작용함을 보여준다.
  - `availability / setback / OA reset`을 하나의 HVAC scheduling 계층으로 묶는 실무적 근거가 된다.

### 6.6 실무적 우선순위 메모

- introduction에 바로 넣기 좋은 논문:
  - 15, 16, 17
- literature review의 calibration methodology 확장용:
  - 16, 17, 18, 19
- Step 2 agent / orchestration 정당화용:
  - 18, 21, 22
- variable-setting 근거 보강용:
  - 15, 23, 24, 25, 27
- HVAC scheduling / setback 변수 정당화용:
  - 25, 26, 27, 28
- 현재 12편과 중복 논지이지만 더 최신/다른 각도를 주는 논문:
  - 16, 17, 18, 20, 21

## Sources
- Energy and Buildings / Elsevier:
  - https://www.sciencedirect.com/science/article/pii/S0378778821008173
  - https://www.sciencedirect.com/science/article/pii/S0378778820300505
  - https://www.sciencedirect.com/science/article/pii/S0378778821006642
  - https://www.sciencedirect.com/science/article/pii/S0378778823007545
  - https://www.sciencedirect.com/science/article/pii/S0378778824008715
  - https://www.sciencedirect.com/science/article/pii/S0378778824008077
  - https://www.sciencedirect.com/science/article/pii/S0378778825014422
- Other journal sources:
  - https://www.sciencedirect.com/science/article/pii/S2352710223024701
  - https://www.sciencedirect.com/science/article/pii/S0360132321009136
  - https://www.sciencedirect.com/science/article/pii/S2352484721004959
  - https://www.sciencedirect.com/science/article/pii/S1359431125030662
  - https://link.springer.com/article/10.1007/s12273-022-0900-5
  - https://buildings.lbl.gov/publications/application-and-evaluation-pattern
  - https://www.sciencedirect.com/science/article/pii/S2589004225021285
- Author metadata cross-check:
  - https://www.ornl.gov/publication/deep-learning-based-bayesian-framework-high-resolution-calibration-building-energy
  - https://pure.skku.edu/en/publications/a-two-step-calibration-framework-for-accurate-building-energy-sim/
  - https://research-hub.nrel.gov/en/publications/application-and-evaluation-of-a-pattern-based-building-energy-mod-2
  - https://www.researchgate.net/publication/397805352_Development_of_a_dynamic_multi-agent_network_for_building_energy_modeling_A_case_study_towards_scalable_and_autonomous_energy_modeling
  - https://bspace.buid.ac.ae/handle/1234/2973
