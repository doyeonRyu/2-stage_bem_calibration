# Methodology Draft

> Author: 유도연   
> Date: 2026.05.02.   

---

## 1. Framework Overview

- 설계 원칙 (5개)
	- **Search–reasoning 분해**
		- Stage 1 (Search Problem): 자동/구조화된 최적화로 광범위 변수 공간 탐색
		- Stage 2 (Reasoning Problem): Search 결과의 진단/정제 reasoning을 사전 정의된 구조 안에서 수행
	- **Structured automation across both arms** 
		- 두 stage 모두 결정이 자유 생성에 흐르지 않도록, *명시된 단계/ 역할 / 변수 도메인 / 물리 제약* 안에서만 결정
		- Stage 2: 자유 생성형 LLM 후처리가 *아니라* Stage 1 위에서 작동하는 *제약된 reasoning 계층*
	- **Literature-grounded variable backbone (implementation 수단)** 
		- Step 0의 변수 list: 선행 GA·최적화 기반 보정 연구의 calibration target에서 채택
	- **최적화 우선, reasoning은 그 다음** (Stage 1 = search, Stage 2 = 진단·정제 reasoning)
		- 광범위 search 문제는 자동 최적화로 처리하고 잔차의 구조적 정제는 specialist reasoning 계층에서 작동
	- **Structural reproducibility** 
		- 본 framework가 주장하는 reproducibility: **structural reproducibility**
		- LLM 출력 변동과 무관하게 *동일한 변수 list, 동일한 specialist 역할 분해, 동일한 진단 계층, 동일한 제약 메커니즘*이 매 실행마다 적용
		- 어떤 LLM이 호출되든 calibration narrative의 골격은 동일하게 유지
		- 이는 free-form generative AI 보정과 본 framework를 가르는 핵심 축이며, *structured reasoning* 측의 운영적 근거

- 단계 정보 흐름
```
Step 0  Pre-calibration baseline & literature-grounded variable selection
        - Baseline OSM 구축
        - 선행 GA·최적화 기반 보정 연구의 calibration target 변수 채택
        - 채택 기준 명시 (빈도·물리 매커니즘 정합)
        - 산출: Stage 1·2 공유 flat 변수 list
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
              |
              v
Step 3  두 채의 실측 건물에 대한 검증
        - 정확도, ablation, 라우팅 해석 가능성, 전이 가능성
```

```markdown
Sub Contribution

1. Contribution 1
    - 선행 Generic algorithm, optimization 기반 calibration 조사를 통해 calibration target 변수를 선정
    - 해당 변수들은 step 1, 2에서 모두 사용

2. Contribution 2
    - Optuna algorithm
    - 확장된 변수 list에 대해 Optuna hyperparameter optimization 반복
    - 한 round 종료 시: search space 갱신, freeze 변수 갱신 (조건에 맞으면)

3. Contribution 3
    - Structured Specialist Multi-agent Reasoning
    - 최적화 단독 시: 왜 그 값에 도달했는지, 잔차의 어느 구조를 정제해야 하는 지 등 reasoning 계층이 부재 -> reasoning gap 해결
    - 진단 agent -> specialist agents (병렬) -> Reality / critic agent -> orchestrator agent 반복
    - 규칙, 역할 기반 agent 작동으로 자유 생성 차단 (structural reproducibility)
```

## 2. Step 0 - Pre-calibration Baseline & Literature-grounded Variable Selection

> 목적: Stage 1·Stage 2가 공유할 baseline OSM과 literature 근거를 갖춘 flat 변수 list를 산출 

1. **Baseline OSM 구축**
	- Revit -> (gbXML) -> SketchUp(오류 수정) -> OpenStudio
	- Geometry, zoning, 외피 재료/레이어, HVAC 토폴로지 반영
2. **선행 GA·최적화 기반 보정 연구의 calibration target 변수 채택**
	- 채택 기준: (a) 선행 연구 등장 빈도, (b) 물리 매커니즘 정합성
	- 산출: 변수명·단위·literature range·출처가 명시된 flat 변수 list (`background/variables_setting.md`)
	- Related Works 파트가 아닌 여기서 출처 정리 예정
	- 사례별 수동 변수 선정 비용 회피 (literature-grounded backbone)
3. **Step 0 Output (Step 1으로 산출)**
	1. baseline OSM
	2. 채택 변수 목록 + 단위 + literature range + 출처 - Stage 1, 2가 모두 사용

## 3. Step 1 - Optuna Optimization (Stage 1, search arm)

> 목적: Step 0에서 확정된 flat 변수 list를 입력으로, Round 0의 SA/correlation 1회 screening 이후 *비-freeze 전 변수 동시* Optuna(TPE) study를 라운드 반복하여 baseline calibrated model을 확보

0. 왜 최적화를 먼저 하는가.
	- Step 1이 푸는 문제는 **search problem**: 
		- 광범위 연속/준연속 변수 공간에서 baseline 대비 어떤 변수 조합이 J를 가장 낮추는지 찾는 일
		- LLM·에이전트가 이런 공간을 직접 탐색하면 비효율적이고 ad-hoc 해진다 -> 우선 구조적 최적화로 공간을 축소
	- 이 단계에서 Optuna(베이지안 기반 TPE)를 채택하는 이유:
		 비-freeze 변수에 대한 동시 study 구성과 search space 동적 갱신에 적합하기 때문
		- 단, 이 단계는 search 결과의 해석·진단 reasoning을 제공하지 않는다 
		— 왜 그 값에 도달했는지·잔차의 어느 구조를 정제해야 하는지 설명 부재. 
		- 이 reasoning gap이 Stage 2의 정당화 지점이며, 본 연구의 primary novelty 무게중심

1. Round 0 — SA/correlation 기반 변수 screening (1회)
	- 입력: Step 0의 flat 변수 list (Optuna 식별자 15개; envelope direct 5 + multiplier 6 + offset 2 + shift 1 + 2차 multiplier 2)
	- 절차: Latin Hypercube Sampling + Spearman rank correlation (또는 Morris screening) 1회 수행
	- 출력: 비중요 변수 screening 후 active 변수 집합. 비활성 변수는 baseline 값으로 freeze.
	- Round 0 단일 1회 한정 

2. Search space 설정
	- 비-freeze 변수: `current_value ± alpha`, alpha는 변수 유형별로 다르게 (multiplier·offset·shift·direct), 라운드 간 `α_new = ρ·α_old`로 축소
	- **Hybrid clamp** (envelope 물리 변수만 적용): `wall_u_value`, `roof_u_value`, `window_u_value`, `window_shgc`, `floor_u_value`, `oa_or_fan_multiplier`는 Optuna sampler 단계에서 literature range로 강제 clamp (`background/variables_setting.md` §3 참조). 그 외 multiplier/offset/shift는 `current_value ± α` 자유 search.
	- α 초기값은 본 round에서 잠정 설정하며, 추후 선행 Optuna 보정 연구 조사를 통해 근거 부여 또는 조정한다 (`Discussion #1` 임계값 sensitivity로 implicit 정당화).

3. 목적함수 J 정의
	- `J = w1·CVRMSE_elec + w2·CVRMSE_gas + w3·|MBE_elec| + w4·|NMBE_gas|`
	- P_phys, P_complex 항 제외 
	- 물리 타당성 검토는 Stage 2 Reality agent로 일관 위임하며, 
	- Stage 1은 envelope 변수에 대한 hybrid clamp만 적용
	- 가중치는 case별로 결정하되 한 연구 내에서는 고정 
	- ASHRAE G14 임계값(monthly CVRMSE ≤ 15%, |NMBE| ≤ 5%)에 비례한 정규화 가중을 1차 후보로 설정

