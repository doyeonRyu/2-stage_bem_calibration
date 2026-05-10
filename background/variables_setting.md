# Variables Setting

> 목적: Step 0 Pre-calibration baseline & literature-grounded variable selection 단계의 *채택 변수 근거*를 정리한다.
> 입력: refs/ 12편 PDF + 외부 출처(Reddy RP-1051, ASHRAE G14, Ramos Ruiz/Fernández Bandera, Coakley 2014) + HVAC scheduling 보강 문헌.
> 출력 단위: 카테고리 없이 **flat 변수 목록** (사용자 결정).
> 작성일: 2026-04-29
> 상태: draft (round 1 — 7편 + 외부 4건 추출 완료, Vera-Piazzini 후속 정리 TODO)

---

## 1. Per-source 변수 추출 (faithful transcription)

> 각 출처의 calibration target / decision variable / search space 원본 표기를 가능한 그대로 옮겨 적는다. 출처별 추출 결과는 정량 비교 전 단계의 raw 자료이다.

### 1.1 Pachano and Bandera (Energy and Buildings, 2021) — Multi-step calibration

- 보정 단위: HVAC system 분해 (HP group -> AHU -> Baseboard radiators)
- SA 방법: 해당 논문 명시 SA 없음 (multi-step engineering decomposition)
- Stage 1 변수 (Heat Pump group, Table 5):
  - Rated Heating Capacity (W) — baseline 63440 -> calibrated 50752
  - Rated COP (W/W) — 5.310 -> 4.300
  - Rated Sensible Heat Ratio (—) — 0.737 -> 0.788
  - Rated Evaporator Air Flow Rate (m³/s) — 5.193 -> 3.000
  - Rated Condenser Water Flow Rate (m³/s) — 0.002 -> 0.018
  - HP-01~04 Off Cycle Loss Coefficient to Ambient Temperature (W/K) — 0 -> 750–900
  - Use Side Design Flow Rate (m³/s)
  - Indirect Water Heating Recovery Time (h)
  - HP Biquadratic Capacity Curve (6 coefficients)
  - HP Biquadratic COP Curve (6 coefficients)
  - Buffer Tank Off Cycle Loss Coefficient (W/K)
  - Buffer Tank Source Side Design Flow Rate (m³/s)
  - Buffer Tank Indirect Water Heating Recovery Time (h)
- Stage 2 변수 (AHU + Baseboard, Table 6):
  - Plant Loop Library Building Loop (m³)
  - AHU Minimum Outdoor Air Flow Rate (m³/s)
  - AHU U-Factor Times Area Value (W/K)
  - AHU Maximum Water Flow Rate (m³/s)
  - AHU Sensible/Latent Air-to-Air Heat Recovery (75%/100% Heating Air Flow) — 4 vars
  - Baseboard per zone × 10 zones × 2 vars (Maximum Water Flow Rate, U-Factor Times Area Value) = 20 vars
- 메모: 매우 HVAC-heavy. Envelope 변수 거의 없음.

### 1.2 El Kounni et al. (Energy and Buildings, 2023) — Pymoo GA

- 보정 단위: zone별 독립 최적화 (zone 1, zone 3 각각)
- SA 방법: "Sensitivity analysis is used to limit the number of features" — 구체 방법 비명시
- 채택 변수 (zone당 4개):
  - Leakage area (cm²) — infiltration model 입력
  - Thermal bridge (kJ/h·K)
  - Convective heat gains/losses (kJ/h·K)
  - Radiant heat gains/losses (kJ/h·K)
- 메모: 매우 envelope/airtightness 중심. 4-variable approach (Ramos Ruiz 계열과 유사).

### 1.3 Guo et al. (Energy Reports, 2021) — Optimization-based (SMO)

- 보정 단위: occupant behavior 시간별 schedule
- SA 방법: 명시 없음 (의도적으로 광범위)
- Decision Variables (Table 4, total 100):
  - Occupation level: V1–V24 (24 hourly vars)
  - Cooling setpoint: V25–V26 (2 vars)
  - Heating setpoint: V27–V28 (2 vars)
  - Load intensity of equipment: V29–V52 (24 hourly vars)
  - Load intensity of lighting: V53–V76 (24 hourly vars)
  - Level of infiltration: V77–V100 (24 hourly vars)
