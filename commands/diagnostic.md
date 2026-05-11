---
description: Step 2 diagnostic phase — diagnostic-agent 호출, 결과를 라운드 MD에 append
argument-hint: <osm_path> <model_name> [N]
---

# /diagnostic <osm_path> <model_name> [N]

## 인수
- `osm_path` (필수)
- `model_name` (필수)
- `N` (선택) — 생략 시 MD의 마지막 `## Round K`에서 K+1, 파일 없으면 1.

## 경로
- MD 로그: `materials/multi-agent/step2_<model_name>.md`
- Round 1 컨텍스트: `materials/optuna/trials/optuna_best/trial_000/{score.json, optuna_best.json, trial.osm}`
- Round N≥2 컨텍스트: `materials/multi-agent/outputs/round_{N-1}/score.json` + MD의 직전 `### Adopt` 채택값
- 실측: `materials/measured/electricity_monthly.csv`, `materials/measured/LNG_monthly.csv`

## 실행

1. 라운드 결정 → MD 파일 초기화 또는 `## Round {N}` 헤더 append (한글 경로 안전 위해 Python).
2. 컨텍스트 로드 (위 경로).
3. **`diagnostic-agent` 단일 호출** — Agent 도구. 입력·출력 스키마·22변수 어휘·status 정의·제약은 agent 정의가 책임.
4. agent 출력을 그대로 `## Round {N}` 아래에 `### Diagnostic` 섹션으로 Python append.
5. 다음 단계 안내: `/route <model_name> {N}`