4. 라운드 기반 변수 동시 Optuna 튜닝 (Round 1+)
	- 라운드당 trial 수 `n_trial = 10` - osm simulation이 너무 오래걸림
	- 라운드당 비 freeze 변수 optuna
	- 라운드 종료 시 전역 J 평가, per-variable freeze 판정, search space 수정

5. Search space 갱신 및 freeze 결정 (결정론적 규칙)
	- **변수 freeze**: 변수 상대 변동 `|v_curr − v_prev| / |v_prev| < θ_freeze` 가 2 라운드 연속 충족 시 freeze (`θ_freeze = 5%`)
	- **Search space 축소**: 비-freeze 변수의 `α_new = ρ · α_old` (`ρ = 0.7`)
	- **Alpha 경계 도달 변수**: 다음 라운드에 alpha 1회 확장 (`× 1/ρ`); 재도달 시 경계로 freeze. envelope hybrid clamp 변수는 literature range 경계 도달 시 *그 자리에서 freeze* (확장 없음).
	- **J 악화 시**: best-so-far 모델 유지, 해당 라운드 freeze 갱신 *건너뜀*

6. 종료 조건 (결정론적 규칙)
	- **수렴 종료**: `(J_prev − J_curr) / J_prev < θ_J` 가 2 라운드 연속 (`θ_J = 1%`)
	- **Freeze 종료**: 모든 변수가 freeze 상태에 도달
	- **Hard cap**: 라운드 수 `R_max = 7` 도달 시 강제 종료 (안전장치)

7. Stage 1 Output (Stage 2로 보낼)
	- 보정된 baseline OSM, 변수별 최종값, freeze 변수 목록 (Round 0 SA-screened freeze + Round + 변동 수렴 freeze), 잔차 패턴, 변수별 잔치 기여도

8. Inter-round Orchestration Protocol (Stage 1의 *결정론적 자동화* 메커니즘)

	> 본 protocol은 Stage 1을 *완전 자동* 루프로 운영하기 위한 사전 정의된 임계값·규칙 집합이다. 모델러는 임계값을 *한 번* 설정한 뒤 어떤 건물에도 동일하게 적용하므로, 사례별 라운드 운영 수동 개입이 사라진다 — 이는 §Framework Overview "Structured automation across both arms" 원칙의 운영적 근거이며 §Introduction §8 *structured search* 주장의 조작적 정의이다.

	### 임계값 표

| 규칙 | 기호 | 권장 값 | 정의 |
|---|---|---|---|
| 라운드당 trial 수 | `n_trial` | 100 | 라운드 1회당 *비-freeze 전 변수 동시* Optuna(TPE) trial 수 (변수 수에 비례 조정 가능) |
| 라운드 수렴 종료 | `θ_J` | 1% | `(J_prev − J_curr)/J_prev < θ_J` 2 라운드 연속 |
| Hard cap | `R_max` | 7 | 안전장치, 도달 시 강제 종료 |
| 변수 freeze | `θ_freeze` | 5% | 변수 상대 변동 `< θ_freeze` 2 라운드 연속 |
| Search space 축소 | `ρ` | 0.7 | 비-freeze 변수 `α_new = ρ · α_old` |
| Round 0 SA screening | — | 1회 | LHS + Spearman (또는 Morris); 비중요 변수는 baseline 값으로 freeze |
| Freeze 종료 | — | 모든 변수 freeze | 자동 종료 |
| J 악화 처리 | — | best-so-far 유지 | 해당 라운드 freeze 갱신 건너뜀 |
| Alpha 경계 도달 | — | 1회 확장 -> 재도달 시 freeze | `× 1/ρ`; envelope hybrid clamp 변수는 literature 경계 도달 시 즉시 freeze |
| Envelope hybrid clamp | — | 적용 | `wall_u_value`, `roof_u_value`, `window_u_value`, `window_shgc`, `floor_u_value`, `oa_or_fan_multiplier`만 sampler 단계에서 literature range 강제 |

### 의사코드