- 메모: 운영 패턴(occupant·schedule·infiltration) 100% 중심, envelope·HVAC 변수 없음.

### 1.4 Baba et al. (Building and Environment, 2022) — VBSA + MOGA

- 보정 단위: 건물 전체 (4 rooms 동시 보정)
- SA 방법: SOBOL global variance-based; 임계값 sensitivity index > 0.05
- 후보 변수 (Table 2, school closed period):
  - Wall U-Value (W/m²K) — 0.40–0.70 (range 1) / 0.20–0.40 (range 2)
  - Roof U-Value (W/m²K) — 0.23–0.33 / 0.15–0.23
  - Air Infiltration (@ACH50) — 3.5–8.5 / 1.5–3.5
  - Window U-Value (W/m²K) — 2.20–3.00
  - Window SHGC — 0.60–0.76
  - Solar reflectance of interior diffusing roll blinds — 0.3–0.9
  - Thermal mass of exterior wall (kJ/m²K) — 150–350
  - Thermal mass of internal floors and roof (kJ/m²K) — 150–350
- 후보 변수 (Table 2, school open period 추가):
  - Occupancy load (number of students) — 20–25
  - Lighting load (W/m²) — 9–16
  - Equipment load (W/m²) — 2–5
  - Maximum air change rate from NV (ACH) — 0–15
  - NV Setpoint (°C) — 20–24
  - Interior shading opening ratio (NW rooms %) — 10–90
  - Interior shading opening ratio (SE rooms %) — 10–90
- 채택 변수 (SA 후, 최종 7개): 4 interior shadings, air infiltration, wall U-value, roof U-value (Table 5 컨텍스트)
- 메모: ≈15 후보 -> SA 후 7개로 축소.

### 1.5 Liang et al. (Applied Thermal Engineering, 2025) — Two-step PSO calibration

- 보정 단위: 건물 전체, 2단계 (정적 -> 동적)
- SA 방법: Morris (1,300 sample combinations); μ* 기준 영향도 ranking
- Step 1 (정적, 비점유, Table 4 No. 1–5):
  - Wall_U (W/m²K) — 0.2–1.006
  - Window_U (W/m²K) — 1.5–3.372
  - Roof_U (W/m²K) — 0.1–0.450
  - Floor_U (W/m²K) — 0.1–0.581
  - Infiltration (1/h) — 0.24–2.0
- Step 2 (동적, 점유, Table 4 No. 6–12):
  - Equipment (W/m²) — 4.0–11.77
  - Light (W/m²) — 5.0–20.0
  - Occupant (W/m²) — 10.0–100.0
  - Window Open Schedule (h/d) — 12:00~01:00
  - Setpoint Schedule (°C) — 24–27
  - T_Dead_band (°C) — 1–2
  - Time-step (h) — 0.25–1
- Morris SA 결과 (μ* 기준 ranking, Table 5): Setpoint 54.97 ≫ Wall_U 28.31 ≫ Infiltration 19.51 > Light 6.25 ≈ T_Dead_band 5.99 > Window_U 4.70 > Roof_U 3.08 > Occupant 2.95 ≈ Equipment 2.33 > Floor_U 1.19 > Window_Open 0.75 ≈ Time_step 0.17
- 메모: 12 변수 모두 calibration에 사용 (낮은 SA 변수도 secondary 분석용으로 유지).

### 1.6 Jiang et al. (Energy and Buildings, 2024) — DL-Bayesian high-resolution calibration

- 보정 단위: 시간(hourly) 해상도 EnergyPlus + LSTM surrogate + Bayesian inference
- SA 방법: 사용 *안 함* — "engineering-based parameter selection" (선행 SA 결과로 5개만 선택하면 hourly fit이 안 됨을 실험적으로 확인). 38개 모두 채택.
- Building Information Parameters (envelope + 부하 정의, 7개):
  - Conductivity of wall insulation (W/m·K)
  - Conductivity of roof insulation (W/m·K)
  - Conductivity of window glass (W/m·K)
  - SHGC
  - Electric equipment definition (W/m²)
  - Lights definition (W/m²)
  - People definition (m²/person)
