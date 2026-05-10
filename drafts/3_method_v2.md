# Methodology

> Author: 유도연   
> Date: 2026.05.02.   

---
## framework

*(fig x. 2-framework)*

 본 연구는 2단계 BEM calibration framework를 제안한다.

Step 0  Pre-calibration Baseline & Literature-grounded Variable Selection
        - Baseline OSM 구축 (Revit → gbXML → OpenStudio → SketchUp 형상 보정)
        - 선행 GA·최적화 기반 보정 연구의 calibration target 변수 채택
        - 산출: Stage 1·2 공유 flat 변수 list + baseline OSM
              |
              v
Step 1  반복형 변수 단위 동시 최적화 (Stage 1)
        - Round 0: SA/correlation 1회 -> 비중요 변수 screening
        - Round 1+: 비-freeze 전 변수 동시 Optuna(TPE) study
        - 라운드 종료 시 전역 J 평가, per-variable freeze 판정,
          search space 축소 (α_new = ρ·α_old)
        - envelope 물리 변수: literature range hybrid clamp
              |
              v
Step 2  진단 기반 전문가 멀티에이전트 정제 (Stage 2, primary novelty)
        - Step 0 변수 list를 운영 단위로 두고 specialist 인스턴스 동적 할당
        - 진단/critic(전력·가스·reality) -> orchestrator -> specialist
        - 후보안 -> reality 검토 -> 채택 / hybrid / freeze

## Step 0

### 1. Baseline OSM
*(fig x. step 0 flowchart)*
![[Pasted image 20260503191434.png]]

step 0은 2-stage BEM calibration framework에 적용하기 위한 Input 산출을 목적으로 한다. 
fig x에서도 볼 수 있듯이, Step 1, 2에서 모두 사용할 기본 baseline OSM을 산출하고, 미세 보정을 위한 변수 list를 선별한다.

Baseline OSM 과정
1. Revit 프로그램을 통해 건물의 기본적인 BIM을 반영하였고 이를 gbXML로 추출하여 OpenStudio model을 생성
2. 이후 형상 오류 보정을 위해 OpenStudio에서 생성된 OSM을 SketchUp에서 열어 최소한의 형상 오류 보정 진행
3. OpenStudio 프로그램을 사용해 기본적인 HVAC 시스템과 설비 장비, 외벽 재료 및 레이어 등이 반영되었음
	- *(Table x. 수정된 변수 category list)*

3번째 단계를 거쳐 Baseline OSM을 산출하였으며 이를 입력으로 2-stage BEM Calibration이 진행되었다.

Baseline.20260510~.osm의 결과

### 2. Variable List

*(Table x. 선행 연구를 통해 선별한 variable list)*

| 변수 (정규화 명)                                           | 단위                   | 인용 빈도 | 1차 운영    | 출처 (C) |
| ---------------------------------------------------- | -------------------- | ----- | -------- | ------ |
| **Infiltration rate (ACH or 1/h or leakage area)**   | ACH, 1/h, cm²        | 6     | ✅ active |        |
| **Wall U-value / 외벽 conductivity**                   | W/m²K                | 4–5   | freeze   |        |
| **Roof U-value / 지붕 conductivity**                   | W/m²K                | 4     | freeze   |        |
| **Window U-value / glass conductivity**              | W/m²K                | 4     | freeze   |        |
| **Window SHGC**                                      | —                    | 3     | freeze   |        |
| **Lighting power density (LPD)**                     | W/m²                 | 4–5   | ✅ active |        |
| **Equipment power density (EPD)**                    | W/m²                 | 4–5   | ✅ active |        |
| **Occupancy density (people)**                       | persons or m²/person | 4–5   | ✅ active |        |
| **Heating setpoint**                                 | °C                   | 5–6   | ✅ active |        |
| **Cooling setpoint**                                 | °C                   | 3–4   | ✅ active |        |
| **Setpoint schedule (occ vs unocc)**                 | °C × time            | 4–5   | freeze   |        |
| **Hourly lighting / equipment / occupancy schedule** | hourly fraction      | 4     | freeze   |        |
| **HVAC operation schedule / availability / setback** | time / shift / mode  | 5–6   | ✅ active |        |
| **Floor U-value**                                    | W/m²K                | 2     | freeze   |        |
| **Outdoor air flow (occ/unocc)**                     | 1/h or m³/s          | 3     | freeze   |        |
| **Thermal mass / capacitance / internal mass**       | kJ/m²K, multiplier   | 3–4   | freeze   |        |
| **DHW peak flow / hot water usage**                  | m³/s                 | 2     | freeze   |        |
| **Boiler efficiency**                                | —                    | 1–2   | freeze   |        |
| **Chiller COP / Fan power**                          | W/W                  | 1–2   | freeze   |        |

stage 1, 2에서 미세 보정을 위해 사용된 변수들 list는 table x와 같다.
- 선행 최적화, GA 기반의 보정 연구의 calibration target 변수를 조사해 (a). 선행 연구 등장 빈도, (b). 물리 매커니즘 정합성

#### 1차 실험 운영 범위 (Initial Run Scope)

상기 19개 변수 중 1차 KETI 실험에서는 **7개 변수만 활성(active)** 하고 나머지는 baseline 값으로 freeze한다.

활성 7개:
- 내부부하·재실밀도: EPD, LPD, occupancy density
- 운영 setpoint: heating setpoint, cooling setpoint
- 가스 cal lever: infiltration rate, HVAC operation schedule (availability shift)

선정 기준:
1. 선행 연구 인용 빈도 상위 (모두 4회 이상 등장; HVAC operation schedule는 인용 빈도 1위(5–6회)로 가스 운영 시간 lever 확보)
2. KETI 부하 구조 정합 — FAB-dominant 전력 baseload(equipment/lighting/density)와 winter-dominant 가스(setpoint/infiltration/HVAC schedule) 양쪽 lever 균형
3. 변수 간 식별성 (collinearity 회피 — schedule multiplier 군은 density·load와 partial collinear, envelope U-value 군은 상호 collinear)

운영 모드 단순화 (1차 실험 한정):
- Round 0 SA screening 생략 — literature 근거로 active 변수 직접 지정
- Block-wise iteration(카테고리 순차 실행) 보류 — 1차는 active 7개 *단일 Optuna(TPE) study*로 운영
- 라운드 기반 변수 동시 튜닝 / freeze 결정 / 종료 조건의 임계값(θ_J=1%, θ_freeze=5%, ρ=0.7, R_max=7)은 동일 적용

후속 라운드 결정 (1차 결과 기반):
- 잔차 시그니처가 frozen 변수 그룹의 누락을 시사 → 해당 변수 추가 활성
- 잔차가 카테고리별로 명확히 분리 → block-wise iteration 도입
- 식별성 검증 필요 → SA screening 도입

> 본 운영 범위 축소는 framework의 *structural reproducibility*를 침해하지 않으며, 동일 protocol의 *부분 인스턴스*(active 변수 집합과 study 운영 모드만 축소)이다.

최종적으로 다음 2-stage bem calibration 과정에 넘어갈 output
- baseline osm, variables list

## Step 1

Step 1은 step 0의 결과인 baseline osm과 변수 list를 입력으로 Optuna Optimization를 반복하여 변수의 탐색 범위를 좁혀가며 BEM 을 보정한다.
이를 통해 구조적으로 변수의 후보 범위를 오차가 적은 방향으로 축소하고 해당 case에 더 영향력이 있는 변수를 선별하고자 한다.

Optuna Optimization (C)
- 개념 및 설명
- GA 등 다른 optimization과의 차이점
- why, how?

*(fig x. step 1 flowchart)*

![[Pasted image 20260503165743.png|352]] *(→ 논문 제출 시 fig x. caption으로 대체)*
1. Round 0 (우선 생략)
	- Optuna optimization 반복 전 변수들의 민감도 및 상관 관계 파악을 통해 변수 list 확정

목적 함수 설정: 
- `J = w1·CVRMSE_elec + w2·CVRMSE_gas + w3·|NMBE_elec| + w4·|NMBE_gas|`
- 전기와 가스 사용량 오차 최소화를 목적으로 하기 때문에 CVRMSE와 NMBE의 오차 최소화를 목적으로 한다.
- 가중치는 case별로 결정하되 한 연구 내에서는 고정

라운드 기반 변수 동시 optuna 튜닝
- 라운드 당 trial 수: n_trial = 10
- 비-freeze 변수 전체 동시 Optuna(TPE) study (C)
- 라운드 종료 시 목적 함수 평가, 변수별 freeze 판정, search space 수정
- **Search space 설정**: 비-freeze 변수 `current_value ± α`, α는 변수 유형별 설정 (multiplier·offset·shift·direct)
- **Hybrid clamp** (envelope 물리 변수 한정): `wall_u_value`, `roof_u_value`, `window_u_value`, `window_shgc`, `floor_u_value`, `oa_or_fan_multiplier`는 sampler 단계에서 literature range로 강제 clamp (C); 그 외 변수는 `current_value ± α` 자유 탐색

