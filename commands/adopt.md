---
description: Step 2 adopt phase — 시뮬레이션 결과 + 후보안 + reality 종합해 orchestrator-adopter-agent 호출, 채택·freeze·평가를 라운드 MD에 append
argument-hint: <model_name> [N]
---

# /adopt <model_name> [N]

## 인수
- `model_name` (필수)
- `N` (선택) — 생략 시 MD의 현재 진행 라운드.

## 경로
- MD 로그: `materials/multi-agent/step2_<model_name>.md`
- 라운드 N 시뮬 결과: `materials/multi-agent/outputs/round_{N}/score.json`
- 라운드 N 갱신 OSM: `materials/multi-agent/osm/step2_round{N}.osm`

## 전제
- 해당 라운드 `### Propose`, `### Reality` 섹션이 모두 채워져 있어야 함.
- EnergyPlus 시뮬레이션이 완료돼 `outputs/round_{N}/score.json`이 존재해야 함.

## 실행

1. MD에서 `## Round {N}` → `### Propose` 통합 후보안 표, `### Reality` 판정 표, `### Diagnostic` 시그니처 추출.
2. 시뮬 결과 로드 — `outputs/round_{N}/score.json` (이전 라운드 score.json과 동일 스키마: metrics, J, ashrae_g14, residuals, monthly).
3. J 비교: J_prev (직전 라운드 또는 Stage 1 best) → J_curr.
4. Stage 2 누적 frozen 목록 + 직전 라운드 채택값을 MD에서 추출.
5. **`orchestrator-adopter-agent` 단일 호출** — Agent 도구. 채택 규칙·freeze 기준(per-variable 변동율<θ_freeze, 2라운드 연속)·종료 조건(ASHRAE G14, 수렴 θ_J=1%, hard cap)은 agent 정의가 책임.
6. agent 출력을 그대로 `## Round {N}` 아래에 다음 두 섹션으로 Python append:
   - `### Adopt` — 채택 변수값 표 + freeze 갱신 목록 + hold 처리 목록 + 근거 요약.
   - `### Evaluation` — J_prev → J_curr 비교, 월별 CVRMSE/NMBE 표, ASHRAE G14 달성 여부, 종료 조건 충족 여부.
7. 다음 단계 안내:
   - 종료 조건 미충족: `/diagnostic <osm_path> <model_name> {N+1}`
   - 종료 조건 충족: Step 2 완료. 최종 OSM·MD 보존 위치 안내.