- Control Parameters (9개):
  - Cooling set-point at occupied hours (°C)
  - Cooling set-point at unoccupied hours (°C)
  - Heating set-point at occupied hours (°C)
  - Heating set-point at unoccupied hours (°C)
  - Chilled water supply temperature for AHU (°C)
  - Supply air temperature of each AHU (°C)
  - Outdoor air flow at occupied hours (1/h)
  - Outdoor air flow at unoccupied hours (1/h)
  - Hot water peak flow rate (m³/s)
- Schedule Parameters (Weekdays 12 intervals + Weekends 10 intervals = 22개)
- Total: 7 + 9 + 22 = 38 calibration parameters
- 메모: hourly 해상도 보정에는 38개가 필요하다는 *반-SA* 입장. Schedule을 hourly 파라미터로 직접 보정.

### 1.7 Chong et al. (Energy and Buildings, 2021) — REVIEW

- 종류: 107편 보정 논문 메타분석
- 변수 list 자체는 제시하지 않음. Fig. 11–12에서 *가장 자주 보정되는 파라미터* ranking 제공.
- "Most common calibration parameters" (§5.4):
  - Building envelope material properties (conductivity, U-value, density 등)
  - Building envelope infiltration rate
  - Internal gains: occupant density (people)
  - Internal gains: lighting power density (LPD, W/m²)
  - Internal gains: equipment power density (EPD, W/m²)
  - Zone cooling setpoint
  - Zone heating setpoint
  - HVAC component efficiency
  - HVAC zone outdoor air levels
  - DHW: hot water usage (residential)
  - Internal load schedules (occupant/lighting/equipment, 전체에서 6–7편이 schedule도 보정)
- 보정 출력 측 매핑 (Fig. 12):
  - 전력(electricity): 위 envelope + internal gains + setpoints + HVAC efficiency + outdoor air -> 가장 많이 보정
  - 가스/스팀: 전력과 비슷한 변수 보정
  - Indoor temperature: envelope material + infiltration이 핵심
  - HVAC 에너지: HVAC 용량·효율
- 메모: SA 결합 비율은 자동화 보정에서 더 높음 (수동 보정에서는 schedule도 동일 빈도로 보정). 본 연구의 Step 0 변수 채택 *주요 근거*.

### 1.8 Vera-Piazzini and Scarpa (Journal of Building Engineering, 2024) — REVIEW

- TODO (round 1에서 미추출): 표/분류 추출 후속 round로 미룸. 본 round는 Chong 메타분석을 1차 근거로 채택.
- 선행 background/literature_review.md 요약: variability·재현성 문제 지적, 표준화 절차 부재 강조.

---

## 2. 외부 출처 (no PDF, web/standard references)

### 2.1 Reddy and Maor (RP-1051, HVAC&R Research, 2006/2007)

- ASHRAE 후원 RP-1051 — building energy calibration 5-step methodology의 foundational reference.
- 변수 선정 방식: "heuristically define a set of influential parameters and schedules" + 그 best-guess + range.
- 구체 변수 list 제공 *안 함* — "depending on the building type"으로 일반화.
- DOE reference building 적용 사례 보고 (다른 후속 연구 인용): 36–139 inputs calibrated to match whole-building electricity.
- 절차: heuristic 후보 -> Monte Carlo coarse grid search -> 영향력 큰 subset 식별 -> fine refinement.
- 본 연구 Step 0과의 정합성: heuristic prior selection 자체는 본 연구의 literature-grounded selection의 선례. 단, 본 연구는 *literature 빈도*를 heuristic 근거로 명시한다는 점에서 차이.

### 2.2 ASHRAE Guideline 14-2014 — Calibrated Simulation

- 보정된 모델로 인정되는 *오차 임계값* 명시 (NMBE ≤ 5%, CV-RMSE ≤ 15% monthly; ≤10%/30% hourly). Liang Table 3, Chong Table 6 모두 이를 인용.
- *변수 list 자체*는 제공하지 않음. "Independent variables are basically the forcing functions" 수준의 일반 안내.
- Annex에서 calibrated simulation을 위해 "Domain experts are consulted for each building to identify the most common and effective variables to calibrate" 문구.
- 본 연구 Step 0과의 정합성: 변수 list 근거가 아니라 *수렴 임계값 근거*. Methodology §3 Step 1의 J 함수와 §1 Sensitivity 임계값 sensitivity 분석에서 인용.