```
# Round 0: SA screening (1회)
active_vars = SA_screening(all_vars, n_lhs, threshold)   # LHS + Spearman or Morris
freeze_set  = all_vars - active_vars                     # 비활성 변수는 baseline로 freeze

initialize: alpha_per_var (active_vars), J_best = J(baseline), round = 1, stagnant = 0
while round <= R_max:
	space = build_search_space(active_vars - freeze_set, alpha_per_var, hybrid_clamp)
	optuna.optimize(study, n_trials=n_trial, search_space=space)   # 비-freeze 전 변수 동시
	J_curr = evaluate_global_J()
	if J_curr < J_best:
		update_model(); update_freeze_per_var(theta_freeze); shrink_alpha(rho)
		delta = (J_best - J_curr) / J_best
		J_best = J_curr
		stagnant = stagnant + 1 if delta < theta_J else 0
	else:
		# J 악화: best-so-far 유지, freeze 갱신 건너뜀
		stagnant += 1
	if stagnant >= 2: break                              # 수렴 종료
	if all_variables_frozen(active_vars): break          # freeze 종료
	round += 1
```

### 임계값의 case-independence 주장
- 임계값은 framework 수준에서 *한 번 설정 -> 모든 건물에 동일 적용*
- 임계값 sensitivity (θ_J, θ_freeze, ρ ±50%; α 초기값)는 §Discussion에서 robustness 분석으로 보고
- 이로써 라운드 수·freeze 시점이 *임의 조정* 의심을 받지 않음 -> §Results 비교 실험 fairness 근거

---

## 4. Step 2 — Diagnosis-driven Specialist Multi-agent Refinement (Stage 2)

> 목적: 진단 agent -> specialist agents -> reality / critic agent -> orchestrator agent 반복 실행

