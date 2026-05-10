# 논문 초안

> 저자: 유도연  
> 초안 작성일: 2026-04-29

투고 목표 (1순위): _Energy and Buildings_  
대안: _Applied Energy_, _Journal of Building Performance Simulation_, _Building and Environment_

---

## Title (후보)

1. A Search-and-Reasoning Two-Stage Calibration Framework for Building Energy Models: Iterative Joint Optimization with Constrained Specialist Multi-agent Reasoning
2. From Search to Reasoning: A Structured Two-Stage Calibration Framework for Building Energy Models Integrating Automated Optimization and Diagnosis-Driven Specialist Refinement
3. Structured Calibration of Building Energy Models via Search-and-Reasoning: A Two-Stage Framework Combining Iterative Optimization with Constrained Specialist Reasoning

> **memo**:  
> 주요 novelty: "`structured search`는 갖췄으나 search 결과의 `reasoning`이 부재한 전통 최적화"와 "`reasoning`은 있으나 `자유 생성에 가까운 LLM 자동화`" 사이의 비어있는 사분면 보강

---

## Introduction

### 1. Problem Statement

1. 건물 에너지 모델링의 필요성
2. 건물 에너지 보정 과정의 중요성 및 보정된 건물 모델의 활용
3. 보정 과정 자체의 일반적 문제 (노동 집약적 / 시간 소요 / 사례 의존)
4. 현재 건물 에너지 보정 분야의 트렌드 (Optimization / Rule-based automation, Multi-step / Staged calibration, Multi-agent calibration / 3~5문장으로 압축, 상세는 Related Works에서 기재)

### 2. Research gap

