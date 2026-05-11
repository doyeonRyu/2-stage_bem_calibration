---
description: Step 2 reality phase — reality-agent를 호출해 specialist 후보안의 물리·운영 타당성 검토, 결과를 라운드 MD에 append
argument-hint: <model_name> [N]
---

# /reality <model_name> [N]

## 인수
- `model_name` (필수)
- `N` (선택) — 생략 시 MD의 현재 진행 라운드.

## 경로
- MD 로그: `materials/multi-agent/step2_<model_name>.md`

## 전제
- 해당 라운드 `### Propose` 섹션이 채워져 있어야 함 (specialist 통합 후보안 표).

## 실행

1. MD에서 `## Round {N}` → `### Propose`의 통합 후보안 표 추출 (변수·현재값·제안값·변동율·물리 사유·specialist).
2. `### Diagnostic` 시그니처도 함께 참조 컨텍스트로 전달 (잔차 방향과 후보안 일관성 확인용).
3. 건물 특성(`materials/optuna/trials/optuna_best/trial_000/optuna_best.json`의 space type·HVAC topology) 발췌.
4. **`reality-agent` 단일 호출** — Agent 도구. 절대 범위·결합 모순·외부 표준 위반은 agent 정의가 책임.
5. agent 출력을 그대로 `## Round {N}` 아래에 `### Reality` 섹션으로 Python append.
   - 형식: 후보안별 `pass / hold / reject + 사유` 표 + 결합 모순 경고 블록(있을 경우).
6. 다음 단계 안내:
   ```
   다음: EnergyPlus 시뮬레이션 실행 (채택 조합 적용 OSM → materials/multi-agent/outputs/round_{N}/score.json)
   그 후: /adopt <model_name> {N}
   ```
