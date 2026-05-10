# Result Draft

## 작업 상태

- 상태: draft
- 기준 문서: `plans/paper_draft.md`

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


## 4. Notes

- figure 필요 지점:
- table 필요 지점:
- 추가 실험 제안:
