---
description: Step 2 routing phase — orchestrator-router-agent 호출, 결과를 라운드 MD에 append
argument-hint: <model_name> [N]
---

# /route <model_name> [N]

## 인수
- `model_name` (필수)
- `N` (선택) — 생략 시 MD의 현재 진행 라운드(가장 최근 `## Round K`).

## 경로
- MD 로그: `materials/multi-agent/step2_<model_name>.md`

## 전제
- 해당 라운드의 `### Diagnostic` 섹션이 이미 채워져 있어야 함.

## 실행

1. MD에서 `## Round {N}` → `### Diagnostic` 블록 추출 (전력·가스 시그니처·교차·통합 candidate list·신뢰도).
2. 현재 base parameters(22변수 + status) 산출:
   - Round 1: `materials/optuna/trials/optuna_best/trial_000/optuna_best.json`
   - Round N≥2: MD의 `## Round {N-1}` → `### Adopt` 채택값.
3. Stage 2 누적 frozen 목록을 MD에서 추출.
4. **`orchestrator-router-agent` 단일 호출** — 위 입력 전달. 매핑·prior·출력 스키마는 agent 정의가 책임.
5. agent 출력을 그대로 `## Round {N}` 아래에 `### Route` 섹션으로 Python append.
6. 다음 단계 안내: `/propose <model_name> {N}`
