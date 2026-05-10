"""
File: optuna_search_space.py

> Date: 2026-05-10
> Author: 유도연

======================================================================
Purpose:
Optuna calibration 변수의 범위, 자료형, 활성 상태를 정의한다.

======================================================================
Description:
총 22개 calibration 후보를 flat Optuna 변수 구조로 정리하고, 카테고리 블록과 활성 변수 집합,
neutral 값, helper API를 제공한다. Stage 1 search space의 기준 정의 파일이다.

Input:
- calibration 후보 변수 설계 기준
- literature 기반 탐색 범위

Output:
- `OPTUNA_SEARCH_SPACE`
- 카테고리 블록 정의
- 활성 변수 목록
- neutral 기본값 dict

======================================================================
Note:
현재 1차 KETI 실험에서는 22개 중 7개만 `enabled=True`로 활성화되어 있다.

======================================================================
Run:
python materials/code/optuna_search_space.py

"""

from __future__ import annotations

from typing import Literal, TypedDict


VarType = Literal["float", "int"]


class SearchSpaceEntry(TypedDict, total=False):
    low:         float
    high:        float
    type:        VarType
    step:        float
    log:         bool
    enabled:     bool
    description: str
    applies_to:  str
    citation:    list[str]


# ---------------------------------------------------------------------------
# Optuna 변수 22개 (모두 building-agnostic 전역 적용)
#   - applies_to: extract_baseline_params() 결과 dict 내 적용 위치 (apply.py 참고)
#   - enabled=False는 추출은 되지만 search space에서 제외 (1차 실험 freeze + 식별성 안전장치)
#   - 1차 실험 active 7개: equipment, lighting, occupancy_density,
#                          heating_setpoint, cooling_setpoint,
#                          infiltration, hvac_availability_shift
#   - citation은 TODO 상태로 두고, 검토 후 보강
# ---------------------------------------------------------------------------
OPTUNA_SEARCH_SPACE: dict[str, SearchSpaceEntry] = {
    # ====================================================================
    # Block 1: Internal Loads (3 vars)
    # ====================================================================
    "equipment_multiplier": {
        "low": 0.7, "high": 1.7, "type": "float", "enabled": True,
        "description": "전 zone 장비밀도(EPD) 배율",
        "applies_to":  "candidates.equipment_multiplier.targets[*].baseline_value",
        "citation":    [],  # TODO: Baba'22, Liang'25, Lyu'21
    },
    "lighting_multiplier": {
        "low": 0.5, "high": 1.5, "type": "float", "enabled": True,
        "description": "조명밀도(LPD) 전역 배율",
        "applies_to":  "candidates.lighting_multiplier.targets[*].baseline_value",
        "citation":    [],  # TODO: Baba'22, Liang'25, Jiang'24
    },
    "occupancy_density_multiplier": {
        "low": 0.5, "high": 1.7, "type": "float", "enabled": True,
        "description": "재실 인원밀도(persons/m²) 전역 배율",
        "applies_to":  "candidates.occupancy_density_multiplier.targets[*].baseline_value",
        "citation":    [],  # TODO: Baba'22 (count), Liang'25 (W/m²)
    },

    # ====================================================================
    # Block 2: Schedules (4 vars)
    # ====================================================================
    "occupancy_schedule_multiplier": {
        "low": 0.5, "high": 1.5, "type": "float", "enabled": True,
        "description": "재실 스케줄 fraction 전역 배율 (1.0 cap 후)",
        "applies_to":  "candidates.occupancy_schedule_multiplier.targets[*].summary",
        "citation":    [],  # TODO: Guo'21, Jiang'24, Lyu'21
    },
    "lighting_schedule_multiplier": {
        "low": 0.5, "high": 1.5, "type": "float", "enabled": False,
        "description": "조명 스케줄 fraction 전역 배율",
        "applies_to":  "candidates.lighting_schedule_multiplier.targets[*].summary",
        "citation":    [],
    },
    "equipment_schedule_multiplier": {
        "low": 0.5, "high": 1.5, "type": "float", "enabled": False,
        "description": "장비 스케줄 fraction 전역 배율",
        "applies_to":  "candidates.equipment_schedule_multiplier.targets[*].summary",
        "citation":    [],
    },
    "hvac_availability_shift": {
        "low": -2, "high": 2, "type": "int", "step": 1, "enabled": True,
        "description": "HVAC availability 스케줄 시프트 (시간 단위, +면 늦게/길게 운영)",
        "applies_to":  "candidates.hvac_availability_shift.targets[*].summary",
        "citation":    [],  # TODO: Lyu'21, Guerrero'25, Wang'24
    },

    # ====================================================================
    # Block 3: Thermostat (3 vars)
    # ====================================================================
    "heating_setpoint_offset": {
        "low": -2.0, "high": 3.0, "type": "float", "enabled": True,
        "description": "전 zone 난방 setpoint 평행이동 (°C)",
        "applies_to":  "candidates.heating_setpoint_offset.targets[*]",
        "citation":    [],  # TODO: Guo'21, Liang'25, Jiang'24
    },
    "cooling_setpoint_offset": {
        "low": -2.0, "high": 3.0, "type": "float", "enabled": True,
        "description": "전 zone 냉방 setpoint 평행이동 (°C)",
        "applies_to":  "candidates.cooling_setpoint_offset.targets[*]",
        "citation":    [],  # TODO: Guo'21, Jiang'24
    },
    "setback_delta_offset": {
        "low": -2.0, "high": 2.0, "type": "float", "enabled": True,
        "description": "occupied vs setback 간 delta 추가 조정 (°C). 양수=setback 더 멀리.",
        "applies_to":  "candidates.setback_delta_offset.targets[*]",
        "citation":    [],  # TODO: Wang'24 (unocc reset), Jiang'24
    },

    # ====================================================================
    # Block 4: Envelope & Air Exchange (6 vars)
    # ====================================================================
    "infiltration_multiplier": {
        "low": 0.5, "high": 2.0, "type": "float", "enabled": True,
        "description": "전 zone 침기율 배율",
        "applies_to":  "candidates.infiltration_multiplier.targets[*]",
        "citation":    [],  # TODO: Kounni'23, Guo'21, Baba'22, Liang'25
    },
    "wall_u_multiplier": {
        "low": 0.7, "high": 1.3, "type": "float", "enabled": False,
        "description": "외벽 U-value 배율 (insulation conductivity 조정 방식)",
        "applies_to":  "candidates.wall_u_multiplier.targets[*].baseline_value",
        "citation":    [],  # TODO: Baba'22, Liang'25, Jiang'24
    },
    "roof_u_multiplier": {
        "low": 0.7, "high": 1.3, "type": "float", "enabled": False,
        "description": "지붕 U-value 배율",
        "applies_to":  "candidates.roof_u_multiplier.targets[*].baseline_value",
        "citation":    [],  # TODO: Baba'22, Liang'25
    },
    "window_u_multiplier": {
        "low": 0.7, "high": 1.3, "type": "float", "enabled": False,
        "description": "창호 U-value 배율 (SimpleGlazing.uFactor)",
        "applies_to":  "candidates.window_u_multiplier.targets[*].baseline_value",
        "citation":    [],  # TODO: Baba'22, Liang'25
    },
    "window_shgc_multiplier": {
        "low": 0.8, "high": 1.2, "type": "float", "enabled": False,
        "description": "창호 SHGC 배율",
        "applies_to":  "candidates.window_shgc_multiplier.targets[*].baseline_value",
        "citation":    [],  # TODO: Baba'22, Jiang'24
    },
    "floor_u_multiplier": {
        "low": 0.7, "high": 1.3, "type": "float", "enabled": False,
        "description": "바닥(지면 접촉면 포함) U-value 배율 [2차 후보]",
        "applies_to":  "candidates.floor_u_multiplier.targets[*].baseline_value",
        "citation":    [],  # TODO: Liang'25
    },

    # ====================================================================
    # Block 5: HVAC & Plant (4 vars)
    # ====================================================================
    "oa_flow_multiplier": {
        "low": 0.7, "high": 1.3, "type": "float", "enabled": True,
        "description": "외기 도입 풍량(OA per area/person) 배율",
        "applies_to":  "candidates.oa_flow_multiplier.targets[*]",
        "citation":    [],  # TODO: Pachano'21, Ramos'20
    },
    "fan_power_multiplier": {
        "low": 0.7, "high": 1.3, "type": "float", "enabled": False,
        "description": "팬 전력 배율 (효율 또는 압력 손실 조정 방식)",
        "applies_to":  "candidates.fan_power_multiplier.targets[*]",
        "citation":    [],  # TODO: Pachano'21
    },
    "boiler_efficiency_multiplier": {
        "low": 0.9, "high": 1.1, "type": "float", "enabled": False,
        "description": "보일러 nominal thermal efficiency 배율",
        "applies_to":  "candidates.boiler_efficiency_multiplier.targets[*].baseline_value",
        "citation":    [],  # TODO: Pachano'21 (HVAC component eff)
    },
    "chiller_cop_multiplier": {
        "low": 0.9, "high": 1.1, "type": "float", "enabled": False,
        "description": "칠러 reference COP 배율",
        "applies_to":  "candidates.chiller_cop_multiplier.targets[*].baseline_value",
        "citation":    [],  # TODO: Pachano'21
    },

    # ====================================================================
    # Block 6: DHW & Thermal Mass (2 vars)
    # ====================================================================
    "dhw_use_multiplier": {
        "low": 0.5, "high": 1.5, "type": "float", "enabled": False,
        "description": "DHW peak flow rate 배율",
        "applies_to":  "candidates.dhw_use_multiplier.targets[*].baseline_value",
        "citation":    [],  # TODO: Pachano'21, Jiang'24
    },
    "thermal_mass_multiplier": {
        "low": 0.7, "high": 1.5, "type": "float", "enabled": False,
        "description": "Internal mass 표면적 또는 construction 열용량 배율 [2차]",
        "applies_to":  "candidates.thermal_mass_multiplier.targets[*].baseline_value",
        "citation":    [],  # TODO: Baba'22 (×2), Ramos'20 (×2)
    },
}


