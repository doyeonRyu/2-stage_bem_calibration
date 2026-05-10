# Introduction Citation Mapping

> Date: 2026-05-03
> Author: 유도연
> 목적: `drafts/1_introduction.md`의 (C) 마커별로 매칭할 citation 후보 정리.
> 기준: 2020년 이후 발표 + SCI/SCIE 학술지 (Elsevier, Springer, Taylor & Francis, Wiley, ASCE 등) 우선. MDPI / KCI는 보강용으로만 두고, 본문 인용은 SCI 등급 위주.

---

## 0. Introduction ↔ Related Works 분담 원칙

> 현재 `drafts/2_related_works.md`는 카테고리별로 대표 논문을 이미 깊게 다룬다. Introduction이 같은 인용을 1:1로 끌고 가면 두 섹션이 사실상 중복된다. 따라서 Introduction은 **분야 전체 motivation/gap의 큰 그림**만 짧게 인용하고, 카테고리별 detail은 Related Works로 미룬다.

| 역할       | Introduction                            | Related Works                  |
| -------- | --------------------------------------- | ------------------------------ |
| 인용 목적    | motivation / framing / 통계               | 카테고리별 비교·한계 분석                 |
| 인용 양     | 카테고리당 0~1편, 분야 review 1편                | 카테고리당 2~5편                     |
| 카테고리 구분  | 4개를 한 문장에 묶어 명명만                        | 4개 절로 분리해 깊이 다룸                |
| 한계점      | "search axis vs reasoning axis"로 1단락 일반화 | 카테고리별 한계 명시                    |

### Introduction 전용으로만 등장할 인용 (Related Works에 없음)
- **[29] González-Torres et al. (2022)** — 건물 부문 에너지 소비 통계 (C1-1)
- **[30] Allouhi et al. (2021)** — (C1-1) 보강
- **[31] Bracht et al. (2021)** — BIM의 비-기하 설정값 누락 (C1-3)
- **[32] Ciccozzi et al. (2023)** — (C1-3) 보강 (MDPI라 가능하면 생략)

### Introduction에서 한 번만 등장하고 Related Works가 깊게 다룰 인용
- **[1] Chong et al. (2021)** — calibration이 왜 필요·왜 어려운가 (C1-2, C2-1, C2-2) 통합 인용
- **[4] Pachano & Bandera (2021)** — "optimization / multi-step" 카테고리 대표 1편 (C2-3-1, C2-3-3)
- **[11] Sun et al. (2022)** — "rule/pattern-based" 카테고리 대표 1편 (C2-3-2)
- **[13] Lu et al. (2025)** — "multi-agent/LLM" 카테고리 대표 1편 (C2-3-4)

### Introduction에는 등장시키지 않고 Related Works 전용으로 둘 인용
- [2] Vera-Piazzini & Scarpa (2024) — Related Works §1
- [3] Guyot et al. (2020) — Related Works 보강
- [5] Gonzalez & Bandera (2022), [6] Baba (2022), [7] Guo (2021), [8] El Kounni (2023), [9] Jiang (2024), [10] Liang (2025) — Related Works §2~§3
- [12] Xiao & Xu (2024), [14] Xu et al. (2025) — Related Works §5
- [15]~[28] — Related Works 보강 또는 Variables Setting

> 결과적으로 Introduction이 인용하는 reference 번호는 **[1], [4], [11], [13], [29], [31]** + 옵션 [30] = 6~7편 수준으로 압축된다.

---

## 0-A. 빠른 매핑 표 (Introduction 본문 인용 기준)