- 개별 방법론(staged calibration, optimization, pattern diagnosis, multi-agent automation)이 부족한 것은 아님 — 각 영역은 충분히 성숙
- 실제 공백: 보정의 두 측면을 모두 구조화된 절차로 통합한 자동 보정 framework의 부재
- 두 사분면의 위치
    - 전통 최적화 / 다단계 보정 (Pachano'21, Baba'22, Liang'25 등):
        - structured search O / structured reasoning X
        - search 결과의 **해석 / 진단 / 정제** reasoning 계층 부재
    - 패턴 기반 보정 (Sun'22 등)
        - reasoning 일부 O (정적 if-then) / structured search 결합 부재
    - LLM 자유 생성 멀티에이전트 (Lu'25, Xu'25, Xiao'24 등)
            - reasoning 일부 O (자유 생성) / structured search X
    - 본 연구의 자리:
        - 두 측면을 **모두 구조화된** 형태로 통합하는 비어있는 사분면.

1. **Structured search (Stage 1)**
    - 광범위 변수 공간에서 optuna 하이퍼 파라미터 최적화로 rule-based 최적값 탐색
    - reasoning이 작동할 **축소된 변수 공간과 구조적 잔차**를 제공하는 implementation 수단으로 작동
2. **Structured reasoning (Stage 2)**
    - search 결과의 진단·정제를 사전 정의된 단계 / 역할 / 변수 도메인 / 물리 제약 안에서 수행
    - reasoning이 가능하다는 novelty

### 3. Research Question

> 보정의 search 측면과 reasoning 측면을 모두 **구조화된 자동 절차**로 통합하는 보정 framework를 어떻게 설계할 것인가?

### 4. Approach Overview

> search 측면과 reasoning 측면을 통합하는 2단계 프레임워크

- Step 1 (search):
    - Optuna 하이퍼파라미터 최적화 알고리즘
    - 구조화, 축소된 변수 search
- Step 2 (reasoning)
    - specialist multi-agent가 진단 결과에 따라 정제 reasoning을 수행하되,
    - orchestrator가 할당한 variable subset / 진단 / reality 제약이 **사전 정의된 구조** 안에서만 작동

### 5. Contribution

기존 BEM calibration 연구

- `search` 측면(최적화·다단계)과 `reasoning` 측면(진단 / LLM multi-agent)을 각각 발전시켜 왔으나, 두 측면을 모두 구조화된 형태로 통합한 자동 보정 절차는 부재함

본 논문의 주요 기여

- search와 reasoing을 단일 framework 안에서 통합하여 자동, 구조화된 보정 절차 제공
- 최적화, 단계별 calibration의 한계점인 reasoning 문제 해결
- LLM-based calibration의 한계점인 자유 생성 -> 구조화
- Stage 1: reasoning이 작동할 축소된 변수 공간과 구조적 잔차를 제공하는 search 단계 역할

```markdown
Primary Contribution

- Structured Search and Reasoning Calibration
    
- calibration을 search problem / reasoning problem으로 분해
    
- Stage 1: Optuna hyperparameter optimization를 통한 보정 변수 구조화 및 search space 축소
    
- Stage 2: 제약 및 역할이 사전 정의된 LLM-based multi-agent를 통한 reasoning calibration automation
    
- 전통 최적화의 reasoning 부재와 LLM 자유 생성의 구조 부재를 동시에 해결
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

Validation

- 두 조건이 다른 건물에서 적용성 검증
    - 환경, 특성이 대비되는 두 채의 실측 건물
    - 수동 재설계 없이 적용 
      -> 정확도 개선, 단계별 ablation, 라우팅 해석 가능성, 사례 의존적 수동 비용 부재 시연

---

## Related Works

1. Review / Positioning
	1. Chong et al. (Energy and Buildings, 2021)
		- automatic calibration은 optimization과 Bayesian 접근이 중심이라고 주장
		- 입/출력, 데이터 해상도, 평가 지표, 재현성 이슈 지적

	2. Vera-Piazzini and Scarpa (Journal of Building Engineering, 2024)
		- variability 분석과 재현성 문제, 표준화된 절차 필요성 강조
	-> 한계점: 표준화된 보정 절차와 재현성이 분야 차원에서 미해결

2. 최적화 기반 자동 보정
	1. Pachano and Bandera (Energy and Buildings, 2021): measured data 기반의 multi-step, optimization-driven calibration 절차 제안
	2. Gonzalez and Bandera (Building Simulation, 2022): EnergyPlus의 HybridModel:Zone를 활용해 measured indoor temperature만으로 infiltration과 internal mass를 추정하는 inverse modeling 기반 calibration 방법을 제안
	3. Kounni et al. (Energy and Buildings, 2023): 2-step calibration 제안. (1) detailed modeling, (2) Pymoo 기반 유전 알고리즘 calibration
	4. Jiang et al. (Energy and Buildings, 2024): deep learning surrogate와 Bayesian calibration을 결합한 framework 제안   
	
	-> 한계점: structured search 절차는 갖췄으나 search 결과의 *해석·진단·정제* reasoning 계층이 부재 -> **structured reasoning 축이 약함**

3. 단계적 (Multi-step / Staged) 보정
	1. Baba et al. (Building and Environment, 2022): 민감도 -> 후보 축소 -> 다목적 GA 보정을 통한 여러 공간 동시 calibration
	2. Liang et al. (Applied Thermal Engineering, 2025): 2-stap calibration 제안. (1) 비점유시 정적 변수, (2) 점유 시 점유 패턴과 동적 변수 조정   

	-> 한계점: structured staging은 분명하나 단계 경계 정의가 사례 특수적, 수동적이며, 단계 간 reasoning 연결이 부재 -> **structured reasoning 축이 약함**

4. 패턴 기반 / 규칙 기반 진단
	1. Sun et al. (Building Simulation, 2022): 월별 오차 패턴 기반 자동 보정 로직   

	-> 한계점: : 정적 reasoning(if-then)은 갖췄으나 일반화·structured search 결합 부재 -> **structured search와 일반화 축이 약함**

5. 건물 에너지 분야의 멀티에이전트 / LLM 자동화
	1. Xiao and Xu (Energy and Buildings, 2024): planner / researcher / advisor 역할의 LLM multi-agent
	2. Lu et al. (iScience, 2025)
		- geometry -> parameter -> calibration -> retrofit end-to-end LLM multi-agent
		- 각 과정에서 자연어로 직접 명령해줘야 함
		- Calibration 과정에서 단순 유전 알고리즘 사용
	3. Xu et al. (Energy and Buildings, 2025)
		- A2A/MCP 기반 동적 멀티에이전트 네트워크 (BEM-AI)   

	-> 한계점: Calibration 과정 부재·specialist 도메인의 명시적 제약 부재 -> **structured search와 structured reasoning 모두 약함**

6. Related Works summary
	- 핵심 메시지: 2-stage 자체는 novelty 아님
	- 차별점은 **`structured search 절차`와 `structured reasoning 절차`의 통합**이며, 
	- primary novelty 무게중심: stage 2(reasoning)
	- 2x2 위치 framing

|                  | structured search | structured reasoning |
| ---------------- | ----------------- | -------------------- |
| 전통 최적화·다단계 보정    | O                 | X                    |
| 패턴 기반 보정         | X                 | 일부                   |
| LLM 자유 생성 멀티에이전트 | X                 | 일부                   |
| 본 연구             | O                 | O                    |

---

## Methodology

### 1. Framework Overview

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

### 2. Step 0 — Pre-calibration Baseline & Literature-grounded Variable Selection

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

### 3. Step 1 — Iterative Joint Optimization (Stage 1, search arm)

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

	#### 임계값 표

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

#### 의사코드

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

#### 임계값의 case-independence 주장
- 임계값은 framework 수준에서 *한 번 설정 -> 모든 건물에 동일 적용*
- 임계값 sensitivity (θ_J, θ_freeze, ρ ±50%; α 초기값)는 §Discussion에서 robustness 분석으로 보고
- 이로써 라운드 수·freeze 시점이 *임의 조정* 의심을 받지 않음 -> §Results 비교 실험 fairness 근거

---

### 4. Step 2 — Diagnosis-driven Specialist Multi-agent Refinement (Stage 2)

> 목적: Stage 1이 남긴 *reasoning gap*(잔차의 구조적 해석 부재)을 진단·정제 reasoning 계층으로 메우되, 사전 정의된 단계·역할·변수 어휘·물리 제약 안에서만 작동시킨다. Stage 2 라운드는 *diagnostic → orchestrator phase 1 → specialists(병렬) → reality → orchestrator phase 2*의 5-step multi-agent 흐름으로 구성된다.

0. 왜 Stage 1을 대체가 아니라 후속으로 두는가
	- Step 1 종료 시점에는 탐색 공간이 줄고 잔차가 구조적으로 드러남
	- 이때 필요한 것은 새로운 전역 탐색이 아니라 *진단과 정제 reasoning* (Stage 1이 남긴 reasoning gap을 메우는 단계)
	- 최적화 단독은 *해석·진단* reasoning이 없어 잔차의 구조적 정제로 이어지지 않음
	- Stage 2 단독 사용 시 한계: 중요/비중요 변수 구분 없이 자유 수정안을 제시 → 사례별 ad-hoc 조정으로 흐르고 재현성이 약화됨
	- 따라서 Stage 2는 Stage 1 위에서 작동하는 *constrained reasoning layer*로 정의 (자유 생성형 AI 후처리가 아님 — operationalization은 §4.7 Constraint Enforcement에서 명시)
	- 전체 흐름: "structured search → structured diagnosis → structured specialist reasoning"

1. Stage 2 작업 pool과 Stage 1 status의 prior 사용
	- **Stage 2 pool**: Step 0에서 정의된 22개 변수 전체 (Stage 1 active·freeze·미활성 status 모두 포함)
	- **Stage 1 status는 prior 정보**: Stage 1의 active/freeze/미활성 구분은 Stage 2의 *prior 정보*로만 작동하며 hard constraint로 전이되지 않는다. Stage 1이 freeze한 변수도 diagnostic이 잔차 시그니처로 명시 지목할 경우 candidate list에 재포함될 수 있다. 이는 Stage 1 search가 미처 다루지 못한 변수를 reasoning 계층이 보강할 수 있도록 하기 위함이며, 본 framework가 주장하는 *reasoning gap 해결* novelty의 운영적 정의이다.
	- **변수 어휘 한정**: Step 0 22개 변수 외 신규 변수 정의·생성은 불가
	- **Stage 2 freeze는 Stage 2 라운드 내에서만 누적**: Stage 1 freeze 위에 누적되지 않는다. Stage 2 freeze 갱신 기준은 §4.5의 채택 규칙에 따른다.

2. 에이전트 구조 (작동 순서별)

	1. **Diagnostic agent**
		- **역할**: 전력·가스 잔차의 통합 해석 + 22개 pool에서 시그니처 정합 candidate list 생성
		- **입력**
			- Stage 1 산출물: 월별 전력·가스 잔차, 변수별 J 기여도
			- Step 0 22개 변수 pool (Stage 1 status — active/freeze/미활성 — 포함; status는 prior 정보)
		- **출력**
			1. 전력 잔차 시그니처
			2. 가스 잔차 시그니처
			3. 두 modality의 교차 시그니처 (예: 여름 cooling 전력 bias와 shoulder 가스 bias 동시 발현)
			4. 시그니처와 정합하는 variable candidate list (22개 pool 전체에서 도출 가능; Stage 1 freeze 변수 포함 허용)
		- **책임 원칙**
			- 잔차 시그니처 해석 + variable candidate list 생성 (변수 *값*은 수정 ✗)
			- candidate list는 Step 0 22개 어휘 내로 한정 (신규 변수 정의 ✗)

	2. **Orchestrator (Phase 1) agent**
		- **역할**: diagnostic의 variable candidate list로부터 라운드별 variable subset 분할 + specialist 인스턴스 호출·할당
		- **입력**
			- diagnostic의 잔차 시그니처(전력·가스·교차) + variable candidate list
			- Stage 1 변수 status (prior 정보) + Stage 2 누적 freeze 목록 (hard 제외)
			- §4.4 initial routing prior (물리 직관 기반)
		- **출력**
			- specialist 인스턴스별 variable subset 할당 목록
			- specialist 호출 명령 (할당 subset + 라운드 컨텍스트)
		- **책임 원칙**
			- candidate list 분할·specialist 호출만 수행 (변수 *값*은 수정 ✗)
			- 출력은 schema validation을 통과해야 함 (§4.7 Constraint Enforcement)

	3. **Specialist agents**
		- **역할**: orchestrator가 라운드별 동적으로 호출·할당하는 인스턴스. 동일 라운드에 여러 인스턴스가 *서로 다른 variable subset*을 담당하며 병렬 호출됨
		- **입력**
			- orchestrator phase 1이 할당한 variable subset
			- 라운드 컨텍스트 (잔차 시그니처, Stage 1 final 값)
		- **출력**
			- 후보안 1개 = (변수 식별자, 신규 값, 물리 매커니즘 사유) tuple list
		- **책임 원칙**
			- 할당된 variable subset 내 수정안 제안 (할당 외 변수·Stage 2 누적 freeze 변수 수정 불가; schema-validated)

	4. **Reality agent**
		- **역할**: specialist 후보안 *사후 검토*에만 호출됨 (라운드 시작 시점에는 호출되지 않음)
		- **입력**
			- 각 specialist 후보안 (변수 식별자·신규 값·물리 사유 tuple list)
		- **출력**
			- 후보안별 판정: **pass / hold / reject** + 사유 (변수값 자체는 수정 ✗)
		- **책임 원칙**
			- *Hard physics layer*: 외부 표준(ASHRAE 90.1/G14/62.1, 국토교통부 건축물 에너지절약설계기준 등) 및 building physics 기본 원리 위반 시 binary reject
			- *Soft plausibility layer*: 표준 범위 내의 *결합 모순*(예: 외피 매우 우수 + 침기율 매우 높음)에 대해 hold/pass 의견 출력
			- 변수 값 자체는 수정 ✗ — 판정·사유 출력에 한정

	5. **Orchestrator (Phase 2) agent**
		- **역할**: specialist 후보안 + reality 판정으로부터 채택 / hybrid / 기각 결정 + Stage 2 freeze 갱신 (변수 값 수정 권한 없음)
		- **입력**
			- specialist 후보안 (변수 식별자·신규 값·물리 사유)
			- reality 판정 결과 (pass/hold/reject + 사유)
			- 후보안 적용 후의 전역 J 평가 결과
		- **출력**
			- 채택 결과 (변수 식별자·최종 채택값)
			- Stage 2 freeze 갱신 목록
			- hold 처리 변수 목록 (다음 라운드 재고)
		- **책임 원칙**
			- LLM 기반 *추론*; 정적 if-then 규칙이 아님 (단, 출력은 §4.7 schema validation으로 변수 식별자 어휘 안에서만 허용)
			- 채택 / hybrid / 기각 + freeze 갱신 (변수 *값*은 수정 ✗)

3. 라운드 프로토콜 (5-step multi-agent 흐름)
	1. **diagnostic** (단일 에이전트, 전력·가스 통합) → 잔차 시그니처 + variable candidate list 생성
	2. **orchestrator phase 1** → candidate list로부터 variable subset 분할 + specialist 인스턴스 호출·할당
	3. **specialists** (병렬) → 각 1개 후보안 생성 (할당된 subset 내에서만)
	4. **reality** → 후보안 hard physics + soft plausibility 검토 (pass / hold / reject)
	5. **orchestrator phase 2** → 채택 / hybrid / 기각 + Stage 2 freeze 갱신
	- 라운드 *시작 시점*의 reality 호출은 두지 않는다 — reality는 specialist 후보안 *사후* 검토에만 작동
	- 종료 조건은 §4.6에 본문화

4. Initial routing prior (orchestrator phase 1 참고용 사전 지식)
	- 본 절의 라우팅 매핑은 orchestrator에 *고정 if-then 규칙*으로 주어지지 않고, *물리 직관 기반 prior*로 prompt에 제공된다. orchestrator는 이를 참고하되 diagnostic의 variable candidate list와 잔차 시그니처 컨텍스트에 따라 *재해석*할 수 있다. 본 prior는 Step 0 22개 변수 list 위에서 *변수 시그니처*(name·unit·physical role)에 직접 매칭되며, 고정 taxonomy(예: 사전 6개 prior 카테고리)를 전제하지 않는다.
	- prior 예시 (변수 시그니처 기반):
		- 내부부하/운영 패턴 전력 시그니처 → LPD, EPD, occupancy density, 운영 schedule 우선 후보 subset
		- 겨울 난방 가스 시그니처 → 외피·공기 흐름 관련 변수 (Wall/Roof/Window U-value, infiltration), 난방 setpoint, HVAC/난방 효율 우선 후보 subset
		- baseload·shoulder 가스 시그니처 → DHW 관련 변수, 운영 schedule, 외피 변수 우선 후보 subset
		- 전력+가스 *교차 시그니처* → 두 modality에 동시 영향을 주는 변수 (운영 schedule, HVAC availability, 점유 density) 우선 후보 subset
		- 반복 지목 variable subset → 다음 라운드 우선순위 상승
	- 이 설계는 Sun(2022)의 *정적 pattern-rule lookup*과 다르다 — 본 framework는 prior를 LLM orchestrator의 *해석 가능한 컨텍스트*로 제공하고 routing의 최종 결정(variable subset 분할 + specialist 할당)은 LLM reasoning에 위임한다.

5. 후보안 채택 규칙 (orchestrator phase 2)
	- 고려 요소: 전역 J 개선, 전력·가스 잔차 시그니처 변화, reality 의견 (pass / hold / reject)
	- 채택 형태
		- 단일 specialist 후보안 우세 → 그대로 채택
		- 복수 후보안이 *비충돌·상보적*(서로 다른 variable subset에 대한 수정안)인 경우 한정 hybrid 허용
		- reality reject 후보안 → 자동 기각
		- reality hold + J 개선 미미 → 다음 라운드 재고
	- **Stage 2 freeze 갱신**: per-variable 상대 변동 `< θ_freeze`가 2 라운드 연속 충족 시 freeze (`θ_freeze`는 Stage 1과 동일 임계값 사용). Stage 2 freeze는 *Stage 2 라운드 간*에만 누적되며, Stage 1 freeze 위에 더해지지 않는다 — Stage 1 freeze 변수가 Stage 2에서 재활성된 경우, 재활성 시점부터 새로 누적된다.

6. 종료 조건
	- **수렴 종료**: `(J_prev − J_curr) / J_prev < θ_J` 가 2 라운드 연속 (`θ_J = 1%`, Stage 1과 동일)
	- **Freeze 종료**: 22개 pool의 모든 변수가 Stage 2 freeze에 도달 시 자동 종료
	- **Hard cap**: Stage 2 라운드 수 상한 도달 시 강제 종료 (안전장치)
	- **ASHRAE G14 조기 종료**: monthly CVRMSE ≤ 15%, |NMBE| ≤ 5%가 전력·가스 모두에서 충족 시 조기 종료
	- *임계값 case-independence 주장은 Stage 1과 동일하게 §Discussion #1에서 robustness로 검증*

7. Constraint Enforcement (Stage 2가 자유 생성형이 *아닌* 메커니즘)
	1. **Domain restriction**:
		- 각 specialist 인스턴스의 출력은 *orchestrator phase 1이 해당 라운드에 할당한 variable subset* 외부를 수정할 수 없다 (schema validation으로 강제)
		- Step 0 22개 변수 어휘 외 변수 신설·정의 변경 불가
		- Stage 2 누적 freeze 변수 수정 불가 (Stage 1 freeze는 prior이며 hard 제약 아님 — §4.1 참조)
	2. **Hard physics constraint**: Reality agent의 hard layer가 외부 표준(ASHRAE 90.1/G14/62.1, 국토교통부 건축물 에너지절약설계기준 등) 및 building physics 기본 원리에서 도출된 binary reject 규칙을 적용. 위반 시 자동 reject (orchestrator phase 2 입력 단계에서 reject 후보안은 채택 후보에서 제외)
	3. **Soft plausibility check**: Reality agent의 soft layer(LLM)가 표준 범위 내의 *결합 모순*에 대해 hold/pass 의견을 출력
	4. **Adoption rule**: Orchestrator phase 2는 §4.5의 채택 규칙(단일 우세 / 비충돌 hybrid / 기각)만 허용하며, 임의 합성·자유 생성 채택을 금지
	5. **Audit log**: 5-step 라운드의 모든 단계(diagnostic 출력, orchestrator phase 1 routing 결정, specialist 후보안, reality 판정, orchestrator phase 2 채택·freeze)는 *변수 identifier 어휘*(Step 0 변수 list의 정규화 변수명)로 로깅된다. 이로써 §Framework Overview의 *structural reproducibility*가 운영적으로 보장된다.

### 5. Case Study Buildings — 두 채의 실증 건물

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

## Results

### 1. 실험 조건

- 세 가지 구성 비교
	- Baseline-only (Step 0 OSM, 보정 없음)
	- Stage 1 only (Step 0 + 반복형 블록 단위 최적화)
	- Stage 1 + Stage 2 (전체 프레임워크)
- 평가 지표
	- 월별 전력/가스 CVRMSE, NMBE
	- ASHRAE Guideline 14 임계값 충족 여부
	- 진단 보조: 겨울 가스 bias, shoulder 가스 bias, 여름 전력 bias
- 비교군 (§Related Works와 정렬)
	- 단일 패스 GA 형태 최적화 (최적화-only 대표)
	- 정적/동적 2단계 보정 (Liang et al., 2025 형태)
	- 패턴 기반 규칙 적용 (Sun et al., 2022 형태)

### 2. Step 0 Outcomes — Literature-grounded 변수 채택 결과

> -> C1 (Literature-grounded variable definition) 제시 지점

1. Building A
	- Baseline OSM 요약
	- Literature variable adoption table (RW §2.1 -> 채택 변수 -> 단위·literature range·출처 매핑)
	- 변수 list 메타데이터 (총 변수 수, 매커니즘별 분포 통계 — taxonomy가 아닌 *describe-only* 통계)
2. Building B (동일 구조)
3. Cross-case 관찰
	- 두 건물에서 *공유된* 변수 list (literature 채택의 case-independence)
	- 두 건물 차이가 변수별 search space 폭과 우선순위에 어떻게 반영되는지

### 3. Step 1 Outcomes — 반복형 변수 단위 동시 최적화

> -> C2 (iterative joint optimization) 검증 지점

1. Round 0 SA screening 결과
	- 두 건물의 SA 결과 (Spearman 또는 Morris μ*) ranking
	- screening 후 active 변수 집합 / baseline freeze 변수 집합 보고
2. 라운드별 J 수렴
	- 두 건물의 라운드별 J 그래프
3. 변수별 J 감소 기여도
	- 어떤 변수가 가장 큰 개선을 가져왔는지 (라운드별 trial 기여도 분석)
	- 두 건물 간 기여도 패턴 차이
4. Freeze 결정 추적
	- 라운드별 per-variable freeze 발생 시점
	- Search space (α) 축소 추이
	- Envelope hybrid clamp 변수의 literature 경계 도달 빈도
5. Stage 1 종료 시점의 잔차 패턴
	- 월별 / 계절별 잔차 (두 건물)
	- Stage 2가 다뤄야 할 *잔차 시그니처* 정리

### 4. Step 2 Outcomes — 진단 기반 specialist 정제

> -> C3 (구조화된 specialist 정제) 검증 지점 — Stage 2가 자유 생성에 흐르지 않고 *할당된 variable subset*·진단·reality 제약 하에서 결정한다는 운영 증거를 제시

1. Routing trace (라운드별)
	- 전력·가스 진단 결과 -> orchestrator의 variable subset 분할·specialist 인스턴스 할당 -> 호출된 specialist -> 채택안
	- 두 건물의 routing trace 표 (또는 sankey-style 시각화) — 변수 식별자 기반 표기
2. Specialist 인스턴스 호출 통계
	- 어느 variable subset이 어떤 잔차 시그니처에서 호출되었는지 / 채택률 / hybrid 비율
3. Reality agent 개입 사례
	- pass / hold / reject 분포
	- reject 또는 hold가 발생한 후보안의 물리적 원인 해석
4. 최종 calibrated model 성능
	- 월별 전력/가스 CVRMSE, NMBE (두 건물)
	- ASHRAE G14 임계값 충족 여부

### 5. Stage Ablation — 단계별 기여도

1. 정확도 변화 표
	- Baseline / Stage 1 / Stage 1+2 × 두 건물 × 전력/가스
2. 오차 축별 기여도
	- 연간 / 월별 / 계절 bias 중 어느 축에서 Stage 2가 가장 크게 기여했는지
3. Stage 2 추가의 *설명 가능성*
	- Stage 1만으로 못 잡은 잔차가 Stage 2의 어떤 routing으로 보완되었는지 사례 1~2개

### 6. Cross-case Application Analysis

> -> C-Validation (두 contrasting case에서의 *literature-grounded backbone + 사례 의존적 수동 비용 부재* 검증) 지점
> 주의: 본 절은 transferability를 *통계적으로 일반화*하지 않는다. *재설계 부재*(literature-grounded backbone의 조작적 정의)와 두 사례에서의 *적용성*을 시연한다.

1. 재설계 여부 점검
	- 동일 변수 list / 에이전트 토폴로지가 두 건물에 *수동 재설계 없이* 적용되었는가
	- 차이가 케이스 특수 search space 폭과 라운드별 variable subset 할당 패턴에만 한정되는지
2. 라우팅 패턴의 cross-case 비교
	- 같은 잔차 시그니처에 대해 두 건물에서 동일·유사 variable subset이 호출되는 경향이 있는지
3. 두 사례에서의 적용성에 대한 정량 / 정성 평가
	- 정량: 두 건물 모두에서 ASHRAE G14 충족
	- 정성: routing trace의 일관성, freeze 패턴의 일관성

---

## Discussion

### 1. Sensitivity / Robustness — Stage 1 임계값

> 본 절은 §Methodology Step 1 §7 Inter-round Orchestration Protocol의 임계값이 *case-independent*하게 재사용 가능하다는 주장의 검증 지점이다. 임계값을 권장 값에서 ±50% 흔들었을 때 Stage 1 결과의 robustness를 보고한다.

1. `θ_J` (라운드 수렴 종료): 0.5% / 1% / 1.5% 조건에서 라운드 수, 최종 J, freeze 변수 집합 변화
2. `θ_freeze` (변수 freeze): 2.5% / 5% / 7.5% 조건에서 freeze 시점·변수 수·최종 J 변화
3. `ρ` (search space 축소율): 0.5 / 0.7 / 0.9 조건에서 수렴 속도·최종 J 변화
4. `R_max` (hard cap): 권장 값에서 도달했는지 여부 보고 (보통은 수렴 종료가 먼저 작동)
5. **Round 0 SA screening robustness**: SA threshold (Spearman/Morris cutoff) ±50% 흔들었을 때 active 변수 집합·최종 J가 임계 내에서 동일한지. SA screening 미적용(전 변수 active) 대비 비교
6. **α 초기값 robustness**: 변수 유형별 α 초기값을 ±50% 흔들었을 때 라운드 수·최종 J 변화 — 본 round의 *임의 설정* α를 사후 implicit 정당화하는 주된 근거

### 2. 가중치 w1~w6 sensitivity
- w1·w2를 ±50% 흔들 때 variable group 또는 변수별 ranking의 보존 여부 (`추가할것.md` #6 권장)

### 3. Limitations
- n=2 건물의 한계: *통계적 일반화*가 아닌 *structural reusability* 시연
- Literature aggregation 결과의 case-dependence — 채택 변수가 선행 연구 풀(GA·최적화 중심)에 편향될 가능성 / 다른 방법론 계열(Bayesian, pattern-based)의 변수가 누락될 위험
- LLM 비결정성의 영향 범위는 §1·§Framework Overview의 *structural reproducibility*로 한정

### 4. Threats to Validity
- LLM 출력 변동: 본 framework 재현성은 *변수 list + 에이전트 토폴로지 + 제약 메커니즘 level*임을 명시
- Weather file 불확실성 (측정 vs. TMY)
- 비교 실험 fairness: 비교군에 줄 변수·범위 정의 protocol (각자 원 논문 셋업) 명시

### 5. Failure mode
- Reality agent가 모든 후보안을 reject한 경우의 처리
- Stage 1에서 J 발산 시 (best-so-far 유지 규칙)
- Stage 2 LLM 출력 schema 위반 시

---

## Conclusion

(추후 채움)
