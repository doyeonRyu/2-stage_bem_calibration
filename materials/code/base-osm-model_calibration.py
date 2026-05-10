"""
File: base-osm-model_calibration.py

> Date: 2026-05-02
> Author: 유도연

======================================================================
Purpose:
KETI 건물의 baseline BEM을 생성해 후속 calibration의 기준 OSM을 구축한다.

======================================================================
Description:
Revit -> gbXML -> SketchUp -> OpenStudio 과정을 거친 기본 OSM을 입력으로 받아 층 정보,
북향, Thermal Zone, 재료/구성, 스케줄, 내부부하, thermostat, HVAC, DHW, infiltration 등을
설정하여 Stage 0 baseline 모델을 완성한다.

Input:
- KETI 기본 OSM 파일
- 존/공간 매핑 규칙
- 시스템 및 운영 설정 로직

Output:
- baseline OSM 파일
- 모델 검증 콘솔 로그

======================================================================
Note:
Stage 1과 Stage 2가 공통으로 참조하는 기준 모델을 만드는 스크립트다.

======================================================================
Run:
python materials/code/base-osm-model_calibration.py

"""

# ============================================================
# 0. 라이브러리 및 모델 로드
# ============================================================
import openstudio
from pathlib import Path
from datetime import datetime
import tempfile
import shutil

def resolve_path(path_str: str) -> Path:
    """Resolve Windows-style paths to WSL mount paths when running on Linux."""
    if len(path_str) >= 3 and path_str[1:3] == ":\\":
        drive = path_str[0].lower()
        suffix = path_str[3:].replace("\\", "/")
        return Path(f"/mnt/{drive}/{suffix}")
    return Path(path_str.replace("\\", "/"))

# osm 모델 로드
osm_path = resolve_path(r"C:\Users\ryudo\OneDrive - gachon.ac.kr\2-stage_osm_calibration-osm\KETI_jb_baseline.osm")
out_dir = resolve_path(r"C:\Users\ryudo\OneDrive - gachon.ac.kr\2-stage_osm_calibration-osm\osm")
out_dir.mkdir(parents=True, exist_ok=True)

if not osm_path.exists():
    raise FileNotFoundError(f"OSM 파일 경로를 찾을 수 없습니다: {osm_path}")

loaded = openstudio.osversion.VersionTranslator().loadModel(openstudio.path(str(osm_path)))
if not loaded.is_initialized():
    raise ValueError(f"OSM 파일을 불러오지 못했습니다: {osm_path}")
model = loaded.get()

spaces = model.getSpaces()
thermal_zones = model.getThermalZones()
surfaces = model.getSurfaces()

print("OpenStudio 버전:", openstudio.openStudioVersion())
print("Space 개수:", len(spaces))
print("기존 Thermal Zone 개수:", len(thermal_zones))
print("Surface 개수:", len(surfaces))

# ============================================================
# 1. 층계 정보 반영
# ============================================================
"""
space name 시작에 따라 층계 정보 반영 (revit에서 space name 정의함)
    - sp-b: B1F
    - sp-1: 1F
    - sp-2: 2F
    - sp-3: 3F
    - sp-4: 4F
    - sp-5: 5F
    - sp-r: 6F
"""

story_names = ["B1F", "1F", "2F", "3F", "4F", "5F", "6F"]
stories = {}
for sname in story_names:
    story = openstudio.model.BuildingStory(model)
    story.setName(sname)
    stories[sname] = story

for space in spaces:
    name = space.nameString()
    if name.startswith("sp-b"):
        space.setBuildingStory(stories["B1F"])
    elif name.startswith("sp-1"):
        space.setBuildingStory(stories["1F"])
    elif name.startswith("sp-2"):
        space.setBuildingStory(stories["2F"])
    elif name.startswith("sp-3"):
        space.setBuildingStory(stories["3F"])
    elif name.startswith("sp-4"):
        space.setBuildingStory(stories["4F"])
    elif name.startswith("sp-5"):
        space.setBuildingStory(stories["5F"])
    elif name.startswith("sp-r"):
        space.setBuildingStory(stories["6F"]) # RF

# ============================================================
# 2. True North 반영
# - Revit에서 방향 변경 x함 (최신 버전에는 포함되어 있음)
# - 왼쪽으로 60도 회전
# ============================================================
building = model.getBuilding()
building.setNorthAxis(60.0)

# ============================================================
# 3. Thermal Zone 생성 및 Space 매핑
# ============================================================
"""
Thermal Zone

Fab동
- FAV-CR: 
- FAB-PREC:
- FAB-PROC:
- FAB-PL:
- FAB-SUP: utility 위치에 있는 공간 일부 포함

Utility동
- CUB-ME:
- CUB-UTI:

지원동_sup
- SUP-OFFICE:
- SUP-LAB:
- SUP-DORM:

공용
- COM-COND:
- COM-UNCOND: 
"""

ZONE_DEFS = {
    "TZ-FAB-CR": {
        "name": "FAB_Clean",
        "use": "cleanroom",
        "spaces": [
            "sp-132나노공정실",
            "sp-139나노공정실-2",
        ],
    },
    "TZ-FAB-PREC": {
        "name": "FAB_Precision",
        "use": "precision",
        "spaces": [
            "sp-131장비개발실",
            "sp-138측정실",
        ],
    },
    "TZ-FAB-PROC": {
        "name": "FAB_Process",
        "use": "process_support",
        "spaces": [
            "sp-b135al",
            "sp-134al-1",
            "sp-137al-2",
            "sp-164ds",
            "sp-165ds",
            "sp-166ad",
        ],
    },
    "TZ-FAB-PL": {
        "name": "FAB_Platform",
        "use": "plenum",
        "spaces": [
            "sp-b132plenum",
            "sp-223fabffuplenum",
            "sp-224fab완충공간",
            "sp-225fab수직연통공간",
            "sp-325fab상부공간",
        ],
    },
    "TZ-FAB-SUP": {
        "name": "FAB_Support",
        "use": "fab_support",
        "spaces": [
            "sp-b133장비반입구",
            "sp-119분석실",
            "sp-121vendorroom",
            "sp-140장비반입구",
            "sp-158locker남",
            "sp-159locker여",
            "sp-160smock남",
            "sp-161smock여",
            "sp-162전실",
            "sp-163booth",
        ],
    },
    "TZ-CUB-ME": {
        "name": "Utility_Mechanical",
        "use": "mechanical",
        "spaces": [
            "sp-b151기계실",
            "sp-b152발전기실",
            "sp-b154창고",
            "sp-152공조기실",
            "sp-155창고-1",
            "sp-156창고-2",
            "sp-303공조기실",
            "sp-r022elev기계실",
            "sp-r031elev기계실",
        ],
    },
    "TZ-CUB-UTIL": {
        "name": "Utility_Utilities",
        "use": "utility",
        "spaces": [
            "sp-b131초순수실",
            "sp-b134-1지하저수조",
            "sp-b134-2지하저수조",
            "sp-b136가스정제기실",
            "sp-b153co2",
            "sp-151전기실",
            "sp-153specialgas실",
            "sp-103통신전산실",
        ],
    },
    "TZ-SUP-OFFICE": {
        "name": "Support_Offices",
        "use": "office",
        "spaces": [
            "sp-104fms", "sp-109av실", "sp-110사무실-1", "sp-112회의실",
            "sp-118세미나실", "sp-120전시실",
            "sp-203사무실-1", "sp-204회의실-1", "sp-209사무실-2", "sp-210화의실-2",
            "sp-214av실", "sp-215-1senior사무실-1", "sp-215-2senior사무실-2",
            "sp-215-3senior사무실-3", "sp-216대회의실", "sp-220센터장실",
            "sp-316av실", "sp-319회의실",
            "sp-416av실", "sp-419회의실",
            "sp-511회의실", "sp-528av실",
        ],
    },
    "TZ-SUP-LAB": {
        "name": "Support_Labs",
        "use": "lab",
        "spaces": [
            "sp-304실험실-1", "sp-309연구실-1", "sp-310연구실-2",
            "sp-311개인연구실-1", "sp-312개인연구실-2",
            "sp-317실험실-2", "sp-318실험실-3", "sp-320실험실-4",
            "sp-321실험실-5", "sp-322실험실-6",
            "sp-403실험실-1", "sp-404실험실-2", "sp-409연구실-1",
            "sp-410연구실-2", "sp-411개인연구실-1", "sp-412개인연구실-2",
            "sp-417실험실-3", "sp-418실험실-4", "sp-420실험실-5",
            "sp-421실험실-6", "sp-422실험실-7",
            "sp-512실험실-1", "sp-513실험실-2", "sp-514실험실-3",
            "sp-515실험실-4", "sp-516실험실-5",
        ],
    },
    "TZ-SUP-DORM": {
        "name": "Support_Dormitories",
        "use": "dorm",
        "spaces": [
            "sp-518기숙사", "sp-519기숙사", "sp-520기숙사", "sp-521기숙사", "sp-522기숙사",
            "sp-523기숙사", "sp-524기숙사", "sp-525기숙사", "sp-526기숙사", "sp-527기숙사",
        ],
    },
    "TZ-COM-COND": {
        "name": "Common_Conditioned",
        "use": "common_cond",
        "spaces": [
            "sp-b1022전실", "sp-b134지하층복도",
            "sp-1022전실", "sp-111탕비실", "sp-114방풍실", "sp-116elevhall", "sp-122휴게실",
            "sp-123복도", "sp-124방풍실", "sp-1334전실", "sp-135복도",
            "sp-2022전실", "sp-211탕비실", "sp-2121elevhall", "sp-217휴게실",
            "sp-218탕비실", "sp-219전실", "sp-221복도", "sp-222void",
            "sp-3022전실", "sp-313탕비실", "sp-3141elevhall", "sp-323휴게실", "sp-324복도",
            "sp-4022전실", "sp-413탕비실", "sp-4141elevhall", "sp-423휴게실", "sp-424복도",
            "sp-5022전실", "sp-5061elevhall", "sp-509탕비실", "sp-510휴게실", "sp-517복도",
        ],
    },
    "TZ-COM-UNCOND": {
        "name": "Common_Unconditioned",
        "use": "common_uncond",
        "spaces": [
            "sp-b1012계단실", "sp-b103화장실pit", "sp-b1041elevpit", "sp-b1554계단실", "sp-b1565계단실",
            "sp-1012계단실", "sp-105장애인화장실여", "sp-106화장실남", "sp-107화장실여",
            "sp-108장애인화장실남", "sp-1171계단실", "sp-1544계단실", "sp-1573계단실",
            "sp-2012계단실", "sp-205화장실여", "sp-206화장실남", "sp-207eps실",
            "sp-208청소도구실", "sp-2131계단실",
            "sp-3012계단실", "sp-305화장실여", "sp-306화장실남", "sp-307eps실",
            "sp-308청소도구실", "sp-3151계단실",
            "sp-4012계단실", "sp-405화장실여", "sp-406화장실남", "sp-407eps실",
            "sp-408청소도구실", "sp-4151계단실",
            "sp-5012계단실", "sp-503화장실여", "sp-504화장실남", "sp-505eps실",
            "sp-5071계단실", "sp-508청소도구실",
            "sp-r012계단실", "sp-r041계단실",
        ],
    },
}

space_by_name = {s.nameString(): s for s in spaces} 

# 기존 Thermal Zone 제거
#   변환 과정에서 자동으로 space - thermal zone이 매핑됨
for tz in list(model.getThermalZones()):
    tz.remove()

thermal_zone_map = {}
assigned_spaces = set()
missing_spaces = []

for zone_id, info in ZONE_DEFS.items():
    tz = openstudio.model.ThermalZone(model)
    tz.setName(zone_id)
    thermal_zone_map[zone_id] = tz
    for sp_name in info["spaces"]:
        sp = space_by_name.get(sp_name)
        if sp is None:
            missing_spaces.append(sp_name)
            continue
        sp.setThermalZone(tz)
        assigned_spaces.add(sp_name)

print("Zone 생성 완료:", len(thermal_zone_map))
print("누락 Space:", len(missing_spaces))
if missing_spaces:
    for n in missing_spaces:
        print(" -", n)

# ============================================================
# 4. Weather / Site / RunPeriod
# Jeonju, KOR
# ============================================================
epw_path = resolve_path(r"raw\KOR_CB_Jeonju.471460_TMYx.2011-2025.epw")
with epw_path.open("rb") as f:
    epw_bytes = f.read().replace(b"\r\n", b"\n")
epw_tmp = Path(tempfile.gettempdir()) / epw_path.name
epw_tmp.write_bytes(epw_bytes)

epw_file = openstudio.EpwFile(openstudio.path(str(epw_tmp)))
openstudio.model.WeatherFile.setWeatherFile(model, epw_file)

site = model.getSite()
site.setName("Jeonju")
site.setLatitude(35.858895)
site.setLongitude(127.082250)
site.setTimeZone(9.0)

# 기존의 RunPeriod 제거
for dd in list(model.getDesignDays()):
    dd.remove()

# 실제 전주 기후조건 기준 재설정
# Summer Design Day
dd_s = openstudio.model.DesignDay(model)
dd_s.setName("Jeonju Ann Clg 0.4% Condns DB=>MWB")
dd_s.setDayType("SummerDesignDay")
dd_s.setMonth(8)
dd_s.setDayOfMonth(21)
dd_s.setMaximumDryBulbTemperature(34.3)
dd_s.setDailyDryBulbTemperatureRange(10.2)
dd_s.setHumidityConditionType("Wetbulb")
dd_s.setWetBulbOrDewPointAtMaximumDryBulb(26.3)
dd_s.setBarometricPressure(100667)
dd_s.setWindSpeed(2.1)
dd_s.setWindDirection(225)
dd_s.setRainIndicator(False)
dd_s.setSnowIndicator(False)
dd_s.setDaylightSavingTimeIndicator(False)
dd_s.setSolarModelIndicator("ASHRAEClearSky")
dd_s.setSkyClearness(1.0)

# Winter Design Day
dd_w = openstudio.model.DesignDay(model)
dd_w.setName("Jeonju Ann Htg 99.6% Condns DB")
dd_w.setDayType("WinterDesignDay")
dd_w.setMonth(1)
dd_w.setDayOfMonth(21)
dd_w.setMaximumDryBulbTemperature(-9.5)
dd_w.setDailyDryBulbTemperatureRange(0.0)
dd_w.setHumidityConditionType("Wetbulb")
dd_w.setWetBulbOrDewPointAtMaximumDryBulb(-9.5)
dd_w.setBarometricPressure(100667)
dd_w.setWindSpeed(1.5)
dd_w.setWindDirection(270)
dd_w.setRainIndicator(False)
dd_w.setSnowIndicator(False)
dd_w.setDaylightSavingTimeIndicator(False)
dd_w.setSolarModelIndicator("ASHRAEClearSky")
dd_w.setSkyClearness(0.0)

# RunPeriod 설정 (1년)
rp = model.getRunPeriod()
rp.setBeginMonth(1)
rp.setBeginDayOfMonth(1)
rp.setEndMonth(12)
rp.setEndDayOfMonth(31)

# SimulationControl 설정
sim_ctrl = model.getSimulationControl()
sim_ctrl.setRunSimulationforSizingPeriods(True)
sim_ctrl.setRunSimulationforWeatherFileRunPeriods(True)
sim_ctrl.setSolarDistribution("FullInteriorAndExteriorWithReflections")

# Ground Temperature 설정 (전주 지역 평균 지중온도 기준)
gt = model.getSiteGroundTemperatureBuildingSurface()
gt.setJanuaryGroundTemperature(2.5)
gt.setFebruaryGroundTemperature(3.0)
gt.setMarchGroundTemperature(6.0)
gt.setAprilGroundTemperature(10.5)
gt.setMayGroundTemperature(15.0)
gt.setJuneGroundTemperature(19.5)
gt.setJulyGroundTemperature(22.0)
gt.setAugustGroundTemperature(22.5)
gt.setSeptemberGroundTemperature(20.0)
gt.setOctoberGroundTemperature(15.0)
gt.setNovemberGroundTemperature(9.0)
gt.setDecemberGroundTemperature(4.5)

# ============================================================
# 5. 재료 / Construction
# ============================================================
"""
1) 재료 정의
- 불투명 재료: Mat-Glass-6mm, Mat-Insulation-50mm, Mat-Gypsum-13mm, 
    Mat-Aluminum-3mm, Mat-Concrete-200mm, Mat-MetalSkin, Mat-RoofInsulation-100mm
- 무질량층: Mat-AirGap, Mat-AirGap-50mm
- 창호 재료: SimpleGlazing 기반 Mat-Window

2) Construction 레이어 구성
- Const-CurtainWall: [glass, air_gap, inner_wall] (유리-공기층-내부벽)
- Const-GlassOnly: [glass] (유리 단일층)
- Const-Aluminum: [mat_al] (알루미늄 단일층)
- Const-ProjectedWall: [mat_al, air_gap_50mm, insulation, inner_wall] (돌출 알루미늄 복합벽: 알루미늄-공기층-단열재-내부벽)
- Const-GroundFloor: [mat_conc, insulation] (지상 바닥과 지하 바닥은 일단 동일하게 적용, 필요시 보완)
- Const-IntSlab: [mat_conc] (내부 슬래브는 일단 단일층으로 적용, 필요시 보완)
- Const-IntWall: [inner_wall, inner_wall] (내부 벽은 일단 양면 석고보드로 적용, 필요시 보완)
- Const-SandwichPanel: [mat_metal_skin, insulation, mat_metal_skin] (기본 외벽은 샌드위치 패널로 적용, 필요시 보완)
- Const-Roof: [mat_metal_skin, mat_roof_ins, mat_metal_skin] (지붕은 금속 지붕 + 단열재 + 금속으로 적용, 필요시 보완)
- Const-Window: [win_glaz]
"""