# ---------------------------------------------------------------------------
# Block-wise iteration 카테고리 매핑
#   - Stage 1 Optuna가 한 번에 한 블록만 흔들도록 함 (식별성 확보)
#   - Stage 2 specialist agent도 동일한 카테고리 구조 유지 (논문 novelty)
# ---------------------------------------------------------------------------
CATEGORY_BLOCKS: dict[str, list[str]] = {
    "internal_loads": [
        "equipment_multiplier",
        "lighting_multiplier",
        "occupancy_density_multiplier",
    ],
    "schedules": [
        "occupancy_schedule_multiplier",
        "lighting_schedule_multiplier",
        "equipment_schedule_multiplier",
        "hvac_availability_shift",
    ],
    "thermostat": [
        "heating_setpoint_offset",
        "cooling_setpoint_offset",
        "setback_delta_offset",
    ],
    "envelope_air": [
        "infiltration_multiplier",
        "wall_u_multiplier",
        "roof_u_multiplier",
        "window_u_multiplier",
        "window_shgc_multiplier",
        "floor_u_multiplier",
    ],
    "hvac_plant": [
        "oa_flow_multiplier",
        "fan_power_multiplier",
        "boiler_efficiency_multiplier",
        "chiller_cop_multiplier",
    ],
    "dhw_mass": [
        "dhw_use_multiplier",
        "thermal_mass_multiplier",
    ],
}