| (C) 위치 | 핵심 주장                                       | Intro에서 실제 인용                                           | Related Works로 이관                          |
| ------ | ------------------------------------------- | ------------------------------------------------------- | ----------------------------------------- |
| 1.1    | 건물 부문이 전 세계 최종 에너지 소비의 약 1/3 차지             | [29] González-Torres et al. (2022) (+옵션 [30] Allouhi)    | —                                         |
| 1.2    | 정확한 BEM이 에너지 예측·효율·절감의 전제                  | [1] Chong et al. (2021)                                  | [2] Vera-Piazzini                         |
| 1.3    | BIM·도면은 형상·HVAC 위주, 비-기하 설정값 부재             | [31] Bracht et al. (2021)                                | (없음)                                       |
| 1.4    | 주요 입력의 불확실성·시간 변동 → calibration 필요성        | [1] Chong et al. (2021)으로 1.2와 묶어 처리                     | [9] Jiang, [15] Calama-González           |
| 2.1    | 실측 데이터 기반 BEM calibration의 당위성              | [1] Chong et al. (2021)으로 통합 (별도 인용 X)                   | [4] Pachano, [10] Liang                   |
| 2.2    | calibration의 노동 집약·사례 의존 한계                 | [1] Chong et al. (2021)                                  | [2] Vera-Piazzini, [3] Guyot              |
| 2.3.1  | optimization 카테고리 (대표 1편)                    | [4] Pachano & Bandera (2021)                             | [6] Baba, [7] Guo, [8] El Kounni, [9] Jiang |
| 2.3.2  | rule/pattern 카테고리 (대표 1편)                    | [11] Sun et al. (2022)                                   | [25] Lyu, [18] Guerrero                   |
| 2.3.3  | multi-step / staged 카테고리                     | [4] Pachano와 같은 인용으로 묶음                                  | [8] El Kounni, [10] Liang                 |
| 2.3.4  | multi-agent / LLM 카테고리 (대표 1편)               | [13] Lu et al. (2025)                                    | [12] Xiao, [14] Xu, [21][22] Zhang        |
| 2.4    | 자동화 calibration의 효율 개선                      | (별도 인용 없이 위 4개 카테고리로부터 합의된 사실로 서술)                       | [9] Jiang, [13] Lu, [16] Herbinger        |
| 2.5    | 한계: search axis vs reasoning axis 부재 (한 단락)  | 인용은 [4],[11],[13]으로 카테고리 신호만 재사용. 한계 자체는 Related Works가 분석 | 카테고리별 한계는 Related Works가 깊이 분석             |

---

## 1. (C) 마커별 상세 매핑

### Section 1. Problem Statement

#### (C1-1) 건물 분야는 에너지 소비가 큼

- **1차 인용**: González-Torres et al. (2022)
  - 핵심 수치: 전 세계 최종 에너지 소비의 약 1/3, CO₂ 배출의 약 1/4가 건물 부문에서 발생. HVAC가 건물 소비의 38% 차지.
  - 사용 문구 예시: *"Buildings account for roughly one-third of global final energy consumption and one-quarter of CO₂ emissions [29]."*
- **보강**: Allouhi et al. (2021, *Energy and Built Environment*) — decarbonisation 관점에서 동일 통계 재확인.

#### (C1-2) 에너지 예측·효율 향상·소비 절감을 위한 정확한 에너지 모델링이 필요

- **1차 인용**: Chong et al. (2021)
  - 핵심: BEM의 정확성이 retrofit 의사결정·운영 최적화·에너지 코드 검증의 전제임을 review에서 명시.
- **보강**: Vera-Piazzini & Scarpa (2024) — 동일 논지의 최신 review.

#### (C1-3) 도면·BIM이 기본적인 HVAC·설비 정보 위주이며, 에너지 시뮬레이션에 필요한 비-기하 설정값은 명시되지 않음

- **1차 인용**: Bracht et al. (2021, *Automation in Construction*)
  - 핵심: BIM-BEM 통합에서 형상 정보는 비교적 잘 전달되나 thermal property, schedule, set-point 등 비-기하 정보는 누락되거나 default로 채워진다고 분석.
- **보강**: Ciccozzi et al. (2023, *Energies*) — BIM-to-BEM 변환 시 thermal envelope의 missing element / gap 문제 review (※ MDPI라 보조용).

#### (C1-4) U-value / setpoint / schedule / density 등 주요 설정값이 명시되지 않거나 시간에 따라 변동