def make_const(name, layers):
    c = openstudio.model.Construction(model)
    c.setName(name)
    v = openstudio.model.MaterialVector()
    for m in layers:
        v.append(m)
    c.setLayers(v)
    return c

# 외장 재료
glass = openstudio.model.StandardOpaqueMaterial(model)
glass.setName("Mat-Glass-6mm")
glass.setRoughness("Smooth")
glass.setThickness(0.006)
glass.setConductivity(1.0)
glass.setDensity(2500)
glass.setSpecificHeat(750)
glass.setThermalAbsorptance(0.9)
glass.setSolarAbsorptance(0.6)
glass.setVisibleAbsorptance(0.6)

air_gap = openstudio.model.MasslessOpaqueMaterial(model)
air_gap.setName("Mat-AirGap")
air_gap.setRoughness("Smooth")
air_gap.setThermalResistance(0.18)

air_gap_50mm = openstudio.model.MasslessOpaqueMaterial(model)
air_gap_50mm.setName("Mat-AirGap-50mm")
air_gap_50mm.setRoughness("Smooth")
air_gap_50mm.setThermalResistance(0.18)

insulation = openstudio.model.StandardOpaqueMaterial(model)
insulation.setName("Mat-Insulation-50mm")
insulation.setRoughness("MediumRough")
insulation.setThickness(0.05)
insulation.setConductivity(0.04)
insulation.setDensity(40)
insulation.setSpecificHeat(1000)

inner_wall = openstudio.model.StandardOpaqueMaterial(model)
inner_wall.setName("Mat-Gypsum-13mm")
inner_wall.setRoughness("Smooth")
inner_wall.setThickness(0.013)
inner_wall.setConductivity(0.16)
inner_wall.setDensity(800)
inner_wall.setSpecificHeat(1000)

mat_al = openstudio.model.StandardOpaqueMaterial(model)
mat_al.setName("Mat-Aluminum-3mm")
mat_al.setRoughness("Smooth")
mat_al.setThickness(0.003)
mat_al.setConductivity(160.0)
mat_al.setDensity(2700)
mat_al.setSpecificHeat(880)
mat_al.setThermalAbsorptance(0.9)
mat_al.setSolarAbsorptance(0.4)
mat_al.setVisibleAbsorptance(0.4)

mat_conc = openstudio.model.StandardOpaqueMaterial(model)
mat_conc.setName("Mat-Concrete-200mm")
mat_conc.setRoughness("MediumRough")
mat_conc.setThickness(0.2)
mat_conc.setConductivity(1.63)
mat_conc.setDensity(2240)
mat_conc.setSpecificHeat(900)

mat_metal_skin = openstudio.model.StandardOpaqueMaterial(model)
mat_metal_skin.setName("Mat-MetalSkin")
mat_metal_skin.setRoughness("Smooth")
mat_metal_skin.setThickness(0.0008)
mat_metal_skin.setConductivity(45.0)
mat_metal_skin.setDensity(7800)
mat_metal_skin.setSpecificHeat(500)

mat_roof_ins = openstudio.model.StandardOpaqueMaterial(model)
mat_roof_ins.setName("Mat-RoofInsulation-100mm")
mat_roof_ins.setRoughness("MediumRough")
mat_roof_ins.setThickness(0.1)
mat_roof_ins.setConductivity(0.04)
mat_roof_ins.setDensity(40)
mat_roof_ins.setSpecificHeat(1000)

const_cw = make_const("Const-CurtainWall", [glass, air_gap, inner_wall])
const_glass_only = make_const("Const-GlassOnly", [glass])
const_al = make_const("Const-Aluminum", [mat_al])
const_projected_wall = make_const("Const-ProjectedWall", [mat_al, air_gap_50mm, insulation, inner_wall])
const_gf = make_const("Const-GroundFloor", [mat_conc, insulation])
const_sl = make_const("Const-IntSlab", [mat_conc])
const_iw = make_const("Const-IntWall", [inner_wall, inner_wall])
const_sw_panel = make_const("Const-SandwichPanel", [mat_metal_skin, insulation, mat_metal_skin])
const_roof = make_const("Const-Roof", [mat_metal_skin, mat_roof_ins, mat_metal_skin])

win_glaz = openstudio.model.SimpleGlazing(model)
win_glaz.setName("Mat-Window")
win_glaz.setUFactor(2.5)
win_glaz.setSolarHeatGainCoefficient(0.4)
const_win = openstudio.model.Construction(model)
const_win.setName("Const-Window")
win_layers = openstudio.model.MaterialVector()
win_layers.append(win_glaz)
const_win.setLayers(win_layers)

def surf_dir(s):
    nm = s.name().get().lower() if s.name().is_initialized() else ""
    parts = nm.split("-")
    if len(parts) >= 2:
        d = parts[1]
        if d == "n":
            return "North"
        if d == "s":
            return "South"
        if d == "e":
            return "East"
        if d == "w":
            return "West"
    nx = s.outwardNormal().x()
    ny = s.outwardNormal().y()
    if abs(ny) >= abs(nx):
        return "North" if ny > 0 else "South"
    return "East" if nx > 0 else "West"

support_cw_targets = {
    "sp-1012계단실", "sp-1022전실", "sp-103통신전산실", "sp-104fms", "sp-105장애인화장실여",
    "sp-106화장실남", "sp-107화장실여", "sp-108장애인화장실남", "sp-109av실", "sp-110사무실-1",
    "sp-111탕비실", "sp-112회의실", "sp-114방풍실", "sp-116elevhall", "sp-1171계단실",
    "sp-118세미나실", "sp-119분석실", "sp-120전시실", "sp-121vendorroom", "sp-122휴게실",
    "sp-123복도", "sp-124방풍실", "sp-203사무실-1", "sp-204회의실-1", "sp-205화장실여",
    "sp-206화장실남", "sp-207eps실", "sp-208청소도구실", "sp-209사무실-2", "sp-210화의실-2",
    "sp-211탕비실", "sp-2121elevhall", "sp-2131계단실", "sp-214av실", "sp-215-1senior사무실-1",
    "sp-215-2senior사무실-2", "sp-215-3senior사무실-3", "sp-216대회의실", "sp-217휴게실",
    "sp-218탕비실", "sp-219전실", "sp-220센터장실", "sp-221복도", "sp-222void", "sp-303공조기실",
    "sp-304실험실-1", "sp-305화장실여", "sp-306화장실남", "sp-307eps실", "sp-308청소도구실",
    "sp-309연구실-1", "sp-310연구실-2", "sp-311개인연구실-1", "sp-312개인연구실-2", "sp-313탕비실",
    "sp-3141elevhall", "sp-3151계단실", "sp-316av실", "sp-317실험실-2", "sp-318실험실-3",
    "sp-319회의실", "sp-320실험실-4", "sp-321실험실-5", "sp-322실험실-6", "sp-323휴게실",
    "sp-324복도", "sp-4022전실", "sp-403실험실-1", "sp-404실험실-2", "sp-405화장실여",
    "sp-406화장실남", "sp-407eps실", "sp-408청소도구실", "sp-409연구실-1", "sp-410연구실-2",
    "sp-411개인연구실-1", "sp-412개인연구실-2", "sp-413탕비실", "sp-4141elevhall", "sp-4151계단실",
    "sp-416av실", "sp-417실험실-3", "sp-418실험실-4", "sp-419회의실", "sp-420실험실-5",
    "sp-421실험실-6", "sp-422실험실-7", "sp-423휴게실", "sp-424복도", "sp-5022전실", "sp-503화장실여",
    "sp-504화장실남", "sp-505eps실", "sp-5061elevhall", "sp-5071계단실", "sp-508청소도구실",
    "sp-509탕비실", "sp-510휴게실", "sp-511회의실", "sp-512실험실-1", "sp-513실험실-2",
    "sp-514실험실-3", "sp-515실험실-4", "sp-516실험실-5", "sp-517복도", "sp-518기숙사",
    "sp-519기숙사", "sp-520기숙사", "sp-521기숙사", "sp-522기숙사", "sp-523기숙사", "sp-524기숙사",
    "sp-525기숙사", "sp-526기숙사", "sp-527기숙사", "sp-528av실"
}

glass_only_spaces = {"sp-114방풍실", "sp-124방풍실"}

projected_wall_surface_targets = {
    "su-s-514-e-w-798",
    "su-s-420-e-w-713",
    "su-s-320-e-w-594",
    "su-s-515-e-w-802",
    "su-s-421-e-w-718",
    "su-s-321-e-w-599",
    "su-e-w-807",
    "su-s-422-e-w-723",
    "su-s-322-e-w-605",
    "su-n-513-e-w-794",
    "su-n-418-e-w-705",
    "su-n-318-e-w-584",
    "su-n-512-e-w-786",
    "su-n-417-e-w-698",
    "su-n-317-e-w-577",
    "su-t-223-e-r-473",
    "su-t-325-e-r-619",
    "su-n-325-e-w-616",
    "su-s-325-e-w-618",
}

projected_wall_shading_targets = {
    "su-x-s-1023",
    "su-x-s-1024",
    "su-x-s-1043",
    "su-x-s-1041",
    "su-x-s-1029",
    "su-x-s-1030",
    "su-x-s-1031",
    "su-x-s-1032",
    "su-x-s-1040",
}

for s in model.getSurfaces():
    if not s.space().is_initialized():
        continue
    sp = s.space().get()
    spn = sp.nameString()
    stype = s.surfaceType()
    obc = s.outsideBoundaryCondition()

# 층계 정보에 따른 외장재 적용
    # B1F, 1F의 지상 바닥과 지하 바닥에 GroundFloor 적용
    if spn.startswith("sp-b"):
        if stype == "Wall" and obc == "Ground":
            s.setConstruction(const_gf)
        elif stype == "Floor" and obc == "Ground":
            s.setConstruction(const_gf)
    elif spn.startswith("sp-1") and stype == "Floor" and obc == "Ground":
        s.setConstruction(const_gf)

    # 
    if stype == "Wall" and obc == "Outdoors":
        direction = surf_dir(s)
        if spn in glass_only_spaces:
            s.setConstruction(const_glass_only) # 방풍실은 내부 마감 없이 유리 단일층 적용
        elif spn in support_cw_targets and direction in ["North", "South"]:
            s.setConstruction(const_cw) # 지원동의 주요 외벽은 북/남향에 커튼월 적용
        else:
            s.setConstruction(const_sw_panel)

    # 내부 벽과 슬래브는 층계에 상관없이 일단 기본적으로 적용, 이후 누락된 부분에 보완 적용
    if stype == "Wall" and obc == "Surface":
        s.setConstruction(const_iw)
    if stype in ["Floor", "RoofCeiling"] and obc == "Surface":
        s.setConstruction(const_sl)
    if stype == "RoofCeiling" and obc == "Outdoors":
        s.setConstruction(const_roof)
    if not s.construction().is_initialized():
        if stype == "Floor":
            s.setConstruction(const_sl)
        elif stype == "RoofCeiling":
            s.setConstruction(const_roof)
        else:
            s.setConstruction(const_sw_panel)

for ss in list(model.getSubSurfaces()):
    base_opt = ss.surface()
    if not base_opt.is_initialized():
        ss.remove()
        continue
    base = base_opt.get()
    if base.outsideBoundaryCondition() == "Surface" and not ss.adjacentSubSurface().is_initialized():
        ss.remove()

for ss in model.getSubSurfaces():
    if not ss.construction().is_initialized():
        ss.setConstruction(const_win)

# 특정 Exterior Surface는 돌출 알루미늄 복합벽, ShadingSurface는 얇은 알루미늄 적용
for s in model.getSurfaces():
    nm = s.name().get() if s.name().is_initialized() else ""
    if nm in projected_wall_surface_targets:
        s.setConstruction(const_projected_wall)
        adj_opt = s.adjacentSurface()
        if adj_opt.is_initialized():
            adj_opt.get().setConstruction(const_projected_wall)

for shd in model.getShadingSurfaces():
    nm = shd.name().get() if shd.name().is_initialized() else ""
    if nm in projected_wall_shading_targets:
        try:
            shd.setConstruction(const_al)
        except Exception:
            pass

# ============================================================
# 6. Schedule
# ============================================================
"""
Sch-AlwaysOn: 24시간 항상 켜짐 스케줄 (조명, 장비 등)
Sch-AlwaysOff: 24시간 항상 꺼짐 스케줄 (조명, 장비 등)

Sch-Occ-Support: 지원동 재실자 스케줄 (평일 0-8 0.025 / 8-18 0.5 / 18-24 0.025, 주말 0.025)
Sch-Light-Support: 지원동 조명 스케줄 (평일 0-8 0.1 / 8-18 0.7 / 18-24 0.1)
Sch-Equip-Support: 지원동 장비 스케줄 (평일 0-8 0.15 / 8-18 0.8 / 18-24 0.15)
Sch-Occ-24h-Low: 24시간 낮은 재실자 스케줄 (평일 0-6 0.08 / 6-18 0.15 / 18-24 0.1, 주말 0.1)
Sch-Occ-Clean: FAB 평일 재실자 스케줄 (평일 0-6 0.2 / 6-18 0.35 / 18-24 0.25, 주말 0.25)
Sch-Light-Clean: FAB 조명 스케줄 (평일 0-6 0.1 / 6-18 0.7 / 18-24 0.1)
Sch-Equip-Clean: FAB 장비 스케줄 (평일 0-6 0.15 / 6-18 0.8 / 18-24 0.15)
Sch-Process-24h: 24시간 프로세스 스케줄 (평일 0-24 0.1)
"""
def make_ruleset_schedule(name, default=0.0):
    sch = openstudio.model.ScheduleRuleset(model)
    sch.setName(name)
    d = sch.defaultDaySchedule()
    d.setName(f"{name}-Default")
    d.addValue(openstudio.Time(0, 24, 0, 0), default)
    return sch

def set_day_values(day_schedule, time_value_pairs):
    day_schedule.clearValues()
    for hh, mm, val in time_value_pairs:
        day_schedule.addValue(openstudio.Time(0, hh, mm, 0), val)

# sch_always_on, sch_always_off: 24시간 항상 켜짐/꺼짐 스케줄
sch_always_on = openstudio.model.ScheduleConstant(model)
sch_always_on.setName("Sch-AlwaysOn")
sch_always_on.setValue(1.0)

sch_always_off = openstudio.model.ScheduleConstant(model)
sch_always_off.setName("Sch-AlwaysOff")
sch_always_off.setValue(0.0)

# 지원동 평일 재실자 스케줄: 0-8 0.025 / 8-18 0.5 / 18-24 0.025, 주말 0.025
sch_occ_support = make_ruleset_schedule("Sch-Occ-Support", 0.025)
set_day_values(
    sch_occ_support.defaultDaySchedule(),
    [(8, 0, 0.025), (18, 0, 0.5), (24, 0, 0.025)]
)
# 평일과 주말을 구분하여 재실자 스케줄 적용
for weekend_name, sat_flag, sun_flag in [("Sat", True, False), ("Sun", False, True)]:
    rule = openstudio.model.ScheduleRule(sch_occ_support)
    rule.setApplySaturday(sat_flag)
    rule.setApplySunday(sun_flag)
    rule.setApplyMonday(False)
    rule.setApplyTuesday(False)
    rule.setApplyWednesday(False)
    rule.setApplyThursday(False)
    rule.setApplyFriday(False)
    set_day_values(rule.daySchedule(), [(24, 0, 0.025)])

# 지원동 조명 스케줄: 0-8 0.1 / 8-18 0.7 / 18-24 0.1
sch_light_support = make_ruleset_schedule("Sch-Light-Support", 0.1)
set_day_values(
    sch_light_support.defaultDaySchedule(),
    [(8, 0, 0.1), (18, 0, 0.7), (24, 0, 0.1)]
)

# 지원동 장비 스케줄: 0-8 0.15 / 8-18 0.8 / 18-24 0.15
sch_equip_support = make_ruleset_schedule("Sch-Equip-Support", 0.15)
set_day_values(
    sch_equip_support.defaultDaySchedule(),
    [(8, 0, 0.15), (18, 0, 0.8), (24, 0, 0.2)]
)

# 24시간 낮은 재실자 스케줄: 0-6 0.08 / 6-18 0.15 / 18-24 0.1, 주말 0.1
sch_occ_24h_low = make_ruleset_schedule("Sch-Occ-24h-Low", 0.1)
set_day_values(
    sch_occ_24h_low.defaultDaySchedule(),
    [(6, 0, 0.08), (18, 0, 0.15), (24, 0, 0.1)]
)

# FAB 평일 재실자 스케줄: 0-6 0.2 / 6-18 0.35 / 18-24 0.25, 주말 0.25
sch_occ_clean = make_ruleset_schedule("Sch-Occ-Clean", 0.25)
set_day_values(
    sch_occ_clean.defaultDaySchedule(),
    [(8, 0, 0.20), (18, 0, 0.35), (24, 0, 0.25)]
)

# FAB 조명 스케줄: 0-6 0.1 / 6-18 0.7 / 18-24 0.1
sch_light_clean = openstudio.model.ScheduleConstant(model)
sch_light_clean.setName("Sch-Light-Clean")
sch_light_clean.setValue(1.0)

# FAB 장비 스케줄: 0-6 0.15 / 6-18 0.8 / 18-24 0.15
sch_equip_clean = openstudio.model.ScheduleConstant(model)
sch_equip_clean.setName("Sch-Equip-Clean")
sch_equip_clean.setValue(1.0)