search space 갱신 및 freeze 결정
- **변수 freeze**: 변수 상대 변동 `|v_curr − v_prev| / |v_prev| < θ_freeze` 가 2 라운드 연속 충족 시 freeze (`θ_freeze = 5%`)
- **Search space 축소**: 비-freeze 변수의 `α_new = ρ · α_old` (`ρ = 0.7`)
- **Alpha 경계 도달 변수**: 다음 라운드에 alpha 1회 확장 (`× 1/ρ`); 재도달 시 경계로 freeze. envelope hybrid clamp 변수는 literature range 경계 도달 시 _그 자리에서 freeze_ (확장 없음).
- **J 악화 시**: best-so-far 모델 유지, 해당 라운드 freeze 갱신 _건너뜀_

종료 조건 (결정론적 규칙)    
- **수렴 종료**: `(J_prev − J_curr) / J_prev < θ_J` 가 2 라운드 연속 (`θ_J = 1%`)
- **Freeze 종료**: 모든 변수가 freeze 상태에 도달
- **Hard cap**: 라운드 수 `R_max = 7` 도달 시 강제 종료 (안전장치)
- ASHRAE G14 임계값(monthly CVRMSE ≤ 15%, |NMBE| ≤ 5%)에 비례한 정규화 가중을 1차 후보로 설정 (C)

step 1 output
- step 1의 output은 step 2. multi-agent를 통한 reasoning 미세 보정의 입력값으로 사용
- step 1의 output: calibrated osm, 변수별 최종값, freeze 변수 목록, 잔차 패턴 및 오차율, 변수별 잔차 기여도
- Stage 1의 active/freeze/미활성 status는 Stage 2의 prior 정보로 전달 (hard constraint 아님); Stage 2는 Step 0 22개 변수 pool 전체를 후보로 운영

*(Table x. protocol)*

table x. 는 optuna optimization의 자동화를 위해 사전 정의된 임계값 및 규칙
- 종료 조건, freeze 조건, search space 업데이트 조건
- round 별 trial 수, 수렴 종료, hard cap 조건
- bast-result 처리
등의 조건을 사전 명시하여 해당 조건에 따라 optuna 실행, 업데이트, 종료가 이루어짐

## Step 2

step 2에서는 llm-based multi-agent를 통해 reasoning한 calibration 자동화를 진행함.
- step 1이후 미세 조정
	- step 1 종료 시점: 탐색 공간이 축소되고 오차가 구조적으로 정리됨
- **Stage 2 작업 pool = Step 0에서 정의된 전체 22개 변수** (Stage 1 active·freeze·미활성 모두 포함). Stage 1의 active/freeze/미활성 구분은 Stage 2의 *prior 정보*로만 작동하며 hard constraint로 전이되지 않음.
- diagnostic agent가 잔차 시그니처(전력·가스·교차)를 진단해 22개 pool 중 시그니처와 정합하는 variable candidate list를 생성하고, **orchestrator phase 1이 라운드별로 그 중 일부 subset을 선택**하여 specialist 인스턴스에 동적 할당함.
- Stage 1 freeze 변수의 처리: 기본값은 "유지" (Stage 1 최종값 사용)이나, diagnostic이 잔차 시그니처로 명시 지목할 경우 candidate list에 재포함 가능; 단 신규 변수 정의·생성은 불가 (Step 0 어휘 내 한정).
- reasoning한 해석, 진단을 통해 구조적 정제 
- 자유 생성 AI 후처리가 아닌 제약 조건을 사전에 명시에 구조화
- 목표로 하는 ASHRAE 조건에 부합, 상태 진단을 통한 논리적 보정을 위해 추가 보정

*(fig x. step 2 flowchart)*
![[Pasted image 20260503171932.png|230]] *(→ 논문 제출 시 fig x. caption으로 대체)*

llm-based multi-agent 과정
1. Dianositic agent
	- **역할**
		- 전력, 가스 통합 해석
        - **입력**
            - Stage 1 산출물의 월별 전력, 가스 잔차 + 변수별 J 기여도
            - Step 0 전체 22개 변수 pool (Stage 1 active·freeze·미활성 status 포함; status는 prior 정보로만 사용)
        - **출력**
            1. 전력 잔차 시그니처
            2. 가스 잔차 시그니처
            3. 두 modality의 교차 시그니처 (예: 여름 cooling 전력 bias와 shoulder 가스 bias 동시 발현)
            4. 시그니처와 정합하는 variable candidate list (Step 0 22개 pool 전체에서 도출; Stage 1 비-freeze·미활성·freeze 변수 모두 포함 가능)
        - **책임 원칙**
            - 잔차 시그니처 해석 + variable candidate list 생성 (변수 *값*은 수정 ✗)
            - candidate list는 Step 0 22개 변수 어휘 내로 한정; 신규 변수 정의·생성은 불가
            - Stage 1 freeze 변수도 잔차 시그니처가 명시적으로 지목할 경우 candidate에 재포함 가능 (Stage 1 freeze는 hard constraint가 아닌 prior)
