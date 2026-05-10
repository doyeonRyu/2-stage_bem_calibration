# Code 구성 및 작동 순서

> 대응 문서: `drafts/3_method_v2.md`
> 작성: 2026-05-03
> 갱신: 2026-05-04 (Step 0 + Step 1 파이프라인 검증 완료)

---

## 0. 현재 상태 요약

### 0.1. 완료
- ✅ Step 0 — baseline OSM 구축 + variable list 확정
- ✅ Step 1 코드 구현 — 6개 모듈 + orchestrator
- ✅ Step 1 파이프라인 스모크 검증 — apply → simulate → score → J 정상 산출
- ✅ Cleanroom-class 보호 적용 — baseline deadband < 1.5°C zone offset 제외
- ✅ 환경 우회 — openstudio Python의 E: 드라이브 read/write 불가 → C: 경유

### 0.2. 진행 가능
- ▶ Step 1 본 실행 (n_trial=10, r_max=3~7, ~3~6시간)

### 0.3. 미착수
- ⬜ Step 2 — multi-agent refinement
- ⬜ Step 3 — cross-case validation (Building B)

### 0.4. 1차 스모크 검증 결과 (2026-05-04)
- run: `KETI_jb_phase1_20260503_2342`
- trial 0 J = 19.61, trial 1 J = 19.90 (smoke r_max=1, n_trial=2)
- trial 평균 wall-clock ≈ 5.4분
- 메트릭 분포: CVRMSE_elec 11% (G14 통과), CVRMSE_gas 84% (cal 핵심 과제), NMBE_elec 9%, NMBE_gas 57%
- 현재 best 가중 J 기여: 가스 86%, 전력 14% — Step 1에서 가스 cal lever 핵심

---

## 1. 코드 모듈 구성 (`materials/code/`)

| 모듈 | 역할 | 대응 단계 | 상태 |
|---|---|---|---|
| `base-osm-model_calibration.py` | Revit→gbXML→SketchUp→OSM baseline 모델 구축 | Step 0 | ✅ 검증 |
| `osm_calibration_params.py` | baseline OSM에서 캘리브레이션 변수 추출 (JSON 저장) | Step 0 | ✅ 검증 |
| `optuna_search_space.py` | Optuna 변수 22개 정의 + 카테고리 블록 + helper | Step 0/1 공유 | ✅ 검증 |
| `apply_calibrated_vars.py` | optuna 변수 적용 (dict / OSM 쓰기) + cleanroom 보호 | Step 1 | ✅ 검증 |
| `simulation.py` | OpenStudio CLI 기반 E+ 실행 + SQL 추출 | Step 1 | ✅ 검증 |
| `score.py` | 월별 sim vs 실측 → CVRMSE/NMBE/J 산출 | Step 1 | ✅ 검증 |
| `optuna_search.py` | 라운드 반복 orchestrator (Step 1 entry point) | Step 1 | ✅ 검증 |
| `_test_extract.py` | extract→apply→write 스모크 테스트 | 검증 | ✅ |

---

## 2. Step 0 — Pre-calibration Baseline (단발 실행, 완료)

### 2.1. baseline OSM 구축
- 실행: `base-osm-model_calibration.py`
- 입력: 기초 OSM (Revit→gbXML→SketchUp 산출)
- 출력: `osm/baseline_osm_<datetime>.osm` 및 OneDrive 운영본
- 현재 사용본: `baseline_osm_20260503_2213.osm` (4,669,387 bytes)

### 2.2. baseline 변수 추출
- 실행: `osm_calibration_params.extract_baseline_params(osm_path)` → `save_params(...)`
- 입력: baseline OSM
- 출력: `materials/building_params/<case>_params.json`
- 구조: `{metadata, candidates{12 카테고리}, context{zone/spacetype/schedule}}`
- 현재 산출: `KETI_jb_params.json`

### 2.3. variable list 확정
- 정의 파일: `optuna_search_space.py::OPTUNA_SEARCH_SPACE` (22개)
- 1차 운영 active 7개: `enabled=True` 표기 (`drafts/3_method_v2.md` §2 표 동기화)
  - 내부부하: equipment / lighting / occupancy_density
  - 운영 setpoint: heating / cooling
  - 가스 cal lever: infiltration / hvac_availability_shift
- 카테고리 블록: `CATEGORY_BLOCKS` (6 블록; block-wise iteration은 1차 보류)

---

## 3. Step 1 — Iterative Joint Optimization (라운드 반복 실행)

### 3.1. 입력 자산
- baseline OSM (Step 0.1 산출, C:\OneDrive 경로)
- baseline params JSON (Step 0.2 산출, E:\materials\building_params)
- EPW (`raw/...epw`, C:\OneDrive 경로 — drive 정합성 위해)
- 실측 CSV (`materials/measured/{electricity,LNG}_monthly.csv`)

### 3.2. Top-level orchestrator
- 실행: `optuna_search.run_phase1(args)`
- 라운드 루프 종료 조건: 수렴(θ_J=1% 2회 연속) / 전 변수 freeze / R_max=7

### 3.3. 라운드 1 흐름
- search space 빌드: literature range 그대로 (`build_round_search_space`)
- Optuna study 생성 (per-round; sqlite3 storage 공통 DB)
- N trial 실행 (`run_round`)
- 라운드 요약 저장 (`round_summary.json`)
- freeze/alpha 갱신 → 종료 검사

### 3.4. 라운드 2+ 흐름
- search space 축소: `clamp(best ± alpha)` 안에서 (alpha = literature_half × ρ^(R−1))
- warm start: 직전 best을 trial 0으로 enqueue
- 그 외 동일

### 3.5. Per-trial 흐름 (objective callback)
- 변수 sampling: active 변수만 trial.suggest, 나머지는 frozen 또는 neutral
- 변수 결합: `neutral_values | frozen_vars | sampled`
- dict 적용: `apply_calibrated_vars.apply_optuna_vars(baseline_dict, vars)`
  - **cleanroom 보호**: baseline deadband < 1.5°C zone은 thermostat offset 제외, `skip_reason` 기록
- OSM 적용: `apply_calibrated_vars.write_applied_to_osm(applied, baseline_osm, trial_osm)`
  - **cleanroom 보호**: thermostat의 (clg min − htg max) < 1.5°C이면 해당 thermostat 스케줄 modify 제외
- 시뮬레이션: `simulation.simulate_and_extract(trial_osm, epw, trial_dir)`
  - 내부: `run_simulation` (OpenStudio CLI subprocess) + `extract_monthly_results` (sqlite3)
- 점수: `score.compute_score(sim_results, measured_elec, measured_gas)`
- 산출물 저장: `case.json`, `score.json`
- 반환값: J (실패 시 `FAILURE_J=1e6`)

### 3.6. 실패 처리
- Stage 태깅: `apply` / `simulate` / `score`
- 실패 시 `_save_failed_trial`이 case/score JSON 자리표시자 + traceback 작성
- J=1e6 부여 → Optuna가 회피 학습

### 3.7. 임계값 (paper §3.7 protocol; 1차 운영 동일)
- 라운드당 trial 수: `n_trial=10`
- Hard cap: `R_max=7`
- Search space 축소율: `ρ=0.7`
- 수렴 종료: `θ_J=1%` 2 라운드 연속
- 변수 freeze: `θ_freeze=5%` (multiplier; offset/shift는 절대값 0.1/1)
- Cleanroom 보호 임계: `DEADBAND_PROTECTION_MIN=1.5°C`

### 3.8. 실측 wall-clock (스모크 기준)
- 1 trial ≈ 5.4분 (E+ annual sim)
- 1 round (10 trial) ≈ 54분
- 본 실행 예상 (3~5 라운드 수렴 시): **3~4.5시간**

---

## 4. 출력 구조

### 4.1. 환경 제약
- openstudio Python이 E: 드라이브 read/write 불가 (KETI 환경 특이)
- 우회: openstudio 거치는 자산은 C:, 외 자산은 E: 유지