# 24시간 프로세스 스케줄: 0-24 0.1
sch_process_24h = openstudio.model.ScheduleConstant(model)
sch_process_24h.setName("Sch-Process-24h")
sch_process_24h.setValue(1.0)

# ============================================================
# 7. SpaceType / Internal Loads
# ============================================================

# SpaceType 생성 함수
def make_space_type(name, occ=None, light_w_m2=None, equip_w_m2=None,
                    occ_sch=None, light_sch=None, equip_sch=None,
                    activity_w=120.0):
    st = openstudio.model.SpaceType(model)
    st.setName(name)

    if occ is not None and occ > 0:
        people_def = openstudio.model.PeopleDefinition(model)
        people_def.setPeopleperSpaceFloorArea(occ)
        people = openstudio.model.People(people_def)
        people.setSpaceType(st)
        if occ_sch is not None:
            people.setNumberofPeopleSchedule(occ_sch)
        act_sch = openstudio.model.ScheduleConstant(model)
        act_sch.setName(f"{name}-ActivitySch")
        act_sch.setValue(activity_w)
        people.setActivityLevelSchedule(act_sch)

    if light_w_m2 is not None and light_w_m2 > 0:
        ld = openstudio.model.LightsDefinition(model)
        ld.setWattsperSpaceFloorArea(light_w_m2)
        lights = openstudio.model.Lights(ld)
        lights.setSpaceType(st)
        if light_sch is not None:
            lights.setSchedule(light_sch)

    if equip_w_m2 is not None and equip_w_m2 > 0:
        ed = openstudio.model.ElectricEquipmentDefinition(model)
        ed.setWattsperSpaceFloorArea(equip_w_m2)
        equip = openstudio.model.ElectricEquipment(ed)
        equip.setSpaceType(st)
        if equip_sch is not None:
            equip.setSchedule(equip_sch)

    return st

# SpaceType 정의
space_types = {
    # TZ-SUP-OFFICE: 37.2 m²/인, 10.5 W/m² 조명, 12 W/m² 장비, 지원동 재실자/조명/장비 스케줄
    "office": make_space_type(
        "ST-Office", occ=1 / 37.2, light_w_m2=10.5, equip_w_m2=12.0,
        occ_sch=sch_occ_support, light_sch=sch_light_support, equip_sch=sch_equip_support
    ),
    # TZ-SUP-LAB: 30 m²/인, 14 W/m² 조명, 18 W/m² 장비, 지원동 재실자/조명/장비 스케줄
    "lab": make_space_type(
        "ST-Lab", occ=1 / 30.0, light_w_m2=14.0, equip_w_m2=18.0,
        occ_sch=sch_occ_support, light_sch=sch_light_support, equip_sch=sch_equip_support
    ),
    # TZ-SUP-DORM: 40 m²/인, 7 W/m² 조명, 8 W/m² 장비, 지원동 재실자/조명/장비 스케줄, 활동량 90 W/인
    "dorm": make_space_type(
        "ST-Dorm", occ=1 / 40.0, light_w_m2=7.0, equip_w_m2=8.0,
        occ_sch=sch_occ_support, light_sch=sch_light_support, equip_sch=sch_equip_support, activity_w=90.0
    ),
    # TZ-COM-COND: 80 m²/인, 6 W/m² 조명, 1 W/m² 장비, 지원동 재실자/조명/장비 스케줄
    "common_cond": make_space_type(
        "ST-Common-Cond", occ=1 / 80.0, light_w_m2=6.0, equip_w_m2=1.0,
        occ_sch=sch_occ_support, light_sch=sch_light_support, equip_sch=sch_occ_support
    ),
    # TZ-COM-UNCOND: 0 m²/인, 1 W/m² 조명, 0 W/m² 장비, 항상 꺼짐 스케줄
    "common_uncond": make_space_type(
        "ST-Common-Uncond", occ=0.0, light_w_m2=1.0, equip_w_m2=0.0,
        occ_sch=sch_always_off, light_sch=sch_always_off, equip_sch=sch_always_off
    ),
    # TZ-FAB-CR: 45 m²/인, 18 W/m² 조명, 200 W/m² 장비, FAB 평일 재실자/조명/장비 스케줄
    "cleanroom": make_space_type(
        "ST-Cleanroom", occ=1 / 45.0, light_w_m2=18.0, equip_w_m2=200.0,  # CAL: base 120 + FFU/FU 80 W/m²
        occ_sch=sch_occ_clean, light_sch=sch_light_clean, equip_sch=sch_equip_clean
    ),
    # TZ-FAB-PREC: 50 m²/인, 15 W/m² 조명, 140 W/m² 장비, FAB 평일 재실자/조명/장비 스케줄
    "precision": make_space_type(
        "ST-Precision", occ=1 / 50.0, light_w_m2=15.0, equip_w_m2=140.0,  # CAL: base 90 + FFU/FU 50 W/m²
        occ_sch=sch_occ_clean, light_sch=sch_light_clean, equip_sch=sch_equip_clean
    ),
    # TZ-FAB-SUP: 35 m²/인, 12 W/m² 조명, 10 W/m² 장비, 지원동 재실자/조명/장비 스케줄
    "fab_support": make_space_type(
        "ST-FAB-Support", occ=1 / 35.0, light_w_m2=12.0, equip_w_m2=10.0,
        occ_sch=sch_occ_support, light_sch=sch_light_support, equip_sch=sch_equip_support
    ),
    # TZ-CUB-ME: 0 m²/인, 4 W/m² 조명, 8 W/m² 장비, 항상 꺼짐 스케줄
    "mechanical": make_space_type(
        "ST-Mechanical", occ=0.0, light_w_m2=4.0, equip_w_m2=8.0,
        occ_sch=sch_always_off, light_sch=sch_process_24h, equip_sch=sch_process_24h
    ),
    # TZ-CUB-UTIL: 0 m²/인, 5 W/m² 조명, 60 W/m² 장비, 24시간 프로세스 스케줄
    "utility": make_space_type(
        "ST-Utility", occ=0.0, light_w_m2=5.0, equip_w_m2=60.0,  # CAL: 10->60 W/m²
        occ_sch=sch_always_off, light_sch=sch_process_24h, equip_sch=sch_process_24h
    ),
    # TZ-FAB-PL: 0 m²/인, 2 W/m² 조명, 2 W/m² 장비, 24시간 프로세스 스케줄
    "plenum": make_space_type(
        "ST-Plenum", occ=0.0, light_w_m2=0.0, equip_w_m2=0.0,
        occ_sch=sch_always_off, light_sch=sch_always_off, equip_sch=sch_always_off
    ),
    # TZ-FAB-PROC: 0 m²/인, 2 W/m² 조명, 2 W/m² 장비, 24시간 프로세스 스케줄
    "process_support": make_space_type(
        "ST-Process-Support", occ=0.0, light_w_m2=2.0, equip_w_m2=2.0,
        occ_sch=sch_always_off, light_sch=sch_process_24h, equip_sch=sch_process_24h
    ),
}

# SpaceType을 공간에 할당 (ZONE_DEFS의 공간 이름 리스트를 기반으로)
for zone_id, info in ZONE_DEFS.items():
    st = space_types.get(info["use"])
    if st is None:
        continue
    for sp_name in info["spaces"]: # 공간 이름 리스트에서 SpaceType 할당
        sp = space_by_name.get(sp_name)
        if sp is not None:
            sp.setSpaceType(st)

# ============================================================
# 8. Thermostat
# - Cooling Setpoint, Heating Setpoint, Thermostat Schedule 등 설정
# ============================================================

# Thermostat Schedule 생성 함수
def make_temp_schedule(name, occupied, setback=None, always=False):
    sch = openstudio.model.ScheduleRuleset(model)
    sch.setName(name)
    day = sch.defaultDaySchedule()
    day.clearValues()
    if always or setback is None: # 항상 켜짐/꺼짐 스케줄이거나 setback이 없는 경우, 24시간 동일한 온도 유지
        day.addValue(openstudio.Time(0, 24, 0, 0), occupied)
    else: # 일반적인 경우, 평일 8-18시에는 occupied 온도, 그 외 시간에는 setback 온도로 설정
        day.addValue(openstudio.Time(0, 8, 0, 0), setback)
        day.addValue(openstudio.Time(0, 18, 0, 0), occupied)
        day.addValue(openstudio.Time(0, 24, 0, 0), setback)
    return sch

# Thermostat Schedule 생성

# TZ-FAB-CR: 냉방: 22.0°C, 난방: 21.0°C, 항상 켜짐 (setback 없음)
clg_sch_clean = make_temp_schedule("Clg-Sch-Clean", 22.0, always=True)
htg_sch_clean = make_temp_schedule("Htg-Sch-Clean", 21.0, always=True)