2. Orchestrator (Phase 1) agent
	- **역할**
		- diagnostic의 variable candidate list로부터 variable subset 분할 + specialist 인스턴스 호출, 할당
        - **입력**
            - diagnostic agent의 잔차 시그니처 (전력·가스·교차)
            - variable candidate list (Step 0 22개 pool 기반)
            - Stage 1 변수 status (active/freeze/미활성, prior 정보) + Stage 2 누적 freeze 목록 (hard 제외)
            - initial routing prior (물리 직관 기반 사전 지식)
        - **출력**
            - specialist 인스턴스별 variable subset 할당 목록
            - specialist 호출 명령 (할당 variable subset + 라운드 컨텍스트)
        - **책임 원칙**
            - candidate list로부터 variable subset 분할 + specialist 호출·할당 (변수 *값*은 수정 ✗)
3. Specialist agents
	- *(table x. specialist agents)*
	- **역할**
		- orchestrator가 라운드별 동적으로 호출·할당하는 인스턴스
		-  동일 라운드에 여러 인스턴스가 *서로 다른 variable subset*을 담당하며 병렬 호출
        - **출력**
            - 후보안 1개 = (변수 식별자, 신규 값, 물리 매커니즘 사유) tuple list
        - **책임 원칙**
            - 할당된 variable subset 내 수정안 제안 (할당 외 변수·freeze 변수 수정 불가; schema-validated)
        
4. Reality agent
	- **역할**
		- specialist 후보안 *사후 검토*에만 호출됨 (라운드 시작 시점에는 호출되지 않음)
        - **입력**
            - 각 specialist agent의 후보안 (변수 식별자·신규 값·물리 사유)
        - **출력**
            - 후보안별 판정 결과: pass / hold / reject + 사유
        - **책임 원칙**
            - hard physics 위반 → 자동 reject (변수 값 수정 ✗)
            - soft plausibility 검토 → hold/pass 의견 출력 (변수 값 수정 ✗)