### 2.3 Ramos Ruiz / Fernández Bandera 계열 (Sensors 2020 외)

- 4-variable reduced approach (15 -> 4 변수 75% 축소, NSGA-II GA):
  - Capacitance (multiplier) — 1–140
  - Internal mass (m²) — 0–90
  - Infiltrations (cm²) — 0–100
  - Thermal bridges (m²K/W) — 0.001–5.0
- SA 방법: 별도 SA 없음. GA + objective function (MAE + Spearman).
- 본 연구 Step 0과의 정합성: 변수 *수* 최소화 trend의 대표 사례. El Kounni의 4-변수 접근과 직접 정렬.

### 2.4 Coakley et al. (RSER, 2014) — REVIEW

- "A review of methods to match building energy simulation models to measured data". 14년 시점에서 over-parameterization·under-determined 문제 처음 체계적으로 지적.
- 개별 변수 list 제시는 없음. 이후 분야가 SA-based 변수 축소로 수렴되는 계기.
- 본 연구 Step 0과의 정합성: literature 빈도 채택 절차의 정당성 논거 (수기 SA 의존을 줄이는 방향). Discussion §3 Limitations의 case-dependence 논의 근거.

### 2.5 HVAC scheduling 보강 문헌 (web/metadata based)

- Lyu et al. (Journal of Building Engineering, 2021) — `10.1016/j.jobe.2020.102058`
  - schedule tuning을 calibration 프로세스의 핵심 모듈로 둔다.
  - short-term monitoring data를 활용해 schedule을 보정한다.
  - internal load schedule과 별도로 `운전 스케줄` 자체가 calibration 변수 후보가 될 수 있다는 직접 근거다.
- Guerrero Ramírez et al. (Building Simulation, 2025) — `10.1007/s12273-024-1200-z`
  - calibrated model 출력으로부터 HVAC operation schedule을 식별한다.
  - HVAC operation schedule, free oscillation period, non-recurrent operational event를 구분한다.
  - 본 연구의 Step 2 진단 로직뿐 아니라, `HVAC scheduling`을 독립 변수/상태로 다뤄도 된다는 근거다.
- Wang et al. (Energy and Buildings, 2024) — `10.1016/j.enbuild.2024.114741`
  - occupancy schedule과 setpoint schedule을 분리해 운전 불확실성을 분석한다.
  - thermostat setback과 occupied/unoccupied control을 schedule 계층으로 볼 수 있는 근거다.
- Yan et al. (Applied Energy, 2020) — `10.1016/j.apenergy.2020.115727`
  - unoccupied temperature setpoint reset과 minimum outdoor airflow reset을 다룬다.
  - calibration 논문은 아니지만 HVAC operation schedule의 물리적 중요성을 보여주는 보강 근거다.

---

## 3. 변수 빈도 aggregation (cross-source)

> 본 연구가 채택할 후보 변수의 *근거 횟수*. 같은 물리 매커니즘을 다른 모델 표기로 구현한 경우는 동일 변수로 묶고, 별도 표기는 비고에 기록한다. ✓ = 명시적 변수, △ = 유사 변수(이름·표기 다름), ○ = 리뷰가 "common" 으로 언급.

| 변수 (정규화 명)                                              | 단위                   | Pachano'21                   | Kounni'23 | Guo'21        | Baba'22      | Liang'25              | Jiang'24                                        | Ramos'20 | Lyu'21 | Guerrero'25 | Wang'24 | Yan'20          | Chong'21 (review) | 합계  |
| ------------------------------------------------------- | -------------------- | ---------------------------- | --------- | ------------- | ------------ | --------------------- | ----------------------------------------------- | -------- | ------ | ----------- | ------- | --------------- | ----------------- | --- |
| Wall U-value / 외벽 conductivity                          | W/m²K                |                              |           |               | ✓            | ✓                     | △ (conductivity)                                |          |        |             |         |                 | ○                 | 4–5 |
| Roof U-value / 지붕 conductivity                          | W/m²K                |                              |           |               | ✓            | ✓                     | △ (conductivity)                                |          |        |             |         |                 | ○                 | 4   |
| Window U-value / glass conductivity                     | W/m²K                |                              |           |               | ✓            | ✓                     | △ (conductivity)                                |          |        |             |         |                 | ○                 | 4   |
| Window SHGC                                             | —                    |                              |           |               | ✓            |                       | ✓                                               |          |        |             |         |                 | ○                 | 3   |
| Floor U-value                                           | W/m²K                |                              |           |               |              | ✓                     |                                                 |          |        |             |         |                 | ○                 | 2   |
| Thermal mass / capacitance / internal mass              | kJ/m²K, multiplier   |                              |           |               | ✓ (×2)       |                       |                                                 | ✓ (×2)   |        |             |         |                 | △                 | 3–4 |
| Thermal bridges                                         | kJ/h·K, m²K/W        |                              | ✓         |               |              |                       |                                                 | ✓        |        |             |         |                 | △                 | 2–3 |
| Convective/radiant heat gains                           | kJ/h·K               |                              | ✓ (×2)    |               |              |                       |                                                 |          |        |             |         |                 | △                 | 1   |
| Infiltration rate (ACH or 1/h or leakage area)          | ACH, 1/h, cm²        |                              | ✓         | ✓             | ✓            | ✓                     | △ (outdoor air flow)                            | ✓        |        |             |         |                 | ○                 | 6   |
| Solar reflectance (blinds/shading)                      | —                    |                              |           |               | ✓            |                       |                                                 |          |        |             |         |                 | △                 | 1   |
| Shading opening ratio                                   | %                    |                              |           |               | ✓ (×2 NW/SE) |                       |                                                 |          |        |             |         |                 | △                 | 1   |
| Lighting power density (LPD)                            | W/m²                 |                              |           | △ (intensity) | ✓            | ✓                     | ✓                                               |          |        |             |         |                 | ○                 | 4–5 |
| Equipment power density (EPD)                           | W/m²                 |                              |           | △             | ✓            | ✓                     | ✓                                               |          |        |             |         |                 | ○                 | 4–5 |
| Occupancy density (people)                              | persons or m²/person |                              |           | △             | ✓ (count)    | ✓ (W/m²)              | ✓                                               |          |        |             | △       |                 | ○                 | 4–5 |
| Heating setpoint                                        | °C                   |                              |           | ✓             |              | ✓                     | ✓ (occ/unocc)                                   |          |        |             | △       | △ (unocc reset) | ○                 | 5–6 |
| Cooling setpoint                                        | °C                   |                              |           | ✓             |              |                       | ✓ (occ/unocc)                                   |          |        |             | △       |                 | ○                 | 3–4 |
| Setpoint schedule (occ vs unocc)                        | °C × time            |                              |           | △             |              | △                     | ✓                                               |          |        |             | ✓       | △               | ○                 | 4–5 |
| Dead-band temperature                                   | °C                   |                              |           |               |              | ✓                     |                                                 |          |        |             |         |                 | △                 | 1   |
| Natural ventilation max ACH                             | ACH                  |                              |           |               | ✓            |                       |                                                 |          |        |             |         |                 | △                 | 1   |
| NV setpoint                                             | °C                   |                              |           |               | ✓            |                       |                                                 |          |        |             |         |                 | △                 | 1   |
| Window-open schedule                                    | h/d                  |                              |           |               |              | ✓                     |                                                 |          |        |             |         |                 | △                 | 1   |
| HVAC component efficiency (COP, fan)                    | W/W                  | ✓ (COP, biquadratic)         |           |               |              |                       |                                                 |          |        |             |         |                 | ○                 | 1–2 |
| HVAC operation schedule / availability / setback        | time / shift / mode  |                              |           |               |              | △ (setpoint schedule) | △ (weekday/weekend schedule, occ/unocc control) |          | ✓      | ✓           | ✓       | ✓               | △                 | 5–6 |
| HVAC component capacity                                 | W                    | ✓ (Heating Capacity 등)       |           |               |              |                       |                                                 |          |        |             |         |                 | ○                 | 1   |
| Air handling unit parameters (UA, flow rates, recovery) | various              | ✓ (다수)                       |           |               |              |                       |                                                 |          |        |             |         |                 | △                 | 1   |
| Outdoor air flow (occ/unocc)                            | 1/h or m³/s          | ✓ (Min OA flow)              |           |               |              |                       | ✓ (×2)                                          |          |        |             |         | ✓               | ○                 | 3   |
| Chilled water / supply air temperature                  | °C                   |                              |           |               |              |                       | ✓ (×2)                                          |          |        |             |         |                 | △                 | 1   |
| DHW peak flow / hot water usage                         | m³/s                 | ✓ (recovery time, flow rate) |           |               |              |                       | ✓                                               |          |        |             |         |                 | ○ (residential)   | 2   |
| Hourly lighting / equipment / occupancy schedule        | hourly fraction      |                              |           | ✓ (×72)       |              |                       | ✓ (×22)                                         |          | ✓      |             | ✓       |                 | ○                 | 4   |
| Time step (simulation)                                  | h                    |                              |           |               |              | ✓                     |                                                 |          |        |             |         |                 |                   | 1   |
| Plant loop volume (e.g., Library Building Loop)         | m³                   | ✓                            |           |               |              |                       |                                                 |          |        |             |         |                 |                   | 1   |
| Buffer tank parameters                                  | various              | ✓                            |           |               |              |                       |                                                 |          |        |             |         |                 |                   | 1   |

> 주의: 합계는 명시적(✓)과 유사(△)의 합. 리뷰 인정(○)은 별도 표기로 cross-paper 추가 가중치만 부여.

### 3.1 빈도 기반 ranking (단순화)

> 정규화된 변수 명 기준, 명시 + 유사 합계의 내림차순.

1. **Infiltration rate / leakage area** — 6 (Kounni, Guo, Baba, Liang, Ramos, Jiang의 outdoor air; Chong review 강조)
2. **Heating setpoint** — 5–6 (Guo, Liang, Jiang, Wang, Yan, Chong review)
3. **HVAC operation schedule / availability / setback** — 5–6 (Lyu'21, Guerrero'25, Wang'24, Yan'20, plus Liang/Jiang proxies)
4. **Wall U-value (외벽 thermal performance)** — 4–5 (Baba, Liang, Jiang, Chong review)
5. **Lighting power density (LPD)** — 4–5 (Guo intensity, Baba, Liang, Jiang, Chong review)
6. **Equipment power density (EPD)** — 4–5 (Guo, Baba, Liang, Jiang, Chong review)
7. **Occupancy density** — 4–5 (Guo, Baba, Liang, Jiang, Wang)
8. **Setpoint schedule (occ vs unocc)** — 4–5 (Guo proxy, Liang proxy, Jiang, Wang, Yan, Chong review)
9. **Window U-value** — 4 (Baba, Liang, Jiang, Chong review)
10. **Roof U-value** — 4 (Baba, Liang, Jiang, Chong review)
11. **Hourly internal-load schedule** — 4 (Guo, Jiang, Lyu, Wang, Chong review note)
12. **Cooling setpoint** — 3–4 (Guo, Jiang, Wang, Chong review)
13. **Window SHGC** — 3 (Baba, Jiang, Chong review)
14. **Outdoor air flow (occ/unocc)** — 3 (Pachano, Jiang, Yan, Chong review)
15. **Thermal mass / capacitance / internal mass** — 3–4 (Baba, Ramos)
16. **Thermal bridges** — 2–3 (Kounni, Ramos)
17. **Floor U-value** — 2 (Liang, Chong review)
18. **DHW (hot water peak flow / recovery time)** — 2 (Pachano, Jiang)
19. **HVAC component efficiency / capacity / curves** — 1–2 (Pachano detailed, Chong review)

빈도 ≤ 1로 떨어지는 항목 (특수 사례, 후보군 제외 가능):
- Solar reflectance, Shading opening ratio, NV max ACH, NV setpoint, Window-open schedule, T_dead_band, Time step, Plant loop volume, Buffer tank parameters, AHU UA·recovery 등.

---

## 4. Step 0 채택 변수 후보 (proposal)

> 위 ranking을 근거로, 본 연구의 Step 0 채택 변수 후보를 다음과 같이 *flat list*로 제시한다. 카테고리 매핑은 *하지 않음* (사용자 결정).
>
> 채택 임계값: cross-source 빈도 ≥ 3 (단, 빈도 2이라도 review 강조 ○가 있으면 고려). 정합성은 paper_draft.md C2 (Stage 1 search arm)와 C3 (Stage 2 reasoning arm) 입력 단위와 직접 연결된다.

### 4.1 1차 채택 후보 (빈도 ≥ 4 또는 review 강조)

1. Infiltration rate (1/h or ACH; ACH50 또는 ACH-natural에 따라 단위 선택 필요)
2. Wall U-value (W/m²K)
3. Roof U-value (W/m²K)
4. Window U-value (W/m²K)
5. Window SHGC (—)
6. Lighting power density (W/m²)
7. Equipment power density (W/m²)
8. Occupancy density (m²/person 또는 W/m²; 단위 선택 필요)
9. Heating setpoint (°C, 점유/비점유 구분)
10. Cooling setpoint (°C, 점유/비점유 구분)
11. Setpoint schedule (occupied/unoccupied 또는 weekday/weekend 기반)
12. Hourly internal-load schedule (lighting / equipment / occupancy 시간별 fraction; interval 기반 권장)
13. HVAC operation schedule / availability / setback schedule (on/off 시간, occupied/unoccupied 운전 구간, thermostat setback time window)

### 4.2 2차 채택 후보 (빈도 2–3, 사례에 따라 선택)

13. Floor U-value (W/m²K) — 빈도 2이지만 envelope 완결성 관점에서 유지 가능
14. Outdoor air flow (occ/unocc) (1/h or m³/s)
15. Thermal mass / capacitance (kJ/m²K 또는 multiplier)
16. DHW peak flow / hot water recovery time
17. HVAC plant efficiency (COP, plant 효율 곡선 — Pachano 식의 detailed parametrization은 Stage 2 specialist 후보로 미루는 것 추천)

### 4.2.1 HVAC scheduling 변수 해석 메모

- `Hourly lighting / equipment / occupancy schedule`은 internal load schedule이다. HVAC schedule과 동일 변수로 취급하지 않는다.
- `Setpoint schedule`은 thermostat control schedule이며, HVAC availability와는 연관되지만 동일 변수는 아니다.
- `HVAC operation schedule / availability / setback schedule`은 별도 2차 후보로 유지한다.
- 구현 단위 예시:
  - system availability shift (start/end time offset)
  - occupied/unoccupied HVAC mode split
  - thermostat setback start/end time
- 문헌상 직접 반복 빈도는 높지 않지만, 최근 calibration/schedule tuning 및 operation schedule identification 연구가 존재하므로 case-dependent secondary variable로 채택 가능하다.

### 4.3 채택 *제외* 권고 (빈도 1 또는 case-specific)

- Solar reflectance, Shading opening ratio (Baba 사례 특수)
- Natural ventilation parameters (Baba)
- T_Dead_band (Liang)
- Time-step (Liang — 시뮬레이션 메타파라미터, 채택 부적합)
- Plant loop volume, Buffer tank, AHU UA·recovery (Pachano 매우 detailed — 본 연구는 plant 단위로 묶어 처리 권고)

### 4.4 단위·범위 잠정안

> Step 0 산출물 (b) "채택 변수 목록 + 출처"의 잠정 range는 본 round의 cross-source 최소값~최대값으로 1차 결정한다. 사례별 baseline OSM 측정값은 미정 (Building A·B의 측정 데이터로 후속 조정 필요).

| 변수 | 단위 | 잠정 range (literature) | 주 출처 |
|---|---|---|---|
| Infiltration rate | 1/h | 0.24–2.0 | Liang (Kounni leakage area는 cm² 별도) |
| Wall U-value | W/m²K | 0.20–1.006 | Liang (Baba 0.40–0.70) |
| Roof U-value | W/m²K | 0.10–0.450 | Liang (Baba 0.23–0.33) |
| Window U-value | W/m²K | 1.5–3.372 | Liang (Baba 2.20–3.00) |
| Window SHGC | — | 0.60–0.76 | Baba |
| Floor U-value | W/m²K | 0.10–0.581 | Liang |
| Lighting power density | W/m² | 5.0–20.0 | Liang (Baba 9–16) |
| Equipment power density | W/m² | 2.0–11.77 | Liang (Baba 2–5) |
| Occupancy density | W/m² 또는 persons | 10–100 W/m² (Liang) / 20–25 학생수 (Baba) | 단위 선택 결정 필요 |
| Heating setpoint | °C | 24–27 (Liang); occupied/unoccupied 분리 (Jiang) | Jiang 권장 |
| Cooling setpoint | °C | occupied/unoccupied 분리 (Jiang) | Jiang |