### 4.2. trial 산출물 (heavy; C: 비-OneDrive)
- 위치: `C:\Users\ryudo\optuna_trials\<run_name>\round_R\trial_NNN\`
- 구성: `case.json`, `score.json`, `trial.osm`, `workflow.osw`, `run/{eplusout.sql, .err, ...}`
- 보관: 1차 연구 단계 전부 유지

### 4.3. Optuna study (가벼움; E: repo)
- 위치: `materials/optuna/studies/<run_name>.db` (sqlite, Python sqlite3 모듈)
- 라운드별 sub-study: `<run_name>__round_R`

### 4.4. summary (가벼움; E: repo)
- 라운드 요약: `<trials_root>/<run_name>/round_R/round_summary.json`
- 최종 요약: `materials/optuna/summaries/<run_name>_summary.json`
- 구성: 입력 자산 경로, 임계값, J_history, frozen_vars, current_best, 라운드별 trial 기록

### 4.5. baseline 자산
- baseline OSM 운영본: `C:\OneDrive\...\osm\baseline_osm_<datetime>.osm` (openstudio E: 읽기 불가 우회)
- baseline OSM 사본: `osm/baseline_osm_<datetime>.osm` (E: repo, 참조용; openstudio 직접 사용 X)
- baseline params JSON: `materials/building_params/<case>_params.json`
- EPW: `C:\OneDrive\...\.epw` (drive 정합성 위해)

---

## 5. 모듈 의존성

```
optuna_search.py
  ├── osm_calibration_params (load_params)
  ├── optuna_search_space (OPTUNA_SEARCH_SPACE, get_enabled_vars, neutral_values)
  ├── apply_calibrated_vars (apply_optuna_vars, write_applied_to_osm)
  ├── simulation (simulate_and_extract)
  ├── score (compute_score)
  └── optuna (TPE sampler, sqlite storage)

apply_calibrated_vars.py
  ├── optuna_search_space (neutral_values)
  ├── osm_calibration_params (_load_model, _name_of, _opt_get, _opt_value)
  └── openstudio

simulation.py
  ├── openstudio (model load/save, OutputMeter, VersionTranslator)
  ├── subprocess (openstudio CLI)
  └── sqlite3 (eplusout.sql 파싱)

score.py
  └── simulation (extract_monthly_results; CLI 옵션)
```

---

## 6. Step 2 — Specialist Multi-agent (예정, 미착수)

### 6.1. 입력
- Step 1 final summary (calibrated OSM + 변수별 final값 + freeze list + 잔차 패턴)
- variable list (Step 0 공유)

### 6.2. agent 구조 (`materials/code/agents/` 예정)
- diagnostic: 전력·가스·교차 시그니처 해석
- orchestrator phase 1: variable subset 분할 + specialist 호출
- specialists: 카테고리별 후보안 생성
- reality: hard physics + soft plausibility 검토
- orchestrator phase 2: 채택 / hybrid / freeze

### 6.3. 출력 구조
- `materials/multi-agent/outputs/<run>/round_R/{routing.json, candidates.json, adopted.json}`

---

## 7. CLI 실행 명령

### 7.1. 스모크 테스트 (검증 완료)
- `python materials/code/optuna_search.py --smoke`
- r_max=1, n_trial=2, 파이프라인 검증 (≈11분)

### 7.2. 본 실행
- `python materials/code/optuna_search.py`
- defaults: study=KETI_jb_phase1, n_trial=10, r_max=7
- 예상: 3~4.5시간 (3~5 라운드 수렴)

### 7.3. 단독 점수 산출
- `python materials/code/score.py --simulation-dir <trial_or_run_dir>`
- run dir / trial dir / SQL 파일 경로 모두 자동 감지

### 7.4. 단독 시뮬레이션
- `python materials/code/simulation.py --osm <osm_path>`
- 출력 dir: `<DEFAULT_OUTPUT_ROOT>/<osm_stem>/`

### 7.5. baseline params 추출
- `python -c "from osm_calibration_params import extract_baseline_params, save_params; save_params(extract_baseline_params(r'<osm>'), r'<json>')"`