5. Orchestrator (Phase 2) agent
	- **역할**
		- 변수 값 수정 권한 없음. routing·할당·채택·freeze 결정만 수행
		- specialist 후보안 + reality 검토 결과로부터 채택 / hybrid / 기각 결정 + freeze 갱신
        - **입력**
            - specialist 후보안 (변수 식별자·신규 값·물리 사유 tuple list)
            - reality agent 판정 결과 (pass/hold/reject + 사유)
            - 전역 J 평가 결과
        - **출력**
            - 채택 변수값 (변수 식별자·최종 채택값)
            - freeze 갱신 목록
            - hold 처리 변수 목록 (다음 라운드 재고)
        - **책임 원칙**
            - LLM 기반 *추론*; 정적 if-then 규칙이 아님 (단, 출력은 #6 (a) schema validation으로 변수 식별자 어휘 안에서만 허용)
            - 채택 / hybrid / 기각 + freeze 갱신 (변수 *값*은 수정 ✗)

라우팅 사전 지식 (Initial routing prior)
- orchestrator phase 1에 고정 if-then 규칙이 아닌 물리 직관 기반 prior로 제공
- orchestrator는 prior를 참고하되 잔차 시그니처·variable candidate list 컨텍스트에 따라 재해석 가능
- prior 예시:
    - 내부부하·운영 패턴 전력 시그니처 → LPD, EPD, 점유 density, 운영 schedule 우선 할당
    - 겨울 난방 가스 시그니처 → 외피 U-value, infiltration, 난방 setpoint, HVAC 효율 변수 우선 할당
    - baseload·shoulder 가스 시그니처 → DHW 관련 변수, 운영 schedule, 외피 변수 우선 할당
    - 전력·가스 교차 시그니처 → 두 modality에 동시 영향하는 변수 (운영 schedule, HVAC availability, 점유 density) 우선 할당
    - 반복 지목 variable subset → 다음 라운드 우선순위 상승

후보안 채택 규칙 (orchestrator phase 2)
- 단일 specialist 후보안 우세 → 그대로 채택
- 복수 후보안이 비충돌·상보적인 경우 한정 hybrid 허용 (서로 다른 variable subset에 대한 수정안)
- reality reject 후보안 → 자동 기각
- reality hold + J 개선 미미 → 다음 라운드 재고
- freeze 갱신: per-variable 변동 `< θ_freeze` 기준; Stage 2 freeze는 Stage 2 라운드 내에서만 누적 (Stage 1 freeze는 prior 정보로만 사용되며, 잔차 시그니처 지목 시 Stage 2가 재활성 가능)

제약 조건 (Constraint Enforcement)
1. **도메인 제한**: specialist 출력은 orchestrator phase 1이 할당한 variable subset 외부 수정 불가 (schema validation 강제); Step 0 22개 변수 어휘 외 신설·정의 변경 불가; Stage 2 누적 freeze 변수 수정 불가
2. **Hard physics 제약**: reality agent가 외부 표준 (ASHRAE 90.1/G14/62.1 (C), 국토교통부 건축물 에너지절약설계기준 (C)) 및 building physics 기본 원리 기반 binary reject 적용; 위반 시 자동 reject
3. **Soft plausibility 검토**: reality agent LLM이 표준 범위 내 결합 모순 (예: 외피 매우 우수 + 침기율 매우 높음)에 대해 hold/pass 의견 출력
4. **채택 규칙 제한**: orchestrator phase 2는 사전 정의된 채택 규칙 (단일 우세·비충돌 hybrid·기각)만 허용; 임의 합성·자유 생성 채택 금지
5. **감사 로그**: 전 단계 (diagnostic 출력·orchestrator routing·specialist 후보안·reality 판정·orchestrator 채택·freeze)를 변수 identifier 어휘 (Step 0 변수 list 정규화 변수명)로 로깅; structural reproducibility 운영적 보장

종료 조건
- **수렴 종료**: `(J_prev − J_curr) / J_prev < θ_J` 가 2 라운드 연속 (`θ_J = 1%`)
- **Freeze 종료**: 22개 pool 중 Stage 2 누적 freeze 변수가 전체에 도달 (Stage 1 freeze와 무관하게 Stage 2 자체 freeze 기준)
- **Hard cap**: Stage 2 라운드 수 상한 도달 시 강제 종료
- **ASHRAE G14 충족**: monthly CVRMSE ≤ 15%, |NMBE| ≤ 5% 달성 시 조기 종료

step 2 output
- 최종 보정 완료된 calibration osm
- 전기, 가스 월별, 전체 오차, 평가 지표 결과 비교
- reasoning -> 분석 결과 포함

## Case Study Buildings — 두 채의 실증 건물

본 연구를 검증하기 위해 두 채의 실측 건물을 case study로써 사용함.
환경·특성이 대비되는 두 건물을 선정해 framework의 적용성을 두 contrasting case에서 시연
본 case study는 통계적 일반화 증명이 아니라 서로 다른 운영·물리 조건에서의 framework 적용성과 동일 변수 list·에이전트 토폴로지의 재설계 없는 적용을 보이는 데 목적이 있다.

1. 케이스 선정 원칙
    - 전이 가능성 검증을 위해 building type / 규모 / 시스템 / 운영 패턴이 대비되는 두 건물 선정

(table x. building a, b 아래의 특정 비교 정리)
	
2. Building A
	- (fig x. building A bem 이미지)
	- 위치 / 기후대 / 용도 / 연면적 / 층수
	- HVAC 시스템 개요
	- 운영 스케줄 특성
	- 실측 데이터: 기간, 해상도(월별·일별·시간별), 전력/가스 항목

3. Building B (동일 구조)
	- (fig x. building B bem 이미지)
	- 위치 / 기후대 / 용도 / 연면적 / 층수
	- HVAC 시스템 개요
	- 운영 스케줄 특성
	- 실측 데이터: 기간, 해상도, 전력/가스 항목

4. Baseline OSM 구축 결과
	- 두 건물의 Step 0 baseline 모델 요약 (geometry, zoning, 외피, HVAC 토폴로지)
	- Baseline 모델의 *보정 전* 성능 (월별 CVRMSE/NMBE 표 1개)
	- *(Table x. Building A·B baseline 모델 보정 전 월별 CVRMSE/NMBE)*

5. 두 건물의 차이가 framework에 던지는 도전 (우선 생략?)
	- 어떤 *variable subset*에서 차이가 클 것으로 예상되는지 (예: A는 HVAC 효율 관련 변수의 비중↑, B는 envelope U-value 관련 변수의 비중↑)
	- 이 차이가 Results의 비교 축을 형성