- **1차 인용**: Jiang et al. (2024, *Energy and Buildings*)
  - 핵심: BEM의 over-parameterization 문제, hourly-resolution에서 설정값 식별 불확실성 강조.
- **보강**: Calama-González et al. (2021, *Applied Energy*) — Bayesian calibration with uncertainty: 설계값과 실측값의 불일치, 변수 축소·우선순위화 필요성 근거.

---

### Section 2. Research Gap

#### (C2-1) 따라서 실제 에너지 소비 데이터에 맞춰 BEM 보정 과정이 필요

- **1차 인용**: Pachano & Bandera (2021)
  - 핵심: measured data 기반 multi-step calibration의 당위성과 절차.
- **보강**: Liang et al. (2025, *Applied Thermal Engineering*) — energy + indoor temperature 기반 two-step calibration.

#### (C2-2) BEM 보정 과정은 매우 노동 집약적·시간 소요·사례 의존

- **1차 인용**: Chong et al. (2021)
  - 핵심: review에서 calibration의 재현성·표준화 문제, 사례 의존 문제를 명시적으로 지적.
- **보강**:
  - Vera-Piazzini & Scarpa (2024) — 표준화·재현성 부재의 최신 비판.
  - Guyot et al. (2020, *Energy and Buildings*) — sub-hourly manual calibration이 얼마나 노동 집약적인지 보여주는 case.

#### (C2-3) 선행 연구 카테고리

##### (C2-3-1) GA 등 optimization

- **1차 인용**: Baba et al. (2022, *Building and Environment*)
  - 핵심: variance-based SA + multi-objective GA로 calibration.
- **보강**:
  - Guo et al. (2021, *Energy Reports*) — Slime Mold Optimization 기반 calibration.
  - El Kounni et al. (2023, *Energy and Buildings*) — Pymoo 기반 GA calibration two-stage.

##### (C2-3-2) Rule-based automation

- **1차 인용**: Sun et al. (2022, *Building Simulation*)
  - 핵심: monthly electricity / gas bias pattern을 보고 어떤 파라미터를 우선 조정할지 결정하는 rule-based 자동화 logic을 public dataset에 적용.
- **보강**: Lyu et al. (2021, *Journal of Building Engineering*) — schedule tuning + signed directed graph 기반 자동화.

##### (C2-3-3) Multi-step / Staged calibration

- **1차 인용**: Pachano & Bandera (2021)
- **보강**:
  - El Kounni et al. (2023) — detailed modeling + GA의 2-stage 구조.
  - Liang et al. (2025) — static/dynamic 파라미터 분리 two-step.

##### (C2-3-4) Multi-agent / LLM-based

- **1차 인용**: Lu et al. (2025, *iScience*)
  - 핵심: geometry → parameter configuration → calibration → retrofit까지 end-to-end LLM multi-agent. 실제 건물에서 ASHRAE Guideline 14 충족.
- **보강**:
  - Xiao & Xu (2024, *E&B*) — planner / researcher / advisor 역할 분리 multi-agent.
  - Xu et al. (2025, *E&B*) — orchestrator + specialist 계층의 dynamic multi-agent network (BEM-AI).
  - Zhang et al. (2025, *E&B*) — agentic workflow 기반 BEM 생성·디버깅.

#### (C2-4) 자동화된 calibration은 수동 calibration보다 빠르고 쉬움

- **1차 인용**: Jiang et al. (2024) — surrogate + Bayesian으로 high-resolution calibration 비용을 크게 줄였다는 정량 결과.
- **보강**:
  - Lu et al. (2025) — LLM multi-agent로 모델링 시간을 크게 절감했다고 보고.
  - Herbinger et al. (2023, *E&B*) — surrogate ANN으로 calibration 계산비용 절감.

#### (C2-5) 한계점 분석

##### (C2-5-1) 전통 최적화 / 단계별 보정: 구조화된 변수 설정·범위 탐색은 가능하나 reasoning 불가