---

## 5. 미해결 사항 / 다음 round TODO

1. **Vera-Piazzini 2024 변수 분류 표** — round 1에서 미추출. 변수 ranking에 review 정량 가중치 추가 가능.
2. **단위 선택 결정** — Occupancy density (W/m² vs. persons or m²/person), Infiltration (ACH vs. ACH50 vs. cm² leakage), Hot water (peak flow vs. recovery time).
3. **Building A / B 측정 데이터 매핑** — 잠정 range를 사례별 baseline OSM과 결합해 ±α 조정.
4. **Schedule 처리 결정** — Guo (100 hourly vars)·Jiang (22 interval vars)·Liang (단일 schedule profile) 중 본 연구 채택 방식 결정 필요. Stage 1 차원 폭발 방지를 위해 interval 기반 (Jiang) 또는 단일 profile (Liang) 권고.
5. **HVAC 변수 처리 결정** — Pachano-수준 detailed plant 변수는 Stage 2 specialist (HVAC/Plant) 도메인에 위임할지, Step 0에서 일부만 노출할지 결정.
6. **HVAC scheduling 표현 결정** — availability shift, setback start/end, occ/unocc mode 중 어떤 파라미터화로 구현할지 결정 필요. 현재 round에서는 `HVAC operation schedule / availability / setback schedule`을 하나의 2차 변수 계층으로 유지.

---

## 6. paper_draft.md cascade 알림 (사용자 확인 필요)

본 단계에서 사용자는 *"카테고리가 아니라 그냥 변수 개념으로 설정"* 으로 결정했다. 이로 인해 paper_draft.md 일부 표현이 cascade로 영향받는다.

### 영향 위치
- §Methodology §2 Step 0 §3 "카테고리 정의" -> variables_setting.md는 카테고리를 산출하지 않음
- §Introduction §8 Contribution **C1** "Literature-grounded **Variable & Category** Definition" -> "Variable Definition"으로 단순화 검토
- §Methodology §1 Framework Overview "Literature-grounded **category** backbone" -> "Literature-grounded **variable** backbone"으로 변경 검토
- §Methodology §3 Step 1 / §4 Step 2 "**카테고리 단위** 최적화" / "**카테고리 도메인** specialist" -> unit 명칭을 "variable group"·"variable domain" 등으로 재정의 검토 (또는 카테고리 개념을 *암묵적 그룹화*로 유지)
- §Methodology Step 1 §7 Inter-round Orchestration Protocol — "다음 카테고리 선택" 규칙 표현 재정의

### 결정 옵션

**옵션 A**: paper_draft.md에서 "카테고리"를 "variable group"으로 일괄 치환. Stage 1·2의 단위는 *물리 매커니즘 기반 그룹*이지만 데이터 검증/literature 분류 산출물은 아님 — 즉 *암묵적 그룹화*.

**옵션 B**: Stage 1·2 단위를 *개별 변수*로 재정의. Optuna는 변수 단위, specialist agent는 변수 단위로 호출. 단점: specialist 수가 폭증, freeze 단위 미세화로 over-engineering 위험.

**옵션 C**: 카테고리 단위는 그대로 유지하되, Step 0에서는 *변수만 산출*하고 카테고리 매핑은 Methodology §1의 *고정된 6 grouping prior* (Envelope/AirExchange, Internal Loads, Schedules/Operation, Thermostat/Setpoints, HVAC/Plant Efficiency, DHW)에 정적으로 매핑. literature는 변수의 빈도 근거만 제공.

-> 본 search_background round 결과로는 **옵션 C가 가장 자연스럽다**: 변수는 literature-grounded, 그룹 단위는 paper_draft.md prior 6개로 고정. 이 경우 paper_draft.md 표현 변경은 최소화 (§Step 0 §3을 "카테고리 정의" 대신 "채택 변수의 prior 6개 group으로의 정적 매핑"으로 재기술).

> 사용자 확인 필요 — A/B/C 중 선택해 주시면 paper_draft.md 후속 patch 적용.
