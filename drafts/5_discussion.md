# Discussion

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
