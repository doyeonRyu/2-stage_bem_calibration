---
description: Step 2 propose phase — /route가 지정한 specialist들을 병렬 호출, 후보안을 라운드 MD에 append
argument-hint: <model_name> [N]
---

# /propose <model_name> [N]

## 인수
- `model_name` (필수)
- `N` (선택) — 생략 시 MD의 현재 진행 라운드.

## 경로
- MD 로그: `materials/multi-agent/step2_<model_name>.md`

## 전제
- 해당 라운드 `### Route` 섹션이 채워져 있어야 함 (Specialist 호출 계획 표).

## 실행

1. MD에서 `## Round {N}` → `### Route` → "Specialist 호출 계획" 표 추출. 각 행: `(specialist, 할당 subset, 조정 방향 힌트, 호출 사유)`.
2. 현재 base parameters(22변수) 산출:
   - Round 1: `materials/optuna/trials/optuna_best/trial_000/optuna_best.json`
   - Round N≥2: 직전 `### Adopt` 채택값.
3. Stage 2 누적 frozen 목록을 MD에서 추출.
4. **호출 계획에 명시된 specialist들을 단일 메시지에서 병렬 호출** — Agent 도구 다중 콜.
   - 각 specialist에 전달: 할당 subset(변수+현재값), 방향 힌트, 호출 사유, diagnostic 시그니처 발췌, building meta(`optuna_best.json`의 해당 변수 targets), frozen 목록.
   - 출력 스키마·제약은 specialist agent 정의가 책임.
5. 모든 specialist 출력을 모아 `## Round {N}` 아래에 `### Propose` 섹션으로 Python append.
   - 형식: specialist별 sub-block + 통합 후보안 표 `(변수, 현재값, 제안값, 변동율, 물리 사유, 출처 specialist)`.
6. 다음 단계 안내: `/reality <model_name> {N}`