- **1차 인용**: Baba et al. (2022) — SA + GA 기반이라 변수 선정 / 범위 설정은 명시적이지만, 잔차 패턴을 해석해 다음 단계를 결정하는 의사결정은 부재.
- **보강**:
  - Jiang et al. (2024) — Bayesian / surrogate 또한 residual 구조에 대한 도메인 reasoning을 직접 수행하지 않음.
  - Jeong & Byon (2024, *Applied Energy*) — bias correction과 heteroskedasticity까지 다루지만, 이 또한 통계적 처리이지 도메인 reasoning이 아님.

##### (C2-5-2) Pattern-based / Rule-based: 정적 if-then으로만 reasoning, 구조적 변수 범위 탐색 불가

- **1차 인용**: Sun et al. (2022) — pattern-based logic이 효과적이지만, 사전 정의된 if-then 매핑에 의존한다는 한계 자체가 본문에 드러남.
- **보강**: Guerrero Ramirez et al. (2025, *Building Simulation*) — clustering으로 진단을 확장했으나, 여전히 변수 search space 자체를 동적으로 구조화하지는 않음.

##### (C2-5-3) Multi-agent / LLM-based: 구조적 search 부재, reasoning은 가능하나 case별 자유 생성에 가까움

- **1차 인용**: Lu et al. (2025) — calibration parameter 집합과 범위를 LLM이 자연어 프롬프트에서 구성. 한계점으로 operational schedule이 calibration loop에 들어가지 않는다고 본문에 명시. 즉 search space의 구조적 보장이 없음을 자기 진술.
- **보강**:
  - Xu et al. (2025) — orchestrator + specialist 계층은 있으나 calibration 전용 구조는 아니며 dynamic 분해라 case별로 작업 구조가 달라짐.
  - Zhang et al. (2025, *E&B*) — agentic workflow가 case마다 자유롭게 plan을 생성, 결과적으로 재현성·구조적 일관성 부족.
  - Zhang et al. (2025, *Automation in Construction*) — agent schema / library 형식으로 모듈화를 시도하지만 calibration 변수 영역에 대한 사전 구조화는 다루지 않음.

---

## 2. 새로 추가한 후보 논문 (29~32)

> 기존 references.md의 1~28에 이어 번호를 붙임. 29, 30, 31은 SCI/SCIE이고, 32는 보조용(Energies, MDPI)이다.

### 29) A review on buildings energy information: Trends, end-uses, fuels and drivers
- 저자: M. González-Torres, L. Pérez-Lombard, J.F. Coronel, I.R. Maestre, D. Yan
- 학술지: Energy Reports
- 연도: 2022
- 권/페이지: Vol. 8, pp. 626–637
- DOI: `10.1016/j.egyr.2021.11.280`
- 요약:
  - 건물 부문이 전 세계 최종 에너지 소비의 약 1/3, CO₂ 배출의 약 1/4를 차지함을 정량적으로 정리.
  - HVAC 38%, DHW 13%, cooking 8%, lighting 5% 등 end-use별 분포 제공.
  - introduction의 (C1-1) "건물 분야의 큰 에너지 소비"를 직접 뒷받침하는 가장 최신·포괄적인 review.

### 30) Building green retrofit in China: Policies, barriers and recommendations / Present and future energy consumption of buildings: Challenges and opportunities towards decarbonisation
- 저자: A. Allouhi, T. Kousksou, A. Jamil, T. El Rhafiki, Y. Mourad, Y. Zeraouli (Allouhi et al.)
- 학술지: Energy and Built Environment
- 연도: 2021
- DOI: `10.1016/j.enbenv.2021.06.001`
- 요약:
  - decarbonisation 관점에서 건물 부문의 에너지 소비 비중과 향후 절감 잠재력을 review.
  - 30~40% 수준의 건물 부문 에너지 점유 통계와 그 배경 (urbanisation, HVAC 확대) 정리.
  - introduction (C1-1) 보강용. González-Torres et al.과 함께 묶어 인용 가능.