# TZ-FAB-PREC: 냉방: 22.0°C, 난방: 21.0°C, 항상 켜짐 (setback 없음)
clg_sch_precision = make_temp_schedule("Clg-Sch-Precision", 22.0, always=True)
htg_sch_precision = make_temp_schedule("Htg-Sch-Precision", 22.0, always=True)

# TZ-SUP-OFFICE: 냉방: 26.0°C (setback 28.0°C), 난방: 23.0°C (setback 19.0°C)
clg_sch_office = make_temp_schedule("Clg-Sch-Office", 26.0, setback=28.0)
htg_sch_office = make_temp_schedule("Htg-Sch-Office", 23.0, setback=19.0)

# TZ-SUP-LAB: 냉방: 26.0°C (setback 28.0°C), 난방: 23.0°C (setback 19.0°C)
clg_sch_lab = make_temp_schedule("Clg-Sch-Lab", 26.0, setback=28.0)
htg_sch_lab = make_temp_schedule("Htg-Sch-Lab", 23.0, setback=19.0)

# TZ-COM-COND: 냉방: 26.0°C (setback 28.0°C), 난방: 22.0°C (setback 18.0°C)
clg_sch_common = make_temp_schedule("Clg-Sch-Common", 26.0, setback=28.0)
htg_sch_common = make_temp_schedule("Htg-Sch-Common", 22.0, setback=18.0)

# TZ-SUP-DORM: 냉방: 26.0°C (setback 27.0°C), 난방: 21.0°C (setback 19.0°C)
clg_sch_dorm = make_temp_schedule("Clg-Sch-Dorm", 26.0, setback=27.0, always=True)
htg_sch_dorm = make_temp_schedule("Htg-Sch-Dorm", 21.0, setback=19.0, always=True)

# TZ-CUB-UTIL: 냉방: 26.0°C, 난방: 19.0°C, 항상 켜짐 (setback 없음)
clg_sch_util = make_temp_schedule("Clg-Sch-Util", 26.0, always=True)
htg_sch_util = make_temp_schedule("Htg-Sch-Util", 19.0, always=True)

zone_tstat_map = {
    "TZ-FAB-CR": (clg_sch_clean, htg_sch_clean),
    "TZ-FAB-PREC": (clg_sch_precision, htg_sch_precision),
    "TZ-FAB-SUP": (clg_sch_office, htg_sch_office),
    "TZ-CUB-ME": (clg_sch_util, htg_sch_util),
    "TZ-CUB-UTIL": (clg_sch_util, htg_sch_util),
    "TZ-SUP-OFFICE": (clg_sch_office, htg_sch_office),
    "TZ-SUP-LAB": (clg_sch_lab, htg_sch_lab),
    "TZ-SUP-DORM": (clg_sch_dorm, htg_sch_dorm),
    "TZ-COM-COND": (clg_sch_common, htg_sch_common),
}

# Thermostat 생성 및 Thermal Zone에 할당
for zone_id, (clg_sch, htg_sch) in zone_tstat_map.items():
    tz = thermal_zone_map[zone_id]
    tstat = openstudio.model.ThermostatSetpointDualSetpoint(model)
    tstat.setName(f"Tstat-{zone_id}")
    tstat.setCoolingSetpointTemperatureSchedule(clg_sch)
    tstat.setHeatingSetpointTemperatureSchedule(htg_sch)
    tz.setThermostatSetpointDualSetpoint(tstat)

# ============================================================
# 9. 기존 Plant / AirLoop / Zone HVAC 정리
# - 새로 구성 
# ============================================================
# 기존에 존재하는 PlantLoop, AirLoopHVAC, ZoneHVACPackagedTerminalHeatPump, ZoneHVACFourPipeFanCoil, FanZoneExhaust 등은 제거
for obj in list(model.getPlantLoops()):
    obj.remove()
for obj in list(model.getAirLoopHVACs()):
    obj.remove()
for obj in list(model.getZoneHVACPackagedTerminalHeatPumps()):
    obj.remove()
for obj in list(model.getZoneHVACFourPipeFanCoils()):
    obj.remove()
for obj in list(model.getFanZoneExhausts()):
    obj.remove()


def safe_remove_model_objects(getter_name):
    getter = getattr(model, getter_name, None)
    if getter is None:
        return
    try:
        for obj in list(getter()):
            obj.remove()
    except TypeError:
        # 일부 OpenStudio Python 바인딩에서는 WaterUse 계열 getter가 직접 iterable로 노출되지 않음
        pass

# WaterUse 계열 객체 제거 
# (WaterUseConnections, WaterUseEquipments, WaterUseEquipmentDefinitions, WaterHeaterMixeds 등)
for getter_name in [
    "getWaterUseConnections",
    "getWaterUseEquipments",
    "getWaterUseEquipmentDefinitions",
    "getWaterHeaterMixeds",
]:
    safe_remove_model_objects(getter_name)

always_on = model.alwaysOnDiscreteSchedule()

# ============================================================
# 10. Plant Loop
# - Chilled Water Loop, Condenser Water Loop, Heating Water Loop, Domestic Hot Water Loop 등 구성
# ============================================================
"""
Chilled Water Loop: 실제 진단설비 기준 450RT x 3, 10/5°C
    - ChillerElectricEIR 모델 사용, Reference Conditions 10/5°C, Setpoint 5°C로 설정
    - Setpoint Manager로 공급수 온도 제어, 스케줄은 항상 5°C 유지
Condenser Water Loop: 실제 냉각탑 500CRT x 3, 37/32°C 직교류형
    - CoolingTowerVariableSpeed 모델 사용, Setpoint 32°C로 설정
     - Setpoint Manager로 공급수 온도 제어, 스케줄은 항상 32°C 유지
Heating Water Loop: 보일러 3대, 실사용 계통 60/50°C 반영
    - BoilerHotWater 모델 사용, Fuel Type은 NaturalGas, Nominal Thermal Efficiency 92%로 설정
     - Setpoint Manager로 공급수 온도 제어, 스케줄은 항상 60°C 유지
Domestic Hot Water Loop: 실사용 계통 60/10°C 반영, 혼합형 온수탱크 1대, 가열부는 보일러 연동, 최대온도 60°C, 효율 90%로 설정    
    - DHW Loop는 실제로는 별도의 온수탱크와 가열부로 구성되지만, 모델링 편의상 가열부를 온수탱크에 통합하여 단일 PlantLoop로 구성
    - WaterHeaterMixed 모델 사용, Heater Fuel Type은 NaturalGas, Heater Thermal Efficiency 90%, Maximum Temperature Limit 60°C로 설정
     - Setpoint Manager로 공급수 온도 제어, 스케줄은 항상60°C 유지
"""
# Chilled Water Loop: 실제 진단설비 기준 450RT x 3, 10/5°C
chw_loop = openstudio.model.PlantLoop(model)
chw_loop.setName("CHW-Loop")
chw_loop.setMaximumLoopTemperature(15.0)
chw_loop.setMinimumLoopTemperature(4.0)

chw_pump = openstudio.model.PumpVariableSpeed(model)
chw_pump.setName("CHW-Pump")
chw_pump.addToNode(chw_loop.supplyInletNode())

for i in range(1, 4):
    ch = openstudio.model.ChillerElectricEIR(model)
    ch.setName(f"CH-{i}")
    ch.setReferenceLeavingChilledWaterTemperature(5.0)
    ch.setReferenceEnteringCondenserFluidTemperature(32.0)
    chw_loop.addSupplyBranchForComponent(ch)

chw_sch = openstudio.model.ScheduleConstant(model)
chw_sch.setName("CHW-Setpoint-Sch")
chw_sch.setValue(5.0)
chw_spm = openstudio.model.SetpointManagerScheduled(model, chw_sch)
chw_spm.setControlVariable("Temperature")
chw_spm.addToNode(chw_loop.supplyOutletNode())

# Condenser Water Loop: 실제 냉각탑 500CRT x 3, 37/32°C 직교류형
cw_loop = openstudio.model.PlantLoop(model)
cw_loop.setName("CW-Loop")
cw_loop.setMaximumLoopTemperature(37.0)
cw_loop.setMinimumLoopTemperature(15.0)

cw_pump = openstudio.model.PumpVariableSpeed(model)
cw_pump.setName("CW-Pump")
cw_pump.addToNode(cw_loop.supplyInletNode())

for i in range(1, 4):
    ct = openstudio.model.CoolingTowerVariableSpeed(model)
    ct.setName(f"CT-{i}")
    cw_loop.addSupplyBranchForComponent(ct)

cw_sch = openstudio.model.ScheduleConstant(model)
cw_sch.setName("CW-Setpoint-Sch")
cw_sch.setValue(32.0)
cw_spm = openstudio.model.SetpointManagerScheduled(model, cw_sch)
cw_spm.setControlVariable("Temperature")
cw_spm.addToNode(cw_loop.supplyOutletNode())

for ch in model.getChillerElectricEIRs():
    cw_loop.addDemandBranchForComponent(ch)