0. 왜 Stage 1을 대체가 아니라 후속으로 두는가 
	- Step 1 종료 시점에는 탐색 공간이 줄고 잔차가 구조적으로 드러남
	- 이때 필요한 건 새로운 전역 탐색이 아니라 *진단과 정제 reasoning* (Stage 1이 남긴 reasoning gap을 메우는 단계)
	- 최적화 단독은 *해석·진단* reasoning이 없어 잔차의 구조적 정제로 이어지지 않음
	- Stage 2 단독 사용 시 한계: 중요/비중요 변수 구분 없이 자유 수정안을 제시 -> 사례별 ad-hoc 조정으로 흐르고 재현성이 약화됨
	- 따라서 Stage 2는 Stage 1 위에서 작동하는 *constrained reasoning layer*로 정의 (자유 생성형 AI 후처리가 아님 - perationalization은 #6 Constraint Enforcement에서 명시)
	- 전체 흐름: "structured search -> structured diagnosis -> structured specialist reasoning"

1. 에이전트 구조 (작동 순서별)
	1. Dianositic agent
		- **역할**
			- 전력, 가스 통합 해석
		- **입력**
			- Stage 1 산출물의 월별 전력, 가스 잔차 + 변수별 J 기여도
		- **출력**
			1. 전력 잔차 시그니처
			2. 가스 잔차 시그니처
			3. 두 modality의 교차 시그니처 (예: 여름 cooling 전력 bias와 shoulder 가스 bias 동시 발현)
			4. 시그니처와 정합하는 variable candidate list
		- **책임 원칙**
			- 잔차 시그니처 해석 + variable candidate list 생성 (변수 *값*은 수정 ✗)
		
	2. Orchestrator (Phase 1) agent
		- **역할**
			- diagnostic의 variable candidate list로부터 variable subset 분할 + specialist 인스턴스 호출, 할당
		- **입력**
			- 
		- **출력**
			- 
		- **책임 원칙**
			- candidate list로부터 variable subset 분할 + specialist 호출·할당 (변수 *값*은 수정 ✗)

	3. Specialist agents
		- **역할**
			- orchestrator가 라운드별 동적으로 호출·할당하는 인스턴스
			- 동일 라운드에 여러 인스턴스가 *서로 다른 variable subset*을 담당하며 병렬 호출
		- **출력**
			- 후보안 1개 = (변수 식별자, 신규 값, 물리 매커니즘 사유) tuple list
		- **책임 원칙**
			- 할당된 variable subset 내 수정안 제안 (할당 외 변수·freeze 변수 수정 불가; schema-validated)

	4. Reality agent
		- **역할**
			- specialist 후보안 *사후 검토*에만 호출됨 (라운드 시작 시점에는 호출되지 않음)
		- **입력**
			- 각 special agents의 후보안들
		- **출력**
			- 검토 후 최소 수정된 후보안들
		- **책임 원칙**
	
	5. Orchestrator (Phase 2) agent
		- **역할**
			- 변수 값 수정 권한 없음. routing·할당·채택·freeze 결정만 수행
			- specialist 후보안 + reality 검토 결과로부터 채택 / hybrid / 기각 결정 + freeze 갱신
		- **입력**
			- 
		- **출력**
			- 
		- **책임 원칙**
			- LLM 기반 *추론*; 정적 if-then 규칙이 아님 (단, 출력은 #6 (a) schema validation으로 변수 식별자 어휘 안에서만 허용)
			- 채택 / hybrid / 기각 + freeze 갱신 (변수 *값*은 수정 ✗)


4. 라운드 프로토콜 (5-step multi-agent 흐름)
	1. **diagnostic** (단일 에이전트, 전력·가스 통합) → 잔차 시그니처 + variable candidate list 생성
	2. **orchestrator phase 1** → candidate list로부터 variable subset 분할 + specialist 인스턴스 호출·할당
	3. **specialists** (병렬) → 각 1개 후보안 생성 (할당된 subset 내에서만)
	4. **reality** → 후보안 hard physics + soft plausibility 검토 (pass / hold / reject)
	5. **orchestrator phase 2** → 채택 / hybrid / 기각 + freeze 갱신
	- 라운드 *시작 시점*의 reality 호출은 두지 않는다 — reality는 specialist 후보안 *사후* 검토에만 작동
	- 종료 조건은 # Methodology # 4.7에서 본문화 (전역 J 수렴·freeze 종료·hard cap)

5. Initial routing prior (orchestrator phase 1 참고용 사전 지식)
	- 본 절의 라우팅 매핑은 orchestrator에 *고정 if-then 규칙*으로 주어지지 않고, *물리 직관 기반 prior*로 prompt에 제공된다. orchestrator는 이를 참고하되 diagnostic의 variable candidate list와 잔차 시그니처 컨텍스트에 따라 *재해석*할 수 있다. 본 prior는 Step 0 변수 list 위에서 *변수 시그니처*(name·unit·physical role)에 직접 매칭되며, 사전 6개 prior 카테고리 등 고정 taxonomy를 전제하지 않는다.
	- prior 예시 (변수 시그니처 기반):
		- diagnostic이 내부부하/운영 패턴 전력 시그니처를 보고했을 때 → 내부부하 관련 변수 (LPD, EPD, occupancy density, 운영 schedule) 우선 후보 subset
		- diagnostic이 winter 난방 가스 시그니처를 보고했을 때 → 외피·공기 흐름 관련 변수 (Wall/Roof/Window U-value, infiltration), 난방 setpoint, HVAC/난방 효율 관련 변수 우선 후보 subset
		- diagnostic이 baseload·shoulder 가스 시그니처를 보고했을 때 → DHW 관련 변수, 운영 schedule, 외피 관련 변수 우선 후보 subset
		- diagnostic이 *교차 시그니처*(전력+가스 동시)를 보고했을 때 → 두 modality에 동시 영향을 주는 변수 (운영 schedule, HVAC availability, 점유 density) 우선 후보 subset
		- diagnostic이 반복 지목하는 변수 subset → 우선순위 상승
	- 이 설계는 Sun(2022)의 *정적 pattern-rule lookup*과 다르다 — 본 framework는 prior를 LLM orchestrator의 *해석 가능한 컨텍스트*로 제공하고 routing의 최종 결정 (variable subset 분할 + specialist 할당)은 LLM reasoning에 위임한다.

6. 후보안 채택 규칙 (orchestrator phase 2)
	- 고려 요소: 전역 J 개선, 전력·가스 잔차 시그니처 변화, reality 의견 (pass / hold / reject)
	- 채택 형태:
		- 단일 specialist 후보안 우세 → 그대로 채택
		- 복수 후보안이 *비충돌·상보적*인 경우에 한해 hybrid 허용 (예: 서로 다른 variable subset에 대한 수정안)
		- reality reject 후보안 → 자동 기각
		- reality hold + J 개선 미미 → 다음 라운드 재고
	- freeze 갱신: §3 Stage 1과 동일한 per-variable 변동 < θ_freeze 기준; Stage 2 freeze는 Stage 1 freeze 위에 *누적*된다

7. Constraint Enforcement (Stage 2가 자유 생성형이 *아닌* 메커니즘)
	 1. **Domain restriction**: 
		 - 각 specialist 인스턴스의 출력은 *orchestrator phase 1이 해당 라운드에 할당한 variable subset* 외부를 수정할 수 없다 (schema validation으로 강제). 
		 - 변수 list 외 변수 신설·정의 변경도 불가. 
		 - Stage 1·Stage 2 누적 freeze 변수 수정도 불가.
	 2. **Hard physics constraint**: 
		 - Reality agent의 hard layer가 외부 표준(ASHRAE 90.1/G14/62.1, 국토교통부 건축물 에너지절약설계기준 등)과 building physics 기본 원리에서 도출된 binary reject 규칙을 적용한다. 
		 - 위반 시 자동 reject (orchestrator phase 2 입력 단계에서 reject 후보안은 채택 후보에서 제외).
	 3. **Soft plausibility check**: 
		 - Reality agent의 soft layer(LLM)가 표준 범위 내의 *결합 모순*(예: 외피 매우 우수 + 침기율 매우 높음)에 대해 hold/pass 의견을 낸다.
	 4. **Adoption rule**
		 - Orchestrator phase 2는 §5의 채택 규칙(단일 우세 / 비충돌 hybrid / 기각)만 허용하며, 임의 합성·자유 생성 채택을 금지한다.
	 5. **Audit log**: 
		 - 5-step 라운드의 모든 단계 (diagnostic 출력, orchestrator phase 1 routing 결정, specialist 후보안, reality 판정, orchestrator phase 2 채택·freeze)는 *변수 identifier 어휘*(Step 0 변수 list의 정규화 변수명)로 로깅되며, 
		 - 이로써 # Framework Overview의 *structural reproducibility*가 운영적으로 보장된다.

## 5. Case Study Buildings — 두 채의 실증 건물

> 목적: 환경·특성이 *대비되는* 두 건물을 선정해 framework의 적용성(C-Validation)을 두 contrasting case에서 시연한다. 본 case study는 *통계적 일반화 증명*이 아니라 *서로 다른 운영·물리 조건에서의 framework 적용성과 동일 변수 list·에이전트 토폴로지의 재설계 없는 적용*을 보이는 데 목적이 있다.

1. 케이스 선정 원칙
	- 전이 가능성 검증을 위해 building type / 규모 / 시스템 / 운영 패턴이 대비되는 두 건물 선정
2. Building A
	- 위치 / 기후대 / 용도 / 연면적 / 층수
	- HVAC 시스템 개요
	- 운영 스케줄 특성
	- 실측 데이터: 기간, 해상도(월별·일별·시간별), 전력/가스 항목
3. Building B (동일 구조)
	- 위치 / 기후대 / 용도 / 연면적 / 층수
	- HVAC 시스템 개요
	- 운영 스케줄 특성
	- 실측 데이터: 기간, 해상도, 전력/가스 항목
4. Baseline OSM 구축 결과
	- 두 건물의 Step 0 baseline 모델 요약 (geometry, zoning, 외피, HVAC 토폴로지)
	- Baseline 모델의 *보정 전* 성능 (월별 CVRMSE/NMBE 표 1개)
5. 두 건물의 차이가 framework에 던지는 도전
	- 어떤 *variable subset*에서 차이가 클 것으로 예상되는지 (예: A는 HVAC 효율 관련 변수의 비중↑, B는 envelope U-value 관련 변수의 비중↑)
	- 이 차이가 §Results의 비교 축을 형성
---

## Notes

### Figure 필요 지점

| # | 위치 | 내용 | 비고 |
|---|---|---|---|
| Fig 1 | §1 단계 정보 흐름 | 4-step framework block diagram (Step 0 → Step 1 → Step 2 → Step 3, 단계 간 입출력 화살표 + 변수 식별자 어휘 공유 표시) | 본문 ASCII block을 정식 도식으로 승격 |
| Fig 2 | §4 §3 라운드 프로토콜 | Stage 2 5-step multi-agent 흐름 도식 (① diagnostic → ② orchestrator phase 1 → ③ specialists 병렬 → ④ reality → ⑤ orchestrator phase 2; 각 step의 입출력 데이터 표기) | Stage 2의 *primary novelty* 시각화 — paper의 핵심 figure |
| Fig 3 | §4 §1 에이전트 구조 | 3계층 에이전트 토폴로지 + 변수 식별자 어휘 인터페이스 (Diagnostic·Reality·Orchestrator·Specialist 인스턴스 간 데이터 흐름 + Stage 1 freeze 변수 인계 화살표) | §1 Framework Overview "두 arm 인터페이스" 도식과 통합 가능 |

### Table 필요 지점

| # | 위치 | 내용 | 비고 |
|---|---|---|---|
| Tbl 1 | §2 변수 채택 결과 | Literature-grounded flat 변수 list (1차 13 + 2차 5) — 정규화 변수명·단위·literature range·출처 | `background/variables_setting.md` §3 표를 정본으로 인용 |
| Tbl 2 | §3 §8 Stage 1 임계값 표 | Inter-round Orchestration Protocol 임계값 (n_trial, θ_J, θ_freeze, ρ, R_max, alpha 경계 처리, hybrid clamp 등) | 본문에 이미 있음 — caption·번호만 부여 |
| Tbl 3 | §4 §3 5-step 라운드 흐름 표 | step·행위자·입력·출력·제약 5컬럼 표 (현재 numbered list로 작성) | bullet list를 표로 정리해 가독성 ↑ |
| Tbl 4 | §4 §1 에이전트 입출력 표 | Diagnostic·Reality·Orchestrator(phase 1·phase 2)·Specialist의 입력·출력·수정권한 매트릭스 | "수정권한 없음 / subset 내 수정" 등 권한 경계를 한 표로 가시화 |
| Tbl 5 | §4 §6 Constraint Enforcement 표 | (a) Domain restriction · (b) Hard physics · (c) Soft plausibility · (d) Adoption rule · (e) Audit log 5개 메커니즘 — 적용 계층·강제 방식·위반 시 처리 | "Stage 2가 자유 생성형이 아닌 메커니즘"의 운영적 증거 |

### 추가 확인 필요 사항

- `variables_setting.md` §6의 옵션 A/B/C 결정 (현재 본 draft는 *암묵적 그룹화* 입장 = 옵션 A에 가까움; 사용자 확정 필요)
- Optuna 변수의 multiplier·offset·shift 파라미터화를 §2 또는 §3 어디에서 본문화할지 결정
- Fig 2 (5-step 흐름)와 Fig 3 (3계층 토폴로지) 분리 vs. 통합 한 장 결정 — 분리하면 narrative 명료, 통합하면 Stage 2 전체를 한 장에 압축
- §3 §7 Stage 1 출력 → §4 입력 매핑 도식이 별도 figure로 필요한지 여부 (현재는 §4 §0 narrative만으로 커버)