### 31) A metamodel for building information modeling-building energy modeling integration in early design stage
- 저자: A.S. Bracht, R.C. Ruschel, A.L. Andriamamonjy(가제) — *원문 저자 메타데이터 재확인 필요*
- 학술지: Automation in Construction
- 연도: 2021
- 권/번호: Vol. 121
- DOI: `10.1016/j.autcon.2020.103425`
- 요약:
  - BIM-to-BEM 변환 과정에서 형상은 비교적 잘 전달되지만 thermal property, schedule, internal load, set-point 등 비-기하 데이터의 손실·default 채움이 발생한다고 분석.
  - early-design 단계에서 누락 정보를 메타모델 구조로 묶어 BEM 입력으로 전달하는 framework 제안.
  - introduction (C1-3) "BIM은 HVAC·설비 위주, 주요 설정값 부재"를 직접 뒷받침.
- 비고: 저자/DOI는 인용 직전 원문 PDF로 1회 더 검증 권장.

### 32) BIM to BEM for Building Energy Analysis: A Review of Interoperability Strategies
- 저자: G. Ciccozzi, T. de Rubeis, D. Paoletti, D. Ambrosini
- 학술지: Energies (MDPI)
- 연도: 2023
- 권/번호: 16(23), 7845
- DOI: `10.3390/en16237845`
- 요약:
  - 2004–2023 BIM–BEM interoperability 전략 4종 (real-time, MVD, middleware, standardized exchange) 비교 review.
  - thermal envelope의 missing element, 잘못된 geometry, 비-기하 thermal property 손실 사례 정리.
- 비고: MDPI라 본문 1차 인용으로는 권장하지 않고, 도면/BIM의 정보 누락을 보강 설명할 때만 사용.

---

## 3. 인용 사용 시 주의

1. (C1-1) 건물 에너지 소비 수치는 **세계 평균 vs. 국가별** 통계가 다르므로 본문에서 한 통계만 인용하고 출처를 명확히 표기.
2. (C1-3) BIM-BEM gap 인용은 **형상 정보 손실** 보다 **비-기하 / 설정값 손실** 쪽 메시지를 골라야 본 논문 calibration 동기와 직접 연결됨. Bracht et al. (2021) 본문에서 thermal property·schedule 누락을 다루는 절을 우선 발췌.
3. (C2-3-3, C2-5-1) Pachano & Bandera (2021), El Kounni et al. (2023), Liang et al. (2025), Baba et al. (2022)는 모두 staged / multi-objective optimization이므로, 같은 문장에서 너무 한꺼번에 묶지 말고 (a) 단계 분리 근거 (b) reasoning 부재 근거로 역할을 나눠 인용.
4. (C2-3-4, C2-5-3) Lu et al. (2025)는 자기 한계점으로 operational schedule이 빠진다는 점을 명시하고 있어서, **자유 생성 한계** 인용에서 이 문장을 직접 paraphrase하면 매우 강하게 차별화 가능.
5. 새로 추가한 29, 30, 31의 메타데이터(특히 31)는 **본문 인용 직전 원문 PDF로 한 번 더 검증** 후 references.md에 정식 추가.

---

## 4. 작업 흐름

1. 본 파일에서 (C) 매핑을 확정한 뒤, 본문 `1_introduction.md` 개조식을 문장형으로 다시 쓸 때 [번호] 형식으로 인용.
2. 정식 인용 직전 29, 30, 31의 DOI / 저자 / 페이지 재확인 → `background/references.md`에 동일 번호로 추가.
3. 1차 인용은 SCI 본저널 위주로 사용하고, 보강 인용은 같은 문단 안에서 "; e.g., [boost1, boost2]" 형식으로 묶음 처리.
Sources:  
- https://www.sciencedirect.com/science/article/pii/S235248472101427X  
- https://www.sciencedirect.com/science/article/abs/pii/S0926580520310475  
- https://www.mdpi.com/1996-1073/16/23/7845  
- https://www.iea.org/energy-system/buildings