# Heating Water Loop: 보일러 3대, 실사용 계통 60/50°C 반영
hw_loop = openstudio.model.PlantLoop(model)
hw_loop.setName("HW-Loop")
hw_loop.setMaximumLoopTemperature(70.0)
hw_loop.setMinimumLoopTemperature(30.0)

hw_pump = openstudio.model.PumpVariableSpeed(model)
hw_pump.setName("HW-Pump")
hw_pump.addToNode(hw_loop.supplyInletNode())

for i in range(1, 4):
    boiler = openstudio.model.BoilerHotWater(model)
    boiler.setName(f"B-{i:02d}")
    boiler.setFuelType("NaturalGas")
    boiler.setNominalThermalEfficiency(0.92)
    hw_loop.addSupplyBranchForComponent(boiler)

hw_sch = openstudio.model.ScheduleConstant(model)
hw_sch.setName("HW-Setpoint-Sch")
hw_sch.setValue(60.0)
hw_spm = openstudio.model.SetpointManagerScheduled(model, hw_sch)
hw_spm.setControlVariable("Temperature")
hw_spm.addToNode(hw_loop.supplyOutletNode())

# Domestic Hot Water Loop
dhw_loop = openstudio.model.PlantLoop(model)
dhw_loop.setName("DHW-Loop")
dhw_loop.setMaximumLoopTemperature(80.0)
dhw_loop.setMinimumLoopTemperature(10.0)

dhw_pump = openstudio.model.PumpVariableSpeed(model)
dhw_pump.setName("DHW-Pump")
dhw_pump.addToNode(dhw_loop.supplyInletNode())

dhw_setpoint_sch = openstudio.model.ScheduleConstant(model)
dhw_setpoint_sch.setName("DHW-Setpoint-Sch")
dhw_setpoint_sch.setValue(60.0)
dhw_spm = openstudio.model.SetpointManagerScheduled(model, dhw_setpoint_sch)
dhw_spm.setControlVariable("Temperature")
dhw_spm.addToNode(dhw_loop.supplyOutletNode())

dhw_heater = openstudio.model.WaterHeaterMixed(model)
dhw_heater.setName("DHW-Heater")
dhw_heater.setHeaterFuelType("NaturalGas")
dhw_heater.setHeaterThermalEfficiency(0.90)
dhw_heater.setMaximumTemperatureLimit(60.0)
dhw_heater.setSetpointTemperatureSchedule(dhw_setpoint_sch)
dhw_loop.addSupplyBranchForComponent(dhw_heater)

# ============================================================
# 11. HVAC Helper
# - AirLoopHVAC, ZoneHVACPackagedTerminalHeatPump, ZoneHVACFourPipeFanCoil, FanZoneExhaust 등 
#   생성 및 Thermal Zone에 할당하는 함수 정의
# ============================================================

# AirLoopHVAC 생성 함수: OA 시스템, 팬, 냉각코일, 난방코일, SAT 제어 포함
def add_exhaust_fan_to_zone(zone, name, flow_m3s, schedule=None, pressure_rise=300.0):
    if schedule is None:
        schedule = always_on
    fan = openstudio.model.FanZoneExhaust(model)
    fan.setName(name)
    fan.setAvailabilitySchedule(schedule)
    fan.setFanEfficiency(0.55)
    fan.setPressureRise(pressure_rise)
    fan.setMaximumFlowRate(flow_m3s)
    fan.addToThermalZone(zone)
    return fan

# Outdoor Air 시스템을 포함한 AirLoopHVAC 생성 함수
def add_oa_per_area_to_space(space, name, oa_m3_s_m2):
    dsoa = openstudio.model.DesignSpecificationOutdoorAir(model)
    dsoa.setName(name)
    dsoa.setOutdoorAirMethod("Flow/Area")
    dsoa.setOutdoorAirFlowperFloorArea(oa_m3_s_m2)
    space.setDesignSpecificationOutdoorAir(dsoa)
    return dsoa

# AirLoopHVAC 생성 함수: OA 시스템, 팬, 냉각코일, 난방코일, SAT 제어 포함
def make_oac_loop(loop_name, supply_temp_c):
    air_loop = openstudio.model.AirLoopHVAC(model)
    air_loop.setName(loop_name)

    oa_ctrl = openstudio.model.ControllerOutdoorAir(model)
    oa_ctrl.setName(f"{loop_name}-OA-Ctrl")
    oa_sys = openstudio.model.AirLoopHVACOutdoorAirSystem(model, oa_ctrl)
    oa_sys.setName(f"{loop_name}-OA-System")
    oa_sys.addToNode(air_loop.supplyInletNode())

    fan = openstudio.model.FanConstantVolume(model, always_on)
    fan.setName(f"{loop_name}-SupplyFan")
    fan.addToNode(air_loop.supplyInletNode())

    cc = openstudio.model.CoilCoolingWater(model)
    cc.setName(f"{loop_name}-CC")
    chw_loop.addDemandBranchForComponent(cc)
    cc.addToNode(air_loop.supplyOutletNode())

    hc = openstudio.model.CoilHeatingWater(model)
    hc.setName(f"{loop_name}-HC")
    hw_loop.addDemandBranchForComponent(hc)
    hc.addToNode(air_loop.supplyOutletNode())

    sat_sch = openstudio.model.ScheduleConstant(model)
    sat_sch.setName(f"{loop_name}-SAT")
    sat_sch.setValue(supply_temp_c)
    spm = openstudio.model.SetpointManagerScheduled(model, sat_sch)
    spm.setControlVariable("Temperature")
    spm.addToNode(air_loop.supplyOutletNode())

    return air_loop

# CAV 리히트 터미널 생성 함수: 팬, 난방코일 포함
def make_cav_reheat_terminal(name):
    hc = openstudio.model.CoilHeatingWater(model)
    hc.setName(f"{name}-RHC")
    hw_loop.addDemandBranchForComponent(hc)
    terminal = openstudio.model.AirTerminalSingleDuctConstantVolumeReheat(model, always_on, hc)
    terminal.setName(name)
    return terminal

# PTHP 생성 함수: 팬, 냉각코일, 난방코일, 보조난방코일 포함
def make_pthp(name):
    fan = openstudio.model.FanOnOff(model, always_on)
    htg = openstudio.model.CoilHeatingDXSingleSpeed(model)
    clg = openstudio.model.CoilCoolingDXSingleSpeed(model)
    supp = openstudio.model.CoilHeatingElectric(model, always_on)
    pthp = openstudio.model.ZoneHVACPackagedTerminalHeatPump(model, always_on, fan, htg, clg, supp)
    pthp.setName(name)
    return pthp

# 4-pipe Fan Coil Unit 생성 함수: 팬, 냉각코일, 난방코일 포함
def make_four_pipe_fcu(name):
    fan = openstudio.model.FanOnOff(model, always_on)
    cc = openstudio.model.CoilCoolingWater(model)
    cc.setName(f"{name}-CC")
    chw_loop.addDemandBranchForComponent(cc)
    hc = openstudio.model.CoilHeatingWater(model)
    hc.setName(f"{name}-HC")
    hw_loop.addDemandBranchForComponent(hc)
    fcu = openstudio.model.ZoneHVACFourPipeFanCoil(model, always_on, fan, cc, hc)
    fcu.setName(name)
    return fcu

# DHW 부하 생성 함수: WaterUseEquipment과 WaterUseConnections을 사용하여 온수 부하 모델링, DHW Loop에 연결
def add_dhw_load(name, space_name, peak_m3_s, flow_fraction_schedule):
    sp = space_by_name.get(space_name)
    if sp is None:
        return None

    target_temp_sch = openstudio.model.ScheduleConstant(model)
    target_temp_sch.setName(f"{name}-TargetTemp")
    target_temp_sch.setValue(43.0)

    defn = openstudio.model.WaterUseEquipmentDefinition(model)
    defn.setName(f"{name}-Def")
    defn.setPeakFlowRate(peak_m3_s)
    defn.setTargetTemperatureSchedule(target_temp_sch)

    equip = openstudio.model.WaterUseEquipment(defn)
    equip.setName(name)
    equip.setFlowRateFractionSchedule(flow_fraction_schedule)
    equip.setSpace(sp)

    conn = openstudio.model.WaterUseConnections(model)
    conn.setName(f"{name}-Conn")
    conn.addWaterUseEquipment(equip)
    dhw_loop.addDemandBranchForComponent(conn)
    return conn

# ============================================================
# 12. FAB HVAC
# - FAB Cleanroom, Precision, Support 존에 대한 HVAC 시스템 구성
# ============================================================
# 실제/설계 타협: FAB는 OAC + FU/FFU 조합 반영
# Clean / Precision은 100% 외기 OAC + zone recirculation FCU로 근사

# FAB OA per Area 설정: Cleanroom 7 L/s/m², Precision 6 L/s/m², Support 3 L/s/m²
FAB_OA_PER_AREA = {
    "TZ-FAB-CR": 0.0070,
    "TZ-FAB-PREC": 0.0060,
    "TZ-FAB-SUP": 0.0030,
}