# 카테고리 ↔ Stage 2 specialist agent 매핑
CATEGORY_TO_AGENT: dict[str, str] = {
    "internal_loads": "internal-loads-agent",
    "schedules":      "schedules-operation-agent",
    "thermostat":     "thermostat-setpoints-agent",
    "envelope_air":   "envelope-air-exchange-agent",
    "hvac_plant":     "hvac-plant-efficiency-agent",
    "dhw_mass":       "dhw-agent",
}


# ---------------------------------------------------------------------------
# Helper API
# ---------------------------------------------------------------------------
def get_enabled_vars(category: str | None = None) -> dict[str, SearchSpaceEntry]:
    """활성화(enabled=True)된 변수만 반환. category 지정 시 해당 블록만."""
    if category is not None:
        names = CATEGORY_BLOCKS[category]
        return {n: OPTUNA_SEARCH_SPACE[n] for n in names if OPTUNA_SEARCH_SPACE[n].get("enabled", True)}
    return {n: e for n, e in OPTUNA_SEARCH_SPACE.items() if e.get("enabled", True)}


def suggest_optuna_trial(trial, category: str | None = None) -> dict[str, float | int]:
    """Optuna trial 객체에서 활성 변수만 sample. 다른 카테고리는 호출자가 frozen 처리."""
    sampled: dict[str, float | int] = {}
    for name, entry in get_enabled_vars(category).items():
        if entry["type"] == "float":
            sampled[name] = trial.suggest_float(
                name, entry["low"], entry["high"],
                log=entry.get("log", False),
                step=entry.get("step"),
            )
        else:
            sampled[name] = trial.suggest_int(
                name, int(entry["low"]), int(entry["high"]),
                step=int(entry.get("step", 1)),
            )
    return sampled


def neutral_values() -> dict[str, float | int]:
    """모든 변수의 무영향(no-op) 값. multiplier=1.0, offset=0.0, shift=0."""
    out = {}
    for name, entry in OPTUNA_SEARCH_SPACE.items():
        if "offset" in name or "shift" in name:
            out[name] = 0.0 if entry["type"] == "float" else 0
        else:
            out[name] = 1.0
    return out


if __name__ == "__main__":
    print(f"Total vars: {len(OPTUNA_SEARCH_SPACE)}")
    for cat, names in CATEGORY_BLOCKS.items():
        enabled = [n for n in names if OPTUNA_SEARCH_SPACE[n].get("enabled", True)]
        print(f"  {cat:18s} ({len(enabled)}/{len(names)} enabled): {', '.join(enabled)}")
