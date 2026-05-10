"""
File: osm_calibration_params.py

> Date: 2026-05-10
> Author: 유도연

======================================================================
Purpose:
baseline OSM에서 calibration 대상 변수와 context 정보를 추출한다.

======================================================================
Description:
baseline OSM 파일을 읽어 Optuna calibration 대상의 baseline 값과 보조 문맥 정보를
`metadata`, `candidates`, `context` 구조로 정리한다. 결과는 JSON으로 저장되어 후속
변수 적용, Stage 1 search, Stage 2 진단 입력에 사용된다.

Input:
- baseline OSM 파일
- OpenStudio 모델 정보

Output:
- baseline params dict
- baseline params JSON
- 추출 메타데이터

======================================================================
Note:
Windows 경로와 WSL 경로를 모두 허용하도록 입력 경로를 정규화한다.

======================================================================
Run:
python materials/code/osm_calibration_params.py --help

"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import openstudio


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def extract_baseline_params(osm_path: Path | str) -> dict[str, Any]:
    """OSM 파일에서 캘리브레이션용 baseline 파라미터를 추출한다.

    Returns:
        {"metadata": {...}, "candidates": {...}, "context": {...}}
    """
    osm_path = _normalize_osm_path(osm_path)
    model = _load_model(osm_path)

    building_name = _extract_building_name(model, fallback=osm_path.stem)
    zones_ctx = _extract_zones(model)
    schedules_ctx = _extract_schedules_inv(model)

    candidate_groups = {
        "equipment":      _extract_equipment(model),
        "lighting":       _extract_lighting(model),
        "occupancy":      _extract_occupancy(model),
        "thermostat":     _extract_thermostat(model),
        "hvac_avail":     _extract_hvac_availability(model),
        "envelope":       _extract_envelope(model),
        "infiltration":   _extract_infiltration(model),
        "ventilation":    _extract_ventilation(model),
        "dhw":            _extract_dhw(model),
        "plant":          _extract_plant(model),
        "fans":           _extract_fans(model),
        "thermal_mass":   _extract_thermal_mass(model),
    }
    candidates = _build_candidate_variables(model, candidate_groups)

    context = {
        "building_name":   building_name,
        "north_axis":      model.getBuilding().northAxis(),
        "zones":           zones_ctx,
        "space_types":     _extract_space_types(model),
        "schedules_inv":   schedules_ctx,
        "constructions":   _extract_constructions_inv(model),
        "candidate_groups": candidate_groups,
    }

    metadata = {
        "building_name":   building_name,
        "source_osm":      str(osm_path),
        "extracted_at":    datetime.now().isoformat(timespec="seconds"),
        "openstudio_ver":  openstudio.openStudioVersion(),
        "n_zones":         len(zones_ctx),
        "n_space_types":   len(context["space_types"]),
        "n_spaces":        len(model.getSpaces()),
    }

    return {"metadata": metadata, "candidates": candidates, "context": context}


def save_params(params: dict[str, Any], out_path: Path | str) -> None:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(params, f, ensure_ascii=False, indent=2, default=_json_default)


def load_params(in_path: Path | str) -> dict[str, Any]:
    with Path(in_path).open("r", encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------
def _load_model(osm_path: Path) -> "openstudio.model.Model":
    if not osm_path.exists():
        raise FileNotFoundError(f"OSM not found: {osm_path}")
    loaded = openstudio.osversion.VersionTranslator().loadModel(
        openstudio.path(str(osm_path))
    )
    if not loaded.is_initialized():
        raise ValueError(f"Failed to load OSM: {osm_path}")
    return loaded.get()


def _normalize_osm_path(osm_path: Path | str) -> Path:
    """Accept either native paths or Windows-style paths when running under WSL/Linux."""
    raw = str(osm_path)
    win_drive = re.match(r"^([A-Za-z]):[\\/](.*)$", raw)
    if win_drive:
        drive = win_drive.group(1).lower()
        rest = win_drive.group(2).replace("\\", "/")
        return Path(f"/mnt/{drive}/{rest}")
    return Path(raw)


def _opt_get(optional, default=None):
    """OpenStudio Optional 패턴: is_initialized() 후 .get()"""
    if optional is None:
        return default
    if hasattr(optional, "is_initialized") and optional.is_initialized():
        return optional.get()
    return default


def _opt_value(optional, default=None):
    """Optional<double> 같이 .get()이 바로 값을 반환하는 경우용"""
    if optional is None:
        return default
    if hasattr(optional, "is_initialized"):
        return optional.get() if optional.is_initialized() else default
    return optional


def _name_of(obj, fallback: str = "<unnamed>") -> str:
    if obj is None:
        return fallback
    name_opt = obj.name() if hasattr(obj, "name") else None
    if name_opt is not None and hasattr(name_opt, "is_initialized"):
        return name_opt.get() if name_opt.is_initialized() else fallback
    if hasattr(obj, "nameString"):
        try:
            return obj.nameString()
        except Exception:
            return fallback
    return fallback


def _json_default(o: Any):
    """openstudio 객체 등 기본 JSON 변환 안 되는 값 처리."""
    try:
        return float(o)
    except Exception:
        return str(o)


# ---------------------------------------------------------------------------
# Schedule value sampling
#   - ScheduleRuleset / ScheduleConstant / ScheduleCompact 등을 통일된 형태로 요약
#   - 복잡한 스케줄은 전체 day profile 대신 (max, min, mean, samples) 정도로 축약
# ---------------------------------------------------------------------------
def _summarize_schedule(sch) -> dict[str, Any]:
    if sch is None:
        return {"type": "none"}
    name = _name_of(sch)

    # ScheduleConstant
    sc = sch.to_ScheduleConstant()
    if sc.is_initialized():
        v = sc.get().value()
        return {"type": "constant", "name": name, "value": v}

    # ScheduleRuleset
    sr = sch.to_ScheduleRuleset()
    if sr.is_initialized():
        ruleset = sr.get()
        default_day = ruleset.defaultDaySchedule()
        return {
            "type": "ruleset",
            "name": name,
            "default_day": _summarize_day_schedule(default_day),
            "rules": [
                {
                    "apply_sunday":    rule.applySunday(),
                    "apply_monday":    rule.applyMonday(),
                    "apply_saturday":  rule.applySaturday(),
                    "day_schedule":    _summarize_day_schedule(rule.daySchedule()),
                }
                for rule in ruleset.scheduleRules()
            ],
        }

    # 기타 스케줄 타입은 이름만 기록
    return {"type": "other", "name": name, "class": sch.iddObject().name()}


def _summarize_day_schedule(day_sch) -> dict[str, Any]:
    """ScheduleDay → (times[h], values) + 통계."""
    times = [t.totalHours() for t in day_sch.times()]
    values = list(day_sch.values())
    return {
        "times_h": times,
        "values": values,
        "max": max(values) if values else None,
        "min": min(values) if values else None,
        "mean": (sum(values) / len(values)) if values else None,
    }


def _build_candidate_variables(model, groups: dict[str, Any]) -> dict[str, Any]:
    """카테고리별 baseline 추출 결과를 22개 변수 중심 candidates 구조로 재조립."""
    return {
        "equipment_multiplier": {
            "apply_mode": "multiply",
            "targets": _targets_equipment(groups["equipment"]),
        },
        "lighting_multiplier": {
            "apply_mode": "multiply",
            "targets": _targets_lighting(groups["lighting"]),
        },
        "occupancy_density_multiplier": {
            "apply_mode": "multiply",
            "targets": _targets_occupancy_density(groups["occupancy"]),
        },
        "occupancy_schedule_multiplier": {
            "apply_mode": "scale_schedule",
            "targets": _targets_schedule_summaries(groups["occupancy"].get("schedules", {})),
        },
        "lighting_schedule_multiplier": {
            "apply_mode": "scale_schedule",
            "targets": _targets_object_schedules(model.getLightss(), lambda obj: _opt_get(obj.schedule())),
        },
        "equipment_schedule_multiplier": {
            "apply_mode": "scale_schedule",
            "targets": _targets_object_schedules(model.getElectricEquipments(), lambda obj: _opt_get(obj.schedule())),
        },
        "hvac_availability_shift": {
            "apply_mode": "shift_schedule",
            "targets": _targets_hvac_availability(groups["hvac_avail"]),
        },
        "heating_setpoint_offset": {
            "apply_mode": "offset",
            "targets": _targets_thermostat(groups["thermostat"], kind="heating"),
        },
        "cooling_setpoint_offset": {
            "apply_mode": "offset",
            "targets": _targets_thermostat(groups["thermostat"], kind="cooling"),
        },
        "setback_delta_offset": {
            "apply_mode": "offset",
            "targets": _targets_thermostat(groups["thermostat"], kind="setback_delta"),
        },
        "infiltration_multiplier": {
            "apply_mode": "multiply",
            "targets": _targets_infiltration(groups["infiltration"]),
        },
        "wall_u_multiplier": {
            "apply_mode": "multiply",
            "targets": _targets_envelope(groups["envelope"].get("wall", {}), "wall"),
        },
        "roof_u_multiplier": {
            "apply_mode": "multiply",
            "targets": _targets_envelope(groups["envelope"].get("roof", {}), "roof"),
        },
        "window_u_multiplier": {
            "apply_mode": "multiply",
            "targets": _targets_envelope(groups["envelope"].get("window", {}), "window_u"),
        },
        "window_shgc_multiplier": {
            "apply_mode": "multiply",
            "targets": _targets_envelope(groups["envelope"].get("window", {}), "window_shgc"),
        },
        "floor_u_multiplier": {
            "apply_mode": "multiply",
            "targets": _targets_envelope(groups["envelope"].get("floor", {}), "floor"),
        },
        "oa_flow_multiplier": {
            "apply_mode": "multiply",
            "targets": _targets_ventilation(groups["ventilation"]),
        },
        "fan_power_multiplier": {
            "apply_mode": "multiply",
            "targets": _targets_fans(groups["fans"]),
        },
        "boiler_efficiency_multiplier": {
            "apply_mode": "multiply",
            "targets": _targets_simple_list(groups["plant"].get("boilers", []), "efficiency"),
        },
        "chiller_cop_multiplier": {
            "apply_mode": "multiply",
            "targets": _targets_simple_list(groups["plant"].get("chillers", []), "cop"),
        },
        "dhw_use_multiplier": {
            "apply_mode": "multiply",
            "targets": _targets_dhw(groups["dhw"]),
        },
        "thermal_mass_multiplier": {
            "apply_mode": "multiply",
            "targets": _targets_thermal_mass(groups["thermal_mass"]),
        },
    }


def _targets_equipment(group: dict[str, Any]) -> list[dict[str, Any]]:
    targets = []
    for st_name, info in group.get("by_space_type", {}).items():
        for obj in info.get("objects", []):
            targets.append({
                "space_type": st_name,
                "object_name": obj.get("name"),
                "baseline_value": obj.get("w_m2"),
                "unit": "W/m2",
            })
    return targets


def _targets_lighting(group: dict[str, Any]) -> list[dict[str, Any]]:
    targets = []
    for st_name, info in group.get("by_space_type", {}).items():
        for obj in info.get("objects", []):
            targets.append({
                "space_type": st_name,
                "object_name": obj.get("name"),
                "baseline_value": obj.get("w_m2"),
                "unit": "W/m2",
                "schedule": obj.get("schedule"),
            })
    return targets


def _targets_occupancy_density(group: dict[str, Any]) -> list[dict[str, Any]]:
    targets = []
    for st_name, info in group.get("by_space_type", {}).items():
        for obj in info.get("objects", []):
            targets.append({
                "space_type": st_name,
                "object_name": obj.get("name"),
                "baseline_value": obj.get("people_per_m2"),
                "unit": "people/m2",
                "people_schedule": obj.get("people_schedule"),
            })
    return targets


def _targets_schedule_summaries(schedules: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {"schedule_name": name, "summary": summary}
        for name, summary in schedules.items()
    ]


def _targets_object_schedules(objects, getter) -> list[dict[str, Any]]:
    seen: set[str] = set()
    targets: list[dict[str, Any]] = []
    for obj in objects:
        sch = getter(obj)
        if sch is None:
            continue
        name = _name_of(sch)
        if name in seen:
            continue
        seen.add(name)
        targets.append({
            "schedule_name": name,
            "summary": _summarize_schedule(sch),
        })
    return targets


def _targets_hvac_availability(group: dict[str, Any]) -> list[dict[str, Any]]:
    targets = []
    for al in group.get("air_loops", []):
        targets.append({
            "object_type": "air_loop",
            "object_name": al.get("name"),
            "schedule_name": al.get("schedule"),
            "summary": al.get("summary"),
        })
    return targets


def _targets_thermostat(group: dict[str, Any], kind: str) -> list[dict[str, Any]]:
    targets = []
    for zone_name, info in group.get("by_zone", {}).items():
        entry = {
            "zone": zone_name,
            "space_type": info.get("space_type"),
            "htg_occupied": info.get("htg_occupied"),
            "htg_setback": info.get("htg_setback"),
            "clg_occupied": info.get("clg_occupied"),
            "clg_setback": info.get("clg_setback"),
        }
        if kind == "heating":
            entry["baseline_value"] = info.get("htg_occupied")
        elif kind == "cooling":
            entry["baseline_value"] = info.get("clg_occupied")
        else:
            entry["baseline_value"] = 0.0
        targets.append(entry)
    return targets


def _targets_infiltration(group: dict[str, Any]) -> list[dict[str, Any]]:
    targets = []
    for target_name, items in group.get("by_space_or_type", {}).items():
        for item in items:
            targets.append({"target_name": target_name, **item})
    return targets


def _targets_envelope(bucket: dict[str, Any], kind: str) -> list[dict[str, Any]]:
    targets = []
    for name, info in bucket.items():
        target = {"construction_name": name, **info}
        if kind == "window_shgc":
            target["baseline_value"] = info.get("shgc")
        else:
            target["baseline_value"] = info.get("u_value_w_m2k")
        targets.append(target)
    return targets


def _targets_ventilation(group: dict[str, Any]) -> list[dict[str, Any]]:
    targets = []
    for dsoa_name, info in group.get("by_dsoa", {}).items():
        targets.append({"dsoa_name": dsoa_name, **info})
    return targets


def _targets_fans(group: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {**item} for item in group.get("fans", []) + group.get("exhaust_fans", [])
    ]


def _targets_simple_list(items: list[dict[str, Any]], field: str) -> list[dict[str, Any]]:
    return [{**item, "baseline_value": item.get(field)} for item in items]


def _targets_dhw(group: dict[str, Any]) -> list[dict[str, Any]]:
    targets = []
    for defn_name, info in group.get("definitions", {}).items():
        targets.append({
            "definition_name": defn_name,
            **info,
            "baseline_value": info.get("peak_flow_m3_s"),
        })
    return targets


def _targets_thermal_mass(group: dict[str, Any]) -> list[dict[str, Any]]:
    targets = [{**item, "baseline_value": item.get("surface_area_m2")} for item in group.get("internal_masses", [])]
    for zone_name, info in group.get("by_zone_surface_capacity", {}).items():
        targets.append({
            "zone": zone_name,
            "surface_thermal_capacity_kJ_K": info.get("surface_thermal_capacity_kJ_K"),
            "baseline_value": info.get("surface_thermal_capacity_kJ_K"),
        })
    return targets


# ---------------------------------------------------------------------------
# Context extractors
# ---------------------------------------------------------------------------
def _extract_building_name(model, fallback: str) -> str:
    """OSM의 OS:Building 객체의 Name을 사용. 없거나 default("Building 1")면 fallback."""
    bldg = model.getBuilding()
    name = _name_of(bldg, fallback="").strip()
    # OpenStudio 기본 이름 패턴은 캘리브레이션 식별에 부적합 → fallback 사용
    if not name or name.lower() in ("building", "building 1") or name.startswith("Building "):
        return fallback
    return name


def _extract_zones(model) -> list[dict[str, Any]]:
    out = []
    for tz in model.getThermalZones():
        spaces = list(tz.spaces())
        floor_area = sum(s.floorArea() for s in spaces)
        volume = sum(s.volume() for s in spaces)
        space_types = {
            _name_of(_opt_get(s.spaceType()))
            for s in spaces
            if _opt_get(s.spaceType()) is not None
        }
        space_type = next(iter(space_types)) if len(space_types) == 1 else None
        is_conditioned = tz.thermostatSetpointDualSetpoint().is_initialized()
        out.append({
            "name":            _name_of(tz),
            "space_type":      space_type,
            "space_types_all": sorted(space_types),
            "n_spaces":        len(spaces),
            "floor_area_m2":   floor_area,
            "volume_m3":       volume,
            "is_conditioned":  is_conditioned,
            "spaces":          [_name_of(s) for s in spaces],
        })
    return out


def _extract_space_types(model) -> list[dict[str, Any]]:
    return [{"name": _name_of(st)} for st in model.getSpaceTypes()]


def _extract_schedules_inv(model) -> list[dict[str, Any]]:
    out = []
    for sch in model.getScheduleRulesets():
        out.append({"name": _name_of(sch), "kind": "Ruleset"})
    for sch in model.getScheduleConstants():
        out.append({"name": _name_of(sch), "kind": "Constant", "value": sch.value()})
    return out


def _extract_constructions_inv(model) -> list[dict[str, Any]]:
    out = []
    for c in model.getConstructions():
        layers = []
        for layer in c.layers():
            layers.append({
                "name":  _name_of(layer),
                "class": layer.iddObject().name(),
            })
        out.append({"name": _name_of(c), "n_layers": len(layers), "layers": layers})
    return out


# ---------------------------------------------------------------------------
# candidates: Internal Loads (equipment / lighting / occupancy)
# ---------------------------------------------------------------------------
def _extract_equipment(model) -> dict[str, Any]:
    """
    Optuna: equipment_multiplier (전 zone 일괄 적용)
    SpaceType별 baseline EPD 추출 + zone로 fan-out.
    """
    by_space_type: dict[str, dict[str, Any]] = {}
    for st in model.getSpaceTypes():
        st_name = _name_of(st)
        equip_w_m2_total = 0.0
        equip_objs = []
        for eq in st.electricEquipment():
            defn = eq.electricEquipmentDefinition()
            w_m2 = _opt_value(defn.wattsperSpaceFloorArea(), 0.0) or 0.0
            equip_w_m2_total += w_m2
            equip_objs.append({
                "name":          _name_of(eq),
                "definition":    _name_of(defn),
                "w_m2":          w_m2,
                "schedule":      _name_of(_opt_get(eq.schedule())),
            })
        by_space_type[st_name] = {
            "w_m2_total":   equip_w_m2_total,
            "objects":      equip_objs,
        }

    by_zone = {}
    for tz in model.getThermalZones():
        zname = _name_of(tz)
        st_names = sorted({
            _name_of(_opt_get(s.spaceType()))
            for s in tz.spaces()
            if _opt_get(s.spaceType()) is not None
        })
        st_name = st_names[0] if len(st_names) == 1 else None
        info = by_space_type.get(st_name, {}) if st_name else {}
        by_zone[zname] = {
            "space_type":  st_name,
            "w_m2":        info.get("w_m2_total"),
        }

    return {"by_space_type": by_space_type, "by_zone": by_zone}


def _extract_lighting(model) -> dict[str, Any]:
    """Optuna: lighting_multiplier"""
    by_space_type = {}
    for st in model.getSpaceTypes():
        st_name = _name_of(st)
        total = 0.0
        objs = []
        for lt in st.lights():
            defn = lt.lightsDefinition()
            w_m2 = _opt_value(defn.wattsperSpaceFloorArea(), 0.0) or 0.0
            total += w_m2
            objs.append({
                "name":     _name_of(lt),
                "w_m2":     w_m2,
                "schedule": _name_of(_opt_get(lt.schedule())),
            })
        by_space_type[st_name] = {"w_m2_total": total, "objects": objs}

    by_zone = {}
    for tz in model.getThermalZones():
        zname = _name_of(tz)
        st_names = sorted({
            _name_of(_opt_get(s.spaceType()))
            for s in tz.spaces()
            if _opt_get(s.spaceType()) is not None
        })
        st_name = st_names[0] if len(st_names) == 1 else None
        info = by_space_type.get(st_name, {}) if st_name else {}
        by_zone[zname] = {"space_type": st_name, "w_m2": info.get("w_m2_total")}

    return {"by_space_type": by_space_type, "by_zone": by_zone}


def _extract_occupancy(model) -> dict[str, Any]:
    """
    Optuna: occupancy_density_multiplier (1차 후보), occupancy_schedule_multiplier
    persons / m² 기준으로 추출.
    """
    by_space_type = {}
    for st in model.getSpaceTypes():
        st_name = _name_of(st)
        density_total = 0.0
        objs = []
        for ppl in st.people():
            defn = ppl.peopleDefinition()
            ppl_per_m2 = _opt_value(defn.peopleperSpaceFloorArea(), 0.0) or 0.0
            density_total += ppl_per_m2
            objs.append({
                "name":              _name_of(ppl),
                "people_per_m2":     ppl_per_m2,
                "people_schedule":   _name_of(_opt_get(ppl.numberofPeopleSchedule())),
                "activity_schedule": _name_of(_opt_get(ppl.activityLevelSchedule())),
            })
        by_space_type[st_name] = {"people_per_m2": density_total, "objects": objs}

    occ_schedules = {}
    for st in model.getSpaceTypes():
        for ppl in st.people():
            sch = _opt_get(ppl.numberofPeopleSchedule())
            if sch is not None:
                name = _name_of(sch)
                if name not in occ_schedules:
                    occ_schedules[name] = _summarize_schedule(sch)

    return {
        "by_space_type": by_space_type,
        "schedules":     occ_schedules,
    }


# ---------------------------------------------------------------------------
# candidates: Thermostat (heating/cooling setpoint, setback)
# ---------------------------------------------------------------------------
def _extract_thermostat(model) -> dict[str, Any]:
    """
    Optuna: heating_setpoint_offset, cooling_setpoint_offset, setback_delta_offset
    각 zone의 htg/clg 스케줄 + 점유/setback 값을 정리.
    """
    by_zone = {}
    sch_summary_cache: dict[str, dict[str, Any]] = {}
    for tz in model.getThermalZones():
        zname = _name_of(tz)
        tstat_opt = tz.thermostatSetpointDualSetpoint()
        if not tstat_opt.is_initialized():
            continue
        tstat = tstat_opt.get()
        clg = _opt_get(tstat.coolingSetpointTemperatureSchedule())
        htg = _opt_get(tstat.heatingSetpointTemperatureSchedule())

        st_names = sorted({
            _name_of(_opt_get(s.spaceType()))
            for s in tz.spaces()
            if _opt_get(s.spaceType()) is not None
        })
        st_name = st_names[0] if len(st_names) == 1 else None

        clg_summary = _summarize_schedule(clg) if clg else None
        htg_summary = _summarize_schedule(htg) if htg else None
        if clg_summary:
            sch_summary_cache[clg_summary.get("name", "")] = clg_summary
        if htg_summary:
            sch_summary_cache[htg_summary.get("name", "")] = htg_summary

        by_zone[zname] = {
            "space_type":     st_name,
            "clg_schedule":   _name_of(clg) if clg else None,
            "htg_schedule":   _name_of(htg) if htg else None,
            "clg_occupied":   _peak_value(clg_summary, "max"),
            "clg_setback":    _peak_value(clg_summary, "max_alt"),
            "htg_occupied":   _peak_value(htg_summary, "max"),
            "htg_setback":    _peak_value(htg_summary, "min_alt"),
        }

    return {"by_zone": by_zone, "schedules": sch_summary_cache}


def _peak_value(sch_summary: dict | None, mode: str):
    """
    스케줄 요약에서 occupied/setback 추정.
      - 냉방: occupied = max(values), setback = max(values) (값 두 개면 큰 쪽이 setback)
      - 난방: occupied = max(values), setback = min(values)
    실제로 occupied/setback 구분은 default_day의 values에서 가장 빈번한 값 vs 그 외로 함.
    여기서는 단순화하여 max/min을 반환.
    """
    if not sch_summary:
        return None
    if sch_summary.get("type") == "constant":
        return sch_summary.get("value")
    day = sch_summary.get("default_day", {})
    values = day.get("values", []) if isinstance(day, dict) else []
    if not values:
        return None
    if mode == "max":
        return max(values)
    if mode == "min_alt":
        return min(values) if len(set(values)) > 1 else None
    if mode == "max_alt":
        return max(values) if len(set(values)) > 1 else None
    return None


# ---------------------------------------------------------------------------
# candidates: HVAC Availability schedules (operation/setback timing)
# ---------------------------------------------------------------------------
def _extract_hvac_availability(model) -> dict[str, Any]:
    """
    Optuna: hvac_availability_shift (시간 단위 시프트)
    AirLoopHVAC.availabilitySchedule + Fan availability 스케줄 추출.
    """
    air_loops = []
    for al in model.getAirLoopHVACs():
        sch = al.availabilitySchedule()
        air_loops.append({
            "name":         _name_of(al),
            "schedule":     _name_of(sch),
            "summary":      _summarize_schedule(sch),
        })

    fan_avail = []
    for getter, label in [
        (model.getFanConstantVolumes, "FanConstantVolume"),
        (model.getFanVariableVolumes, "FanVariableVolume"),
        (model.getFanOnOffs,          "FanOnOff"),
        (model.getFanZoneExhausts,    "FanZoneExhaust"),
    ]:
        try:
            for fan in getter():
                sch = _opt_get(fan.availabilitySchedule())
                if sch is None:
                    continue
                fan_avail.append({
                    "fan_name":  _name_of(fan),
                    "fan_class": label,
                    "schedule":  _name_of(sch),
                })
        except Exception:
            continue

    return {"air_loops": air_loops, "fans": fan_avail}


# ---------------------------------------------------------------------------
# candidates: Envelope (wall/roof/floor U-value, window U/SHGC)
# ---------------------------------------------------------------------------
def _extract_envelope(model) -> dict[str, Any]:
    """
    Optuna: wall/roof/floor/window_u_multiplier, window_shgc_multiplier
    Surface 타입별 U-value 추출.
      - 불투명: 1 / R_total (R = sum(thickness/conductivity), Massless는 thermalResistance)
      - 창: SimpleGlazing은 uFactor/SHGC 직접, 기타는 추정 안 함
    """
    construction_props: dict[str, dict[str, Any]] = {}
    for c in model.getConstructions():
        cname = _name_of(c)
        u, r, mass = _construction_thermal_props(c)
        construction_props[cname] = {
            "u_value_w_m2k": u,
            "r_value_m2k_w": r,
            "thermal_mass_kJ_m2K": mass,
            "is_window": _is_window_construction(c),
        }

    wall, roof, floor, window_opaque = {}, {}, {}, {}
    for s in model.getSurfaces():
        if s.outsideBoundaryCondition() not in ("Outdoors", "Ground"):
            continue
        const = _opt_get(s.construction())
        if const is None:
            continue
        cname = _name_of(const)
        props = construction_props.get(cname, {})
        bucket = {
            "Wall":        wall,
            "RoofCeiling": roof,
            "Floor":       floor,
        }.get(s.surfaceType())
        if bucket is None:
            continue
        bucket.setdefault(cname, {
            "u_value_w_m2k":      props.get("u_value_w_m2k"),
            "r_value_m2k_w":      props.get("r_value_m2k_w"),
            "thermal_mass_kJ_m2K": props.get("thermal_mass_kJ_m2K"),
            "n_surfaces":         0,
            "total_area_m2":      0.0,
        })
        bucket[cname]["n_surfaces"] += 1
        bucket[cname]["total_area_m2"] += s.netArea()

    # 창호 (SimpleGlazing 우선)
    windows = {}
    for ss in model.getSubSurfaces():
        const = _opt_get(ss.construction())
        if const is None:
            continue
        cname = _name_of(const)
        u, shgc = _window_props(const)
        windows.setdefault(cname, {
            "u_value_w_m2k":   u,
            "shgc":            shgc,
            "n_subsurfaces":   0,
            "total_area_m2":   0.0,
        })
        windows[cname]["n_subsurfaces"] += 1
        windows[cname]["total_area_m2"] += ss.netArea()

    return {
        "wall":   wall,
        "roof":   roof,
        "floor":  floor,
        "window": windows,
        "by_construction": construction_props,
    }


def _construction_thermal_props(construction) -> tuple[float | None, float | None, float | None]:
    """불투명 construction의 U, R, thermal mass(kJ/m²K) 계산.

    SimpleGlazing이 포함된 창 construction은 (None, None, None)을 반환.
    """
    R_total = 0.0
    mass_kJ_m2K = 0.0
    has_glazing = False
    for layer in construction.layers():
        # SimpleGlazing 검출
        sg = layer.to_SimpleGlazing()
        if sg.is_initialized():
            has_glazing = True
            continue
        # StandardOpaqueMaterial
        som = layer.to_StandardOpaqueMaterial()
        if som.is_initialized():
            m = som.get()
            t = m.thickness()
            k = m.conductivity()
            if k > 0:
                R_total += t / k
            mass_kJ_m2K += m.density() * m.specificHeat() * t / 1000.0
            continue
        # MasslessOpaqueMaterial
        mom = layer.to_MasslessOpaqueMaterial()
        if mom.is_initialized():
            R_total += mom.get().thermalResistance()
            continue
        # AirGap
        ag = layer.to_AirGap()
        if ag.is_initialized():
            R_total += ag.get().thermalResistance()
            continue
        # 기타 재료는 무시 (U 계산 불가 표시)
    if has_glazing:
        return None, None, None
    if R_total <= 0:
        return None, None, mass_kJ_m2K or None
    return 1.0 / R_total, R_total, mass_kJ_m2K


def _is_window_construction(construction) -> bool:
    for layer in construction.layers():
        if layer.to_SimpleGlazing().is_initialized():
            return True
        if layer.to_StandardGlazing().is_initialized():
            return True
    return False


def _window_props(construction) -> tuple[float | None, float | None]:
    """SimpleGlazing 우선으로 U/SHGC 추출."""
    # ConstructionBase → Construction 캐스팅 (SubSurface는 ConstructionBase로 노출됨)
    if not hasattr(construction, "layers"):
        c_opt = construction.to_Construction()
        if not c_opt.is_initialized():
            return None, None
        construction = c_opt.get()
    for layer in construction.layers():
        sg = layer.to_SimpleGlazing()
        if sg.is_initialized():
            g = sg.get()
            return g.uFactor(), g.solarHeatGainCoefficient()
        sgz = layer.to_StandardGlazing()
        if sgz.is_initialized():
            g = sgz.get()
            u = _opt_value(g.thermalConductance(), None)
            shgc = _opt_value(g.solarHeatGainCoefficient(), None) if hasattr(g, "solarHeatGainCoefficient") else None
            return u, shgc
    return None, None


# ---------------------------------------------------------------------------
# candidates: Infiltration
# ---------------------------------------------------------------------------
def _extract_infiltration(model) -> dict[str, Any]:
    """Optuna: infiltration_multiplier"""
    by_space = {}
    for infil in model.getSpaceInfiltrationDesignFlowRates():
        sp = _opt_get(infil.space())
        st = _opt_get(infil.spaceType())
        target = _name_of(sp) if sp else (f"SpaceType:{_name_of(st)}" if st else "<orphan>")
        method = infil.designFlowRateCalculationMethod()
        record = {
            "name":              _name_of(infil),
            "method":            method,
            "design_flow_rate":  _opt_value(infil.designFlowRate(), None),
            "flow_per_area":     _opt_value(infil.flowperSpaceFloorArea(), None),
            "flow_per_ext_area": _opt_value(infil.flowperExteriorSurfaceArea(), None),
            "ach":               _opt_value(infil.airChangesperHour(), None),
            "schedule":          _name_of(_opt_get(infil.schedule())),
        }
        by_space.setdefault(target, []).append(record)

    by_zone = {}
    for tz in model.getThermalZones():
        zname = _name_of(tz)
        items = []
        for s in tz.spaces():
            items.extend(by_space.get(_name_of(s), []))
            st = _opt_get(s.spaceType())
            if st is not None:
                items.extend(by_space.get(f"SpaceType:{_name_of(st)}", []))
        by_zone[zname] = items

    return {"by_space_or_type": by_space, "by_zone": by_zone}


# ---------------------------------------------------------------------------
# candidates: Ventilation (OA per area / per person)
# ---------------------------------------------------------------------------
def _extract_ventilation(model) -> dict[str, Any]:
    """Optuna: oa_flow_multiplier"""
    out = {}
    for dsoa in model.getDesignSpecificationOutdoorAirs():
        out[_name_of(dsoa)] = {
            "method":            dsoa.outdoorAirMethod(),
            "flow_per_person":   dsoa.outdoorAirFlowperPerson(),
            "flow_per_area":     dsoa.outdoorAirFlowperFloorArea(),
            "flow_per_zone":     dsoa.outdoorAirFlowRate(),
            "ach":               dsoa.outdoorAirFlowAirChangesperHour(),
            "schedule":          _name_of(_opt_get(dsoa.outdoorAirFlowRateFractionSchedule())),
        }

    # space별 적용 매핑
    by_space = {}
    for sp in model.getSpaces():
        dsoa = _opt_get(sp.designSpecificationOutdoorAir())
        if dsoa is not None:
            by_space[_name_of(sp)] = _name_of(dsoa)

    return {"by_dsoa": out, "by_space": by_space}


# ---------------------------------------------------------------------------
# candidates: DHW (peak flow / use rate)
# ---------------------------------------------------------------------------
def _extract_dhw(model) -> dict[str, Any]:
    """Optuna: dhw_use_multiplier"""
    definitions = {}
    for defn in model.getWaterUseEquipmentDefinitions():
        definitions[_name_of(defn)] = {
            "peak_flow_m3_s":          defn.peakFlowRate(),
            "target_temp_schedule":    _name_of(_opt_get(defn.targetTemperatureSchedule())),
            "sensible_fraction_sch":   _name_of(_opt_get(defn.sensibleFractionSchedule())),
            "latent_fraction_sch":     _name_of(_opt_get(defn.latentFractionSchedule())),
        }

    equipments = []
    for eq in model.getWaterUseEquipments():
        defn = eq.waterUseEquipmentDefinition()
        equipments.append({
            "name":              _name_of(eq),
            "definition":        _name_of(defn),
            "space":             _name_of(_opt_get(eq.space())),
            "flow_fraction_sch": _name_of(_opt_get(eq.flowRateFractionSchedule())),
        })

    return {"definitions": definitions, "equipments": equipments}


# ---------------------------------------------------------------------------
# candidates: Plant (boiler / chiller / DHW heater efficiency)
# ---------------------------------------------------------------------------
def _extract_plant(model) -> dict[str, Any]:
    """Optuna: boiler_efficiency_multiplier, chiller_cop_multiplier"""
    boilers = []
    for b in model.getBoilerHotWaters():
        boilers.append({
            "name":         _name_of(b),
            "fuel_type":    b.fuelType(),
            "efficiency":   b.nominalThermalEfficiency(),
            "capacity_w":   _opt_value(b.nominalCapacity(), None),
        })

    chillers = []
    for ch in model.getChillerElectricEIRs():
        chillers.append({
            "name":     _name_of(ch),
            "cop":      _opt_value(ch.referenceCOP(), None) if hasattr(ch, "referenceCOP") else None,
            "leaving_chw_temp": ch.referenceLeavingChilledWaterTemperature(),
            "entering_cnd_temp": ch.referenceEnteringCondenserFluidTemperature(),
        })

    dhw_heaters = []
    for wh in model.getWaterHeaterMixeds():
        dhw_heaters.append({
            "name":         _name_of(wh),
            "fuel_type":    wh.heaterFuelType(),
            "efficiency":   _opt_value(wh.heaterThermalEfficiency(), None),
            "max_temp_c":   _opt_value(wh.maximumTemperatureLimit(), None),
        })

    cooling_towers = []
    for ct in model.getCoolingTowerVariableSpeeds():
        cooling_towers.append({"name": _name_of(ct), "class": "CoolingTowerVariableSpeed"})
    for ct in model.getCoolingTowerSingleSpeeds():
        cooling_towers.append({"name": _name_of(ct), "class": "CoolingTowerSingleSpeed"})

    return {
        "boilers":         boilers,
        "chillers":        chillers,
        "dhw_heaters":     dhw_heaters,
        "cooling_towers":  cooling_towers,
    }


# ---------------------------------------------------------------------------
# candidates: Fans (efficiency / pressure / max flow)
# ---------------------------------------------------------------------------
def _extract_fans(model) -> dict[str, Any]:
    """Optuna: fan_power_multiplier (oa_or_fan_multiplier에 포함되거나 분리)"""
    fans = []
    for getter, label in [
        (model.getFanConstantVolumes, "FanConstantVolume"),
        (model.getFanVariableVolumes, "FanVariableVolume"),
        (model.getFanOnOffs,          "FanOnOff"),
    ]:
        try:
            for f in getter():
                fans.append({
                    "name":           _name_of(f),
                    "class":          label,
                    "efficiency":     _opt_value(f.fanEfficiency(), None) if hasattr(f, "fanEfficiency") else None,
                    "pressure_rise":  _opt_value(f.pressureRise(), None) if hasattr(f, "pressureRise") else None,
                    "max_flow_m3_s":  _opt_value(f.maximumFlowRate(), None) if hasattr(f, "maximumFlowRate") else None,
                })
        except Exception:
            continue

    exhaust_fans = []
    for f in model.getFanZoneExhausts():
        exhaust_fans.append({
            "name":          _name_of(f),
            "efficiency":    f.fanEfficiency(),
            "pressure_rise": f.pressureRise(),
            "max_flow_m3_s": _opt_value(f.maximumFlowRate(), None),
            "thermal_zone":  _name_of(_opt_get(f.thermalZone())),
        })

    return {"fans": fans, "exhaust_fans": exhaust_fans}


# ---------------------------------------------------------------------------
# candidates: Thermal mass (internal mass per zone)
# ---------------------------------------------------------------------------
def _extract_thermal_mass(model) -> dict[str, Any]:
    """Optuna: thermal_mass_multiplier
    InternalMass 객체 + Construction에 내재된 thermal capacity를 모두 추출.
    """
    internal_masses = []
    for im in model.getInternalMasss() if hasattr(model, "getInternalMasss") else []:
        defn = im.internalMassDefinition()
        internal_masses.append({
            "name":             _name_of(im),
            "definition":       _name_of(defn),
            "surface_area_m2":  _opt_value(defn.surfaceArea(), None),
            "area_per_floor":   _opt_value(defn.surfaceAreaperSpaceFloorArea(), None),
            "construction":     _name_of(_opt_get(defn.construction())),
            "space":            _name_of(_opt_get(im.space())),
            "space_type":       _name_of(_opt_get(im.spaceType())),
        })

    # Construction-기반 zone별 thermal mass 합계 (벽/슬래브 표면적 × construction mass)
    cons_mass = {
        _name_of(c): _construction_thermal_props(c)[2]
        for c in model.getConstructions()
    }
    by_zone = {}
    for tz in model.getThermalZones():
        zname = _name_of(tz)
        total_kJ_K = 0.0
        for sp in tz.spaces():
            for srf in sp.surfaces():
                const = _opt_get(srf.construction())
                if const is None:
                    continue
                m = cons_mass.get(_name_of(const))
                if m is None:
                    continue
                total_kJ_K += m * srf.netArea()
        by_zone[zname] = {"surface_thermal_capacity_kJ_K": total_kJ_K}

    return {"internal_masses": internal_masses, "by_zone_surface_capacity": by_zone}


# ---------------------------------------------------------------------------
# 기본 저장 경로
#   추출 결과는 materials/building_params/{building_name}_params.json 으로 저장
# ---------------------------------------------------------------------------
_CODE_DIR = Path(__file__).resolve().parent          # materials/code/
_MATERIALS_DIR = _CODE_DIR.parent                    # materials/
DEFAULT_OUTPUT_DIR = _MATERIALS_DIR / "building_params"


def default_output_path(building_name: str) -> Path:
    """{materials/building_params}/{building_name}_params.json"""
    return DEFAULT_OUTPUT_DIR / f"{building_name}_params.json"


# ---------------------------------------------------------------------------
# CLI demo
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Extract baseline calibration params from OSM")
    parser.add_argument("osm", type=Path, help="Path to baseline OSM file")
    parser.add_argument("--building-name", "--building_name", dest="building_name", default=None,
                        help="Override building name "
                             "(default: read from OSM Building.name(), fallback OSM stem). "
                             "Output → materials/building_params/{name}_params.json")
    parser.add_argument("--out", type=Path, default=None,
                        help="Override output JSON path (default: standard location)")
    args = parser.parse_args()

    params = extract_baseline_params(args.osm)
    building_name = args.building_name or params["metadata"]["building_name"]
    out_path = args.out or default_output_path(building_name)
    save_params(params, out_path)
    md = params["metadata"]
    print(f"Building: {building_name}")
    print(f"Extracted: {md['n_zones']} zones, {md['n_space_types']} space types")
    print(f"Saved to: {out_path}")