for zid, oa_per_area in FAB_OA_PER_AREA.items():
    for sp_name in ZONE_DEFS[zid]["spaces"]:
        sp = space_by_name.get(sp_name)
        if sp is not None:
            add_oa_per_area_to_space(sp, f"DSOA-{sp_name}", oa_per_area)

# 가스 보정: OA 2배로 OAC 코일 부하를 높이고, SAT를 낮춰 terminal reheat 부담도 확대
oac_fab = make_oac_loop("OAC-FAB", 19.0)
for zid in ["TZ-FAB-CR", "TZ-FAB-PREC"]:
    diffuser = make_cav_reheat_terminal(f"ATU-{zid}")
    oac_fab.addBranchForZone(thermal_zone_map[zid], diffuser.to_StraightComponent())

# Cleanroom / Precision recirculation (FU/FFU 근사)
for zid in ["TZ-FAB-CR", "TZ-FAB-PREC"]:
    fcu = make_four_pipe_fcu(f"FU-{zid}")
    fcu.addToThermalZone(thermal_zone_map[zid])

# FAB support는 일반 공조 + OAC 일부 공급 + 존 장비 없음
support_diffuser = make_cav_reheat_terminal("ATU-TZ-FAB-SUP")
oac_fab.addBranchForZone(thermal_zone_map["TZ-FAB-SUP"], support_diffuser.to_StraightComponent())

# FAB 배기 상향
add_exhaust_fan_to_zone(thermal_zone_map["TZ-FAB-CR"], "Exh-TZ-FAB-CR", flow_m3s=3.20)
add_exhaust_fan_to_zone(thermal_zone_map["TZ-FAB-PREC"], "Exh-TZ-FAB-PREC", flow_m3s=2.20)
add_exhaust_fan_to_zone(thermal_zone_map["TZ-FAB-PROC"], "Exh-TZ-FAB-PROC", flow_m3s=5.00)
add_exhaust_fan_to_zone(thermal_zone_map["TZ-FAB-SUP"], "Exh-TZ-FAB-SUP", flow_m3s=2.00, schedule=sch_occ_support)

# 플리넘은 비조화
thermal_zone_map["TZ-FAB-PL"].setUseIdealAirLoads(False)

# ============================================================
# 13. 지원동 / 유틸리티 HVAC
# - 진단보고서 운영 기준을 반영하여 지원동 사무실/연구실/기숙사/공용은 PTHP 계열로 구성
# - 유틸리티는 존별 개별 장비 + 국소 배기 중심으로 단순화
# ============================================================

# 지원동 사무실/연구실/기숙사/공용 및 일부 유틸리티는 PTHP 적용
for zid in ["TZ-SUP-OFFICE", "TZ-SUP-LAB", "TZ-SUP-DORM", "TZ-COM-COND", "TZ-CUB-UTIL"]:
    pthp = make_pthp(f"PTHP-{zid}")
    pthp.addToThermalZone(thermal_zone_map[zid])

# 연구실/실험실 국소 배기
add_exhaust_fan_to_zone(thermal_zone_map["TZ-SUP-LAB"], "Exh-TZ-SUP-LAB", flow_m3s=1.00, schedule=sch_occ_support)

# Utility mechanical은 환기 위주
add_exhaust_fan_to_zone(thermal_zone_map["TZ-CUB-ME"], "Exh-TZ-CUB-ME", flow_m3s=1.00)
add_exhaust_fan_to_zone(thermal_zone_map["TZ-CUB-UTIL"], "Exh-TZ-CUB-UTIL", flow_m3s=0.80)

# 비조화 영역
thermal_zone_map["TZ-COM-UNCOND"].setUseIdealAirLoads(False)

# ============================================================
# 14. DHW Loads
# - 지원동 사무실/연구실/공용은 0.12~0.18 L/s peak, 기숙사는 0.27 L/s peak로 설정, 지원동 재실자/조명 스케줄 적용
# 
# ============================================================
add_dhw_load("DHW-Office", "sp-111탕비실", peak_m3_s=0.00018, flow_fraction_schedule=sch_occ_support)
add_dhw_load("DHW-Lab", "sp-304실험실-1", peak_m3_s=0.000135, flow_fraction_schedule=sch_occ_support)
add_dhw_load("DHW-Common", "sp-211탕비실", peak_m3_s=0.00012, flow_fraction_schedule=sch_occ_support)
add_dhw_load("DHW-Dorm", "sp-518기숙사", peak_m3_s=0.00027, flow_fraction_schedule=sch_always_on)


# ============================================================
# 15. Infiltration
# - FAB은 0, 지원동은 0.0003 m3/s·m2, 유틸리티는 0.0001 m3/s·m2로 설정, 나머지는 0.0003 m3/s·m2로 설정
# ============================================================
# source-faithful: FAB 0, 지원동 0.0003 m3/s·m2, Utility 0.0001 m3/s·m2

def add_infiltration_ext_area(space, name, val_m3_s_m2, schedule):
    infil = openstudio.model.SpaceInfiltrationDesignFlowRate(model)
    infil.setName(name)
    infil.setSchedule(schedule)
    infil.setFlowperExteriorSurfaceArea(val_m3_s_m2)
    infil.setSpace(space)
    return infil


for s in spaces:
    n = s.nameString()

    if n in ZONE_DEFS["TZ-FAB-CR"]["spaces"] or n in ZONE_DEFS["TZ-FAB-PREC"]["spaces"]:
        add_infiltration_ext_area(s, f"Infil-{n}", 0.0, sch_always_on)
    elif n in ZONE_DEFS["TZ-FAB-PROC"]["spaces"]:
        add_infiltration_ext_area(s, f"Infil-{n}", 0.0001, sch_always_on)
    elif n in ZONE_DEFS["TZ-FAB-PL"]["spaces"]:
        add_infiltration_ext_area(s, f"Infil-{n}", 0.0000, sch_always_on)
    elif n in ZONE_DEFS["TZ-FAB-SUP"]["spaces"]:
        add_infiltration_ext_area(s, f"Infil-{n}", 0.0002, sch_occ_support)
    elif n in ZONE_DEFS["TZ-SUP-OFFICE"]["spaces"] or n in ZONE_DEFS["TZ-SUP-LAB"]["spaces"] or n in ZONE_DEFS["TZ-SUP-DORM"]["spaces"] or n in ZONE_DEFS["TZ-COM-COND"]["spaces"]:
        add_infiltration_ext_area(s, f"Infil-{n}", 0.0003, sch_always_on)
    elif n in ZONE_DEFS["TZ-CUB-ME"]["spaces"] or n in ZONE_DEFS["TZ-CUB-UTIL"]["spaces"]:
        add_infiltration_ext_area(s, f"Infil-{n}", 0.0001, sch_always_on)
    elif n in ZONE_DEFS["TZ-COM-UNCOND"]["spaces"]:
        add_infiltration_ext_area(s, f"Infil-{n}", 0.0005, sch_always_on)
    else:
        add_infiltration_ext_area(s, f"Infil-{n}", 0.0003, sch_always_on)


# ============================================================
# 16. 검증
# - Thermal Zone별 공간/장비 개수, SpaceType/ThermalZone 미할당 공간 리스트 등 점검
# ============================================================
print("=" * 60)
print("검증 시작")
for tz in model.getThermalZones():
    print(f"[ZONE] {tz.nameString():20s} | spaces={len(tz.spaces()):2d} | equip={len(tz.equipment()):2d}")

spaces_without_st = [s.nameString() for s in spaces if not s.spaceType().is_initialized()]
spaces_without_tz = [s.nameString() for s in spaces if not s.thermalZone().is_initialized()]

print("SpaceType 미할당:", len(spaces_without_st))
for n in spaces_without_st:
    print(" -", n)

print("ThermalZone 미할당:", len(spaces_without_tz))
for n in spaces_without_tz:
    print(" -", n)


# ============================================================
# 17. 저장
# ============================================================
duplicate_path = resolve_path(r"E:\AiCE2\2026\01_BIM-UBEM-LLM\2-stage_osm_calibration\osm")
duplicate_path.mkdir(parents=True, exist_ok=True)
filename = f"baseline_osm_{datetime.now().strftime('%Y%m%d_%H%M')}.osm"
save_path = duplicate_path / filename
model.save(openstudio.path(str(save_path)), True)

external_save_path = out_dir / filename
if external_save_path != save_path:
    out_dir.mkdir(parents=True, exist_ok=True)
    try:
        shutil.copy2(str(save_path), str(external_save_path))
    except OSError as exc:
        print(f"외부 복사 생략: {external_save_path} ({exc})")

print(f"모델 저장 완료: {save_path}")
if external_save_path != save_path:
    if external_save_path.exists():
        print(f"외부 복사 완료: {external_save_path}")
