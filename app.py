import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# ============================================================
# 설정
# ============================================================
st.set_page_config(
    page_title="바이오 IR 데이터베이스",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# 데이터 로드
# ============================================================
@st.cache_data
def load_data():
    data_path = Path("data/ir_database.xlsx")
    if not data_path.exists():
        st.error("data/ir_database.xlsx 파일이 없습니다.")
        st.stop()

    # 필요한 컬럼만 로드해서 메모리 절약
    needed_cols = [
        "회사명", "국가", "설립연도", "기업단계", "임직원수",
        "대표이사", "주요사업 한줄요약", "홈페이지",
        "자본금", "누적 투자유치액", "현재 투자단계", "주요 투자사",
        "치료영역", "모달리티", "세부 적응증", "핵심 타깃/MoA",
        "리드에셋 코드명", "리드에셋 개발단계",
        "잠재 파트너사 / 고객사",
        "특허 등록 건수", "특허 출원 건수", "PCT 출원 여부",
        "파일명", "파싱일자"
    ]

    # 실제 존재하는 컬럼만 선택
    all_cols = pd.read_excel(data_path, nrows=0).columns.tolist()
    use_cols  = [c for c in needed_cols if c in all_cols]

    df = pd.read_excel(data_path, usecols=use_cols)
    df = df.fillna("")

    # 문자열 컬럼 메모리 최적화
    for col in df.select_dtypes(include="str").columns:
        df[col] = df[col].astype("string")

    return df

df = load_data()


# ============================================================
# 치료영역 그룹핑 매핑 (우선순위 순서대로 검사)
# ============================================================
DISEASE_GROUP_MAP = [
    # 종양/항암 (가장 많음 - 우선 검사)
    ("혈액암",      ["혈액암", "백혈병", "림프종", "다발성골수종", "혈액 내 감염"]),
    ("고형암",      ["고형암", "폐암", "간암", "췌장암", "위암", "대장암", "유방암", "전립선암", "난소암", "방광암", "신장암", "식도암", "갑상선암", "담도암", "자궁암"]),
    ("종양학/항암", ["종양", "oncology", "항암", "면역항암", "암", "cancer", "종양학", "암질환", "항종양", "암 조기", "방사성의약품"]),

    # 신경계
    ("퇴행성뇌질환",["치매", "알츠하이머", "파킨슨", "퇴행성 뇌", "신경퇴행", "neurodegenerative"]),
    ("신경계/CNS",  ["신경계", "신경과", "cns", "뇌신경", "뇌졸중", "척수", "간질", "뇌질환", "신경재생", "신경종양", "신경독성", "neurology", "뇌·신경"]),
    ("정신건강",    ["정신", "우울", "불안", "조현병", "adhd", "자폐", "멘탈", "공황", "인지", "치매 예방", "신경발달", "psychiatry", "웰니스", "수면"]),

    # 심혈관/대사
    ("심혈관",      ["심혈관", "심장", "부정맥", "심부전", "동맥", "혈관", "뇌졸중", "심근", "cardio", "혈행"]),
    ("대사질환",    ["대사", "당뇨", "비만", "지방간", "고혈압", "고지혈", "인슐린", "ketone", "mash", "내분비"]),

    # 면역/자가면역
    ("자가면역/염증",["자가면역", "류마티스", "크론", "루푸스", "섬유증", "섬유화", "염증성 장", "건선", "autoimmune", "염증질환", "알레르기", "호흡기알레르기"]),

    # 감염병
    ("감염질환",    ["감염", "항바이러스", "항생제", "바이러스", "세균", "결핵", "항균", "infectious", "감염병", "백신", "vaccine", "항감염"]),

    # 근골격계
    ("근골격계",    ["근골격", "관절", "척추", "정형외과", "근감소", "골다공증", "연골", "근이영양증", "근염", "재활", "통증", "근육"]),

    # 안과
    ("안과",        ["안과", "망막", "눈", "시력", "ophthalm", "안질환", "시기능", "안보건"]),

    # 소화기
    ("소화기/간",   ["소화기", "간질환", "간암", "간", "장", "위", "대장", "소장", "소화", "hepat", "장질환", "소화기계"]),

    # 호흡기
    ("호흡기",      ["호흡기", "폐", "천식", "copd", "폐섬유", "기관지", "폐암 진단"]),

    # 피부
    ("피부/탈모",   ["피부", "탈모", "두피", "derma", "피부과", "창상", "상처", "피부재생", "피부질환", "피부암", "스킨"]),

    # 여성/비뇨기
    ("여성/비뇨기", ["여성", "비뇨기", "난임", "자궁", "생식", "펨테크", "전립선", "방광"]),

    # 안과
    ("치과/구강",   ["치과", "구강", "치주", "임플란트", "교정", "dental"]),

    # 뷰티/화장품
    ("뷰티/화장품", ["화장품", "뷰티", "미용", "코스메", "cosmetic", "스킨케어", "안티에이징", "미백", "보습"]),

    # 건강기능식품/영양
    ("건강기능식품",["건강기능식품", "영양제", "프로바이오틱스", "식품", "영양", "메디푸드", "건강식품", "개별인정형"]),

    # 반려동물/동물
    ("반려동물/동물의약품", ["반려동물", "동물", "수의", "펫", "가축", "동물의약품", "동물용"]),

    # 디지털헬스/플랫폼
    ("디지털헬스/플랫폼", ["디지털 헬스", "디지털헬스", "플랫폼", "임상시험", "데이터", "영상의학", "방사선", "헬스케어 플랫폼", "cro", "신약개발"]),
]

def get_disease_group(area_str: str) -> str:
    """치료영역 문자열을 상위 카테고리로 매핑."""
    if not area_str or str(area_str).strip() in ("", "nan"):
        return "기타"
    a = str(area_str).lower()
    for group_name, keywords in DISEASE_GROUP_MAP:
        for kw in keywords:
            if kw.lower() in a:
                return group_name
    return "기타"

# ============================================================
# 모달리티 그룹핑 매핑
# ============================================================
MODALITY_GROUP_MAP = {
    # 저분자 / 합성신약
    "저분자": "저분자/합성신약",
    "소분자": "저분자/합성신약",
    "small molecule": "저분자/합성신약",
    "합성신약": "저분자/합성신약",
    "복합신약": "저분자/합성신약",
    "chemical": "저분자/합성신약",
    "protac": "저분자/합성신약",
    "tpd": "저분자/합성신약",
    "molecular glue": "저분자/합성신약",
    "mgd": "저분자/합성신약",
    "펩타이드": "저분자/합성신약",
    "peptidomimetic": "저분자/합성신약",
    "aso": "저분자/합성신약",
    "antisense": "저분자/합성신약",
    "올리고핵산": "저분자/합성신약",

    # 항체 / ADC
    "항체": "항체/ADC",
    "단일클론항체": "항체/ADC",
    "단클론항체": "항체/ADC",
    "이중항체": "항체/ADC",
    "이중특이항체": "항체/ADC",
    "bispecific": "항체/ADC",
    "adc": "항체/ADC",
    "antibody": "항체/ADC",
    "mab": "항체/ADC",
    "pdc": "항체/ADC",
    "t세포인게이저": "항체/ADC",
    "융합단백질": "항체/ADC",
    "재조합 단백질": "항체/ADC",
    "fc 융합": "항체/ADC",

    # 세포치료제
    "세포치료": "세포치료제",
    "car-t": "세포치료제",
    "car-nk": "세포치료제",
    "nk세포": "세포치료제",
    "nk 세포": "세포치료제",
    "줄기세포": "세포치료제",
    "배양 적혈구": "세포치료제",
    "대식세포": "세포치료제",

    # 유전자치료제
    "유전자치료": "유전자치료제",
    "유전자 치료": "유전자치료제",
    "gene therapy": "유전자치료제",
    "aav": "유전자치료제",
    "렌티바이러스": "유전자치료제",
    "레트로바이러스": "유전자치료제",
    "oncolytic": "유전자치료제",
    "암용해바이러스": "유전자치료제",
    "mrna": "유전자치료제",
    "sirna": "유전자치료제",
    "crispr": "유전자치료제",
    "유전자 편집": "유전자치료제",
    "유전자세포": "유전자치료제",
    "세포유전자": "유전자치료제",
    "lncrna": "유전자치료제",
    "비암호화rna": "유전자치료제",
    "grna": "유전자치료제",

    # 백신
    "백신": "백신",
    "vaccine": "백신",
    "vlp": "백신",
    "불활화백신": "백신",
    "cancer vaccine": "백신",
    "암 백신": "백신",
    "암백신": "백신",
    "치료용 암 백신": "백신",
    "플라스미드 dna 백신": "백신",

    # 마이크로바이옴 / 생균제
    "마이크로바이옴": "마이크로바이옴/생균제",
    "lbp": "마이크로바이옴/생균제",
    "live biotherapeutic": "마이크로바이옴/생균제",
    "프로바이오틱스": "마이크로바이옴/생균제",
    "포스트바이오틱스": "마이크로바이옴/생균제",
    "미생물제제": "마이크로바이옴/생균제",
    "박테리오파지": "마이크로바이옴/생균제",
    "생균치료제": "마이크로바이옴/생균제",
    "생균 의약품": "마이크로바이옴/생균제",
    "bacteria": "마이크로바이옴/생균제",

    # 약물전달시스템 (DDS) / 나노
    "dds": "DDS/나노의약품",
    "나노입자": "DDS/나노의약품",
    "나노전달": "DDS/나노의약품",
    "나노소재": "DDS/나노의약품",
    "나노의약품": "DDS/나노의약품",
    "리포좀": "DDS/나노의약품",
    "lnp": "DDS/나노의약품",
    "나노제제": "DDS/나노의약품",
    "마이크로스피어": "DDS/나노의약품",
    "microsphere": "DDS/나노의약품",
    "엑소좀": "DDS/나노의약품",
    "exosome": "DDS/나노의약품",
    "ev(": "DDS/나노의약품",
    "ev 기반": "DDS/나노의약품",
    "약물전달": "DDS/나노의약품",
    "하이드로겔": "DDS/나노의약품",
    "하이드로젤": "DDS/나노의약품",
    "경피전달": "DDS/나노의약품",
    "마이크로니들": "DDS/나노의약품",

    # 체외진단 / IVD
    "체외진단": "체외진단(IVD)",
    "ivd": "체외진단(IVD)",
    "분자진단": "체외진단(IVD)",
    "진단키트": "체외진단(IVD)",
    "액체생검": "체외진단(IVD)",
    "ngs": "체외진단(IVD)",
    "pcr": "체외진단(IVD)",
    "poct": "체외진단(IVD)",
    "바이오센서": "체외진단(IVD)",
    "lfia": "체외진단(IVD)",
    "신속진단": "체외진단(IVD)",

    # 의료기기
    "의료기기": "의료기기",
    "웨어러블": "의료기기",
    "organ-on": "의료기기",
    "오가노이드": "의료기기",
    "organ on": "의료기기",
    "임플란트": "의료기기",
    "전자약": "의료기기",
    "디바이스": "의료기기",
    "electroceutical": "의료기기",

    # AI / 디지털헬스 / 소프트웨어
    "ai 소프트웨어": "AI/디지털헬스",
    "ai소프트웨어": "AI/디지털헬스",
    "디지털 헬스": "AI/디지털헬스",
    "디지털헬스": "AI/디지털헬스",
    "디지털치료": "AI/디지털헬스",
    "dtx": "AI/디지털헬스",
    "samd": "AI/디지털헬스",
    "saas": "AI/디지털헬스",
    "소프트웨어": "AI/디지털헬스",
    "플랫폼": "AI/디지털헬스",
    "모바일 앱": "AI/디지털헬스",
    "딥러닝": "AI/디지털헬스",
    "ai/ml": "AI/디지털헬스",
    "ai 기반": "AI/디지털헬스",

    # 화장품 / 기능성소재
    "화장품": "화장품/기능성소재",
    "코스메슈티컬": "화장품/기능성소재",
    "cosmeceutical": "화장품/기능성소재",
    "기능성 화장품": "화장품/기능성소재",
    "건강기능식품": "화장품/기능성소재",
    "천연물": "화장품/기능성소재",
    "기능성 소재": "화장품/기능성소재",
    "개별인정형": "화장품/기능성소재",

    # 플랫폼 / 연구도구
    "플랫폼 기술": "플랫폼/연구도구",
    "바이오파운드리": "플랫폼/연구도구",
    "크로마토그래피": "플랫폼/연구도구",
    "멤브레인 필터": "플랫폼/연구도구",
    "자동화 로봇": "플랫폼/연구도구",
    "cro": "플랫폼/연구도구",
    "스크리닝": "플랫폼/연구도구",
}

def get_modality_group(modality_str: str) -> str:
    """모달리티 문자열을 상위 카테고리로 매핑."""
    if not modality_str:
        return "기타"
    m = modality_str.lower()
    for keyword, group in MODALITY_GROUP_MAP.items():
        if keyword.lower() in m:
            return group
    return "기타"

# 회사 단위로 그룹핑 (캐싱)
@st.cache_data
def group_by_company(df):
    groups = {}
    for _, row in df.iterrows():
        name = row.get("회사명", "")
        if not name:
            continue
        if name not in groups:
            groups[name] = {
                "info": row,
                "pipelines": []
            }
        # 파이프라인 정보 추가
        pipeline = {
            "코드명":    row.get("리드에셋 코드명", ""),
            "개발단계":  row.get("리드에셋 개발단계", ""),
            "치료영역":  row.get("치료영역", ""),
            "모달리티":  row.get("모달리티", ""),
            "적응증":    row.get("세부 적응증", ""),
            "타깃":      row.get("핵심 타깃/MoA", ""),
        }
        if any(v for v in pipeline.values()):
            groups[name]["pipelines"].append(pipeline)
    return groups

# 모달리티/치료영역 그룹 컬럼 추가 (함수 정의 이후에 실행)
df["모달리티_그룹"] = df["모달리티"].apply(get_modality_group)
df["치료영역_그룹"] = df["치료영역"].apply(get_disease_group)

# ============================================================
# 스타일
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');
html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }

.main-header {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    color: white; padding: 1.75rem 2rem; border-radius: 12px; margin-bottom: 1.5rem;
}
.main-header h1 { font-size: 22px; font-weight: 700; margin: 0 0 4px; }
.main-header p  { font-size: 13px; opacity: 0.7; margin: 0; }

.metric-card {
    background: white; border: 1px solid #e8ecf0;
    border-radius: 10px; padding: 1rem 1.25rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}
.metric-card .label { font-size: 11px; color: #8a9bb0; margin-bottom: 4px; font-weight: 500; }
.metric-card .value { font-size: 26px; font-weight: 700; color: #1a2332; }

.company-row {
    background: white; border: 1px solid #e8ecf0;
    border-radius: 10px; padding: 1.1rem 1.4rem;
    margin-bottom: 10px;
}
.company-name { font-size: 15px; font-weight: 700; color: #1a2332; }
.company-summary { font-size: 12px; color: #6a7b8e; margin-top: 2px; line-height: 1.5; }

.badge {
    display: inline-block; font-size: 11px; font-weight: 500;
    padding: 2px 9px; border-radius: 20px; margin-right: 4px;
}
.badge-pre  { background:#e8f5e9; color:#2e7d32; }
.badge-1    { background:#e3f2fd; color:#1565c0; }
.badge-2    { background:#fff3e0; color:#e65100; }
.badge-3    { background:#f3e5f5; color:#6a1b9a; }
.badge-area { background:#f0f4ff; color:#3451b2; }
.badge-mod  { background:#f5f0ff; color:#5b21b6; }
.badge-gray { background:#f1f3f5; color:#5a6a7e; }

.pipeline-table { width:100%; border-collapse:collapse; margin-top:10px; font-size:12px; }
.pipeline-table th {
    background:#f8fafc; color:#6a7b8e; font-weight:500;
    padding:7px 10px; text-align:left;
    border-bottom:1px solid #e8ecf0; white-space:nowrap;
}
.pipeline-table td {
    padding:8px 10px; border-bottom:1px solid #f0f2f5;
    color:#1a2332; vertical-align:top; line-height:1.5;
}
.pipeline-table tr:last-child td { border-bottom: none; }

.info-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:10px; margin-top:12px; }
.info-item .info-label { font-size:11px; color:#8a9bb0; margin-bottom:2px; }
.info-item .info-value { font-size:13px; color:#1a2332; font-weight:500; }

div[data-testid="stSidebar"] { background:#f8fafc; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 헤더
# ============================================================
company_count = df["회사명"].nunique()
st.markdown(f"""
<div class="main-header">
    <h1>🧬 바이오 IR 데이터베이스</h1>
    <p>총 {company_count}개 기업 · {len(df)}개 파이프라인</p>
</div>
""", unsafe_allow_html=True)

# ============================================================
# 사이드바 필터
# ============================================================
with st.sidebar:
    st.markdown("### 🔍 필터")

    search = st.text_input("검색", placeholder="회사명, 적응증, 기술...")

    area_groups = ["전체"] + sorted([x for x in df["치료영역_그룹"].dropna().unique() if x not in ("", "기타")] + ["기타"])
    sel_area = st.selectbox("치료영역 (그룹)", area_groups)

    groups = ["전체"] + sorted([x for x in df["모달리티_그룹"].dropna().unique() if x not in ("", "기타")] + ["기타"])
    sel_modality = st.selectbox("모달리티 (그룹)", groups)

    stages = ["전체"] + sorted([x for x in df["리드에셋 개발단계"].dropna().unique() if x != ""])
    sel_stage = st.selectbox("개발단계", stages)

    countries = ["전체"] + sorted([x for x in df["국가"].dropna().unique() if x != ""])
    sel_country = st.selectbox("국가", countries)

    st.markdown("---")
    if st.button("🔄 초기화", use_container_width=True):
        st.rerun()

# ============================================================
# 필터링
# ============================================================
filtered = df.copy()

if search:
    mask = (
        filtered["회사명"].str.contains(search, na=False, case=False) |
        filtered.get("세부 적응증",       pd.Series(dtype=str)).str.contains(search, na=False, case=False) |
        filtered.get("주요사업 한줄요약",  pd.Series(dtype=str)).str.contains(search, na=False, case=False) |
        filtered.get("핵심 타깃/MoA",     pd.Series(dtype=str)).str.contains(search, na=False, case=False) |
        filtered.get("모달리티",           pd.Series(dtype=str)).str.contains(search, na=False, case=False)
    )
    filtered = filtered[mask]

if sel_area     != "전체": filtered = filtered[filtered["치료영역_그룹"] == sel_area]
if sel_modality != "전체": filtered = filtered[filtered["모달리티_그룹"] == sel_modality]
if sel_stage    != "전체": filtered = filtered[filtered["리드에셋 개발단계"] == sel_stage]
if sel_country  != "전체": filtered = filtered[filtered["국가"]             == sel_country]

company_groups = group_by_company(filtered)
filtered_company_count = len(company_groups)

# ============================================================
# 요약 지표
# ============================================================
col1, col2, col3, col4 = st.columns(4)
for col, (label, value) in zip(
    [col1, col2, col3, col4],
    [
        ("검색된 기업",    filtered_company_count),
        ("파이프라인 수",  len(filtered)),
        ("치료영역 그룹",  filtered["치료영역_그룹"].nunique()),
        ("모달리티 그룹",  filtered["모달리티_그룹"].nunique()),
    ]
):
    with col:
        st.markdown(f"""
        <div class="metric-card">
            <div class="label">{label}</div>
            <div class="value">{value}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================
# 탭
# ============================================================
tab1, tab2, tab3 = st.tabs(["📋 기업 리스트", "📊 차트 분석", "📄 전체 데이터"])

# ── 탭1: 기업 리스트 ─────────────────────────────────────────
with tab1:
    if not company_groups:
        st.info("조건에 맞는 기업이 없습니다.")
    else:
        st.markdown(f"**{filtered_company_count}개 기업** 표시 중")
        st.markdown("<br>", unsafe_allow_html=True)

        # 페이지당 50개씩 표시
        page_size = 50
        total_cos = len(filtered_companies)
        total_pages = max(1, (total_cos - 1) // page_size + 1)
        if total_pages > 1:
            page = st.number_input("페이지", min_value=1, max_value=total_pages, value=1, step=1)
            start = (page - 1) * page_size
            end   = start + page_size
            st.caption(f"{start+1}~{min(end, total_cos)} / 전체 {total_cos}개 기업")
            page_companies = dict(list(company_groups.items())[start:end])
        else:
            page_companies = company_groups

        for company_name, data_dict in page_companies.items():
            info      = data_dict["info"]
            pipelines = data_dict["pipelines"]

            # 파이프라인에서 대표 정보 수집
            stages_list    = [p["개발단계"] for p in pipelines if p["개발단계"]]
            areas_list     = list(dict.fromkeys([p["치료영역"] for p in pipelines if p["치료영역"]]))
            modality_list  = list(dict.fromkeys([p["모달리티"] for p in pipelines if p["모달리티"]]))

            stage_repr = stages_list[0] if stages_list else ""
            stage_cls  = (
                "badge-pre" if "전임상" in stage_repr or "pre" in stage_repr.lower() else
                "badge-1"   if "1상"    in stage_repr else
                "badge-2"   if "2상"    in stage_repr else
                "badge-3"   if "3상"    in stage_repr else
                "badge-gray"
            )

            summary   = str(info.get("주요사업 한줄요약", ""))
            invest    = str(info.get("누적 투자유치액", ""))
            investors = str(info.get("주요 투자사", ""))
            partner   = str(info.get("잠재 파트너사 / 고객사", ""))
            ceo       = str(info.get("대표이사", ""))
            homepage  = str(info.get("홈페이지", ""))
            patent    = f"등록 {info.get('특허 등록 건수','')}건 / 출원 {info.get('특허 출원 건수','')}건"
            country   = str(info.get("국가", ""))

            # 배지 HTML
            badges_html = ""
            if stage_repr:
                badges_html += f'<span class="badge {stage_cls}">{stage_repr}</span>'
            for a in areas_list[:2]:
                badges_html += f'<span class="badge badge-area">{a}</span>'
            for m in modality_list[:2]:
                badges_html += f'<span class="badge badge-mod">{m}</span>'
            if country:
                badges_html += f'<span class="badge badge-gray">{country}</span>'

            # expander 제목은 HTML 미지원 → 텍스트로 표시
            stage_text   = f"[{stage_repr}]" if stage_repr else ""
            area_text    = " · ".join(areas_list[:2])
            mod_text     = " · ".join(modality_list[:1])
            exp_title    = f"{company_name}  {stage_text}  {area_text}  {mod_text}"
            with st.expander(exp_title, expanded=False):

                # 배지 (expander 안에서는 HTML 사용 가능)
                st.markdown(badges_html, unsafe_allow_html=True)

                # 회사 요약
                if summary:
                    st.markdown(f"<div style='font-size:13px;color:#5a6a7e;margin-bottom:14px;line-height:1.7'>{summary}</div>", unsafe_allow_html=True)

                # 기업 기본 정보
                st.markdown("**기업 정보**")
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    st.markdown(f"<div style='font-size:11px;color:#8a9bb0'>대표이사</div><div style='font-size:13px;font-weight:500'>{ceo or '-'}</div>", unsafe_allow_html=True)
                with c2:
                    st.markdown(f"<div style='font-size:11px;color:#8a9bb0'>누적 투자유치액</div><div style='font-size:13px;font-weight:500'>{invest or '-'}</div>", unsafe_allow_html=True)
                with c3:
                    st.markdown(f"<div style='font-size:11px;color:#8a9bb0'>주요 투자사</div><div style='font-size:13px;font-weight:500'>{investors or '-'}</div>", unsafe_allow_html=True)
                with c4:
                    st.markdown(f"<div style='font-size:11px;color:#8a9bb0'>특허 현황</div><div style='font-size:13px;font-weight:500'>{patent}</div>", unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

                # 파이프라인 테이블
                if pipelines:
                    st.markdown(f"**파이프라인 ({len(pipelines)}개)**")
                    rows_html = ""
                    for p in pipelines:
                        s = p["개발단계"]
                        sc = (
                            "badge-pre" if "전임상" in s or "pre" in s.lower() else
                            "badge-1"   if "1상" in s else
                            "badge-2"   if "2상" in s else
                            "badge-3"   if "3상" in s else
                            "badge-gray"
                        )
                        rows_html += f"""
                        <tr>
                            <td><b>{p['코드명'] or '-'}</b></td>
                            <td><span class="badge {sc}">{s or '-'}</span></td>
                            <td>{p['치료영역'] or '-'}</td>
                            <td>{p['모달리티'] or '-'}</td>
                            <td>{p['적응증'] or '-'}</td>
                            <td>{p['타깃'] or '-'}</td>
                        </tr>"""

                    st.markdown(f"""
                    <table class="pipeline-table">
                        <thead>
                            <tr>
                                <th>코드명</th>
                                <th>개발단계</th>
                                <th>치료영역</th>
                                <th>모달리티</th>
                                <th>적응증</th>
                                <th>핵심 타깃/MoA</th>
                            </tr>
                        </thead>
                        <tbody>{rows_html}</tbody>
                    </table>
                    """, unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

                # 파트너사 & 홈페이지
                c5, c6 = st.columns(2)
                with c5:
                    st.markdown(f"<div style='font-size:11px;color:#8a9bb0'>잠재 파트너사 / 고객사</div><div style='font-size:13px'>{partner or '-'}</div>", unsafe_allow_html=True)
                with c6:
                    if homepage:
                        st.markdown(f"<div style='font-size:11px;color:#8a9bb0'>홈페이지</div><a href='{homepage}' target='_blank' style='font-size:13px'>{homepage}</a>", unsafe_allow_html=True)

# ── 탭2: 차트 분석 ──────────────────────────────────────────
with tab2:
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("**치료영역 분포**")
        area_counts = filtered["치료영역_그룹"].value_counts().reset_index()
        area_counts.columns = ["치료영역 그룹", "파이프라인 수"]
        if not area_counts.empty:
            fig = px.pie(area_counts, names="치료영역 그룹", values="파이프라인 수",
                         color_discrete_sequence=px.colors.qualitative.Set3, hole=0.4)
            fig.update_layout(margin=dict(t=10,b=10,l=10,r=10), height=340,
                              font_family="Noto Sans KR")
            st.plotly_chart(fig, width='stretch')

    with c2:
        st.markdown("**모달리티 분포**")
        mod_counts = filtered["모달리티_그룹"].value_counts().reset_index()
        mod_counts.columns = ["모달리티 그룹", "파이프라인 수"]
        if not mod_counts.empty:
            fig2 = px.bar(mod_counts, x="파이프라인 수", y="모달리티 그룹", orientation="h",
                          color_discrete_sequence=["#2c5364"])
            fig2.update_layout(margin=dict(t=10,b=10,l=10,r=10), height=380,
                               font_family="Noto Sans KR", yaxis_title="", xaxis_title="파이프라인 수")
            st.plotly_chart(fig2, width='stretch')

    st.markdown("**개발단계 분포**")
    stage_counts = filtered["리드에셋 개발단계"].value_counts().reset_index()
    stage_counts.columns = ["개발단계", "기업수"]
    if not stage_counts.empty:
        fig3 = px.bar(stage_counts, x="개발단계", y="기업수",
                      color_discrete_sequence=["#203a43"])
        fig3.update_layout(margin=dict(t=10,b=10,l=10,r=10), height=280,
                           font_family="Noto Sans KR", xaxis_title="", yaxis_title="기업 수")
        st.plotly_chart(fig3, width='stretch')

# ── 탭3: 전체 데이터 ────────────────────────────────────────
with tab3:
    show_cols = [c for c in [
        "회사명", "국가", "치료영역", "모달리티", "리드에셋 개발단계",
        "세부 적응증", "잠재 파트너사 / 고객사",
        "특허 등록 건수", "특허 출원 건수",
        "누적 투자유치액", "주요 투자사", "파싱일자"
    ] if c in filtered.columns]

    st.dataframe(filtered[show_cols], width='stretch', height=500)

    csv = filtered.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
    st.download_button("⬇️ 현재 필터 결과 다운로드 (CSV)", csv, "ir_filtered.csv", "text/csv", use_container_width=False)
