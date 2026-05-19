import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# ============================================================
# 설정
# ============================================================
st.set_page_config(
    page_title="헬스케어 IR 기술 검색",
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

    needed_cols = [
        "회사명", "국가", "설립연도", "기업단계", "임직원수",
        "대표이사", "주요사업 한줄요약", "홈페이지",
        "자본금", "누적 투자유치액", "현재 투자단계", "주요 투자사",
        "치료영역", "모달리티", "세부 적응증", "핵심 타깃/MoA",
        "기술 차별점 요약", "IP 리스크",
        "리드에셋 코드명", "리드에셋 개발단계",
        "잠재 파트너사 / 고객사",
        "특허 등록 건수", "특허 출원 건수", "PCT 출원 여부",
        "본사 주소", "파일명", "파싱일자"
    ]
    all_cols = pd.read_excel(data_path, nrows=0).columns.tolist()
    use_cols = [c for c in needed_cols if c in all_cols]
    df = pd.read_excel(data_path, usecols=use_cols)
    df = df.fillna("")
    return df

df = load_data()

# ============================================================
# 치료영역 그룹핑
# ============================================================
DISEASE_GROUP_MAP = [
    ("혈액암",          ["혈액암","백혈병","림프종","다발성골수종"]),
    ("고형암",          ["고형암","폐암","간암","췌장암","위암","대장암","유방암","전립선암","난소암"]),
    ("종양학/항암",     ["종양","oncology","항암","면역항암","암","cancer"]),
    ("퇴행성뇌질환",   ["치매","알츠하이머","파킨슨","퇴행성 뇌","신경퇴행"]),
    ("신경계/CNS",      ["신경계","신경과","cns","뇌신경","뇌졸중","뇌질환","neurology"]),
    ("정신건강",        ["정신","우울","불안","adhd","멘탈","공황","인지","수면","psychiatry","웰니스"]),
    ("심혈관",          ["심혈관","심장","부정맥","심부전","동맥","혈관","cardio"]),
    ("대사질환",        ["대사","당뇨","비만","지방간","고혈압","인슐린","내분비"]),
    ("자가면역/염증",   ["자가면역","류마티스","크론","섬유증","염증성 장","autoimmune","알레르기"]),
    ("감염질환",        ["감염","항바이러스","항생제","바이러스","결핵","항균","감염병","백신","vaccine"]),
    ("근골격계",        ["근골격","관절","척추","정형외과","근감소","골다공증","재활","통증"]),
    ("안과",            ["안과","망막","시력","ophthalm","안질환"]),
    ("소화기/간",       ["소화기","간질환","간","장","위","대장","hepat"]),
    ("호흡기",          ["호흡기","폐","천식","copd","폐섬유"]),
    ("피부/탈모",       ["피부","탈모","두피","derma","창상","스킨"]),
    ("여성/비뇨기",     ["여성","비뇨기","난임","자궁","펨테크","전립선"]),
    ("치과/구강",       ["치과","구강","치주","임플란트","dental"]),
    ("뷰티/화장품",     ["화장품","뷰티","미용","코스메","cosmetic","안티에이징"]),
    ("건강기능식품",    ["건강기능식품","영양제","프로바이오틱스","식품","개별인정형"]),
    ("반려동물/동물",   ["반려동물","동물","수의","펫","가축"]),
    ("디지털헬스",      ["디지털 헬스","디지털헬스","플랫폼","임상시험","영상의학","cro"]),
]

MODALITY_GROUP_MAP = {
    "저분자":"저분자/합성신약","소분자":"저분자/합성신약","small molecule":"저분자/합성신약",
    "합성신약":"저분자/합성신약","protac":"저분자/합성신약","tpd":"저분자/합성신약",
    "molecular glue":"저분자/합성신약","펩타이드":"저분자/합성신약","aso":"저분자/합성신약",
    "항체":"항체/ADC","단일클론항체":"항체/ADC","이중항체":"항체/ADC","adc":"항체/ADC",
    "antibody":"항체/ADC","mab":"항체/ADC","융합단백질":"항체/ADC","재조합 단백질":"항체/ADC",
    "세포치료":"세포치료제","car-t":"세포치료제","car-nk":"세포치료제",
    "nk세포":"세포치료제","줄기세포":"세포치료제",
    "유전자치료":"유전자치료제","유전자 치료":"유전자치료제","aav":"유전자치료제",
    "mrna":"유전자치료제","sirna":"유전자치료제","crispr":"유전자치료제",
    "백신":"백신","vaccine":"백신","vlp":"백신","불활화백신":"백신",
    "마이크로바이옴":"마이크로바이옴/생균제","lbp":"마이크로바이옴/생균제",
    "프로바이오틱스":"마이크로바이옴/생균제","박테리오파지":"마이크로바이옴/생균제",
    "dds":"DDS/나노의약품","나노입자":"DDS/나노의약품","리포좀":"DDS/나노의약품",
    "lnp":"DDS/나노의약품","엑소좀":"DDS/나노의약품","약물전달":"DDS/나노의약품",
    "마이크로니들":"DDS/나노의약품","하이드로겔":"DDS/나노의약품",
    "체외진단":"체외진단(IVD)","ivd":"체외진단(IVD)","분자진단":"체외진단(IVD)",
    "액체생검":"체외진단(IVD)","pcr":"체외진단(IVD)","ngs":"체외진단(IVD)",
    "의료기기":"의료기기","웨어러블":"의료기기","organ-on":"의료기기","오가노이드":"의료기기",
    "ai 소프트웨어":"AI/디지털헬스","디지털 헬스":"AI/디지털헬스","dtx":"AI/디지털헬스",
    "samd":"AI/디지털헬스","소프트웨어":"AI/디지털헬스","모바일 앱":"AI/디지털헬스",
    "화장품":"화장품/기능성소재","건강기능식품":"화장품/기능성소재","천연물":"화장품/기능성소재",
}

def get_disease_group(v):
    if not v or str(v).strip() in ("","nan"): return "기타"
    a = str(v).lower()
    for g, kws in DISEASE_GROUP_MAP:
        if any(k.lower() in a for k in kws): return g
    return "기타"

def get_modality_group(v):
    if not v: return "기타"
    m = str(v).lower()
    for k, g in MODALITY_GROUP_MAP.items():
        if k.lower() in m: return g
    return "기타"

df["치료영역_그룹"] = df["치료영역"].apply(get_disease_group)
df["모달리티_그룹"] = df["모달리티"].apply(get_modality_group)

# ============================================================
# 회사 단위 그룹핑
# ============================================================
@st.cache_data
def group_by_company(df):
    groups = {}
    for _, row in df.iterrows():
        name = str(row.get("회사명","")).strip()
        if not name: continue
        if name not in groups:
            groups[name] = {"info": row, "pipelines": []}
        p = {k: str(row.get(k,"")) for k in ["리드에셋 코드명","리드에셋 개발단계","치료영역","모달리티","세부 적응증","핵심 타깃/MoA","기술 차별점 요약"]}
        if any(v for v in p.values()):
            groups[name]["pipelines"].append(p)
    return groups

# ============================================================
# 스타일
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');
*{box-sizing:border-box}
html,body,[class*="css"]{font-family:'Noto Sans KR',sans-serif}

/* 헤더 */
.top-header{
    background:linear-gradient(135deg,#0d1b3e 0%,#1a3a6e 60%,#1e5799 100%);
    color:white;padding:1.5rem 2rem 1.2rem;margin-bottom:0;
}
.top-header h1{font-size:22px;font-weight:700;margin:0 0 4px;letter-spacing:-0.3px}
.top-header p{font-size:13px;opacity:.7;margin:0 0 12px}
.tag-row{display:flex;gap:8px;flex-wrap:wrap}
.tag-chip{background:rgba(255,255,255,.15);color:white;font-size:12px;font-weight:500;
    padding:4px 12px;border-radius:20px;border:1px solid rgba(255,255,255,.25)}

/* 탭 버튼 */
.tab-bar{background:#1a3a6e;padding:0 2rem;display:flex;gap:0;border-bottom:none}
.stTabs [data-baseweb="tab-list"]{background:#1a3a6e;gap:0;padding:0 1rem}
.stTabs [data-baseweb="tab"]{color:rgba(255,255,255,.6);font-size:14px;font-weight:500;
    padding:12px 20px;border-bottom:3px solid transparent}
.stTabs [aria-selected="true"]{color:white!important;border-bottom:3px solid white!important;background:transparent!important}

/* 사이드바 */
section[data-testid="stSidebar"]{background:#f8fafc;padding-top:0}
section[data-testid="stSidebar"] .block-container{padding:1rem}

.filter-section{margin-bottom:1.2rem}
.filter-title{font-size:12px;font-weight:600;color:#374151;margin-bottom:8px;text-transform:uppercase;letter-spacing:.5px}

/* 카드 */
.company-card{
    background:white;border:1.5px solid #e5e7eb;border-radius:10px;
    padding:1.25rem 1.5rem;margin-bottom:12px;
    transition:border-color .15s,box-shadow .15s;
}
.company-card:hover{border-color:#3b82f6;box-shadow:0 2px 12px rgba(59,130,246,.12)}
.company-card.needs-review{border-left:4px solid #f59e0b}

.card-header{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px}
.company-name-row{display:flex;align-items:center;gap:10px;flex-wrap:wrap}
.company-name{font-size:18px;font-weight:700;color:#111827}
.company-eng{font-size:13px;color:#9ca3af;font-weight:400}
.company-meta{font-size:12px;color:#9ca3af;margin-bottom:8px}
.company-summary{font-size:13px;color:#4b5563;line-height:1.65;margin-bottom:12px}

/* 배지 */
.badge{display:inline-flex;align-items:center;font-size:11px;font-weight:600;
    padding:3px 10px;border-radius:20px;margin-right:5px;margin-bottom:4px;white-space:nowrap}
.badge-pre{background:#ecfdf5;color:#059669;border:1px solid #a7f3d0}
.badge-1{background:#eff6ff;color:#1d4ed8;border:1px solid #bfdbfe}
.badge-2{background:#fff7ed;color:#c2410c;border:1px solid #fed7aa}
.badge-3{background:#f5f3ff;color:#6d28d9;border:1px solid #ddd6fe}
.badge-modality{background:#f0fdf4;color:#166534;border:1px solid #bbf7d0}
.badge-disease{background:#f0f9ff;color:#0369a1;border:1px solid #bae6fd}
.badge-tag{background:#f1f5f9;color:#475569;border:1px solid #e2e8f0}
.badge-review{background:#fffbeb;color:#92400e;border:1px solid #fde68a}
.badge-ok{background:#f0fdf4;color:#065f46;border:1px solid #a7f3d0}
.confidence{font-size:11px;color:#9ca3af;font-weight:500}

/* 파이프라인 테이블 */
.pipe-table{width:100%;border-collapse:collapse;font-size:12px;margin-top:10px}
.pipe-table th{background:#f8fafc;color:#6b7280;font-weight:600;
    padding:7px 10px;text-align:left;border-bottom:1.5px solid #e5e7eb;white-space:nowrap}
.pipe-table td{padding:8px 10px;border-bottom:1px solid #f3f4f6;color:#374151;vertical-align:top;line-height:1.5}
.pipe-table tr:last-child td{border-bottom:none}
.pipe-table tr:hover td{background:#fafbfc}

/* 인포 그리드 */
.info-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin:12px 0;
    padding:12px;background:#f8fafc;border-radius:8px}
.info-item .info-label{font-size:11px;color:#9ca3af;margin-bottom:3px;font-weight:500}
.info-item .info-value{font-size:13px;color:#111827;font-weight:500}

/* 구분선 */
.divider{border:none;border-top:1px solid #f3f4f6;margin:12px 0}

/* 메트릭 */
.metric-box{background:white;border:1px solid #e5e7eb;border-radius:8px;padding:14px 18px;text-align:center}
.metric-box .m-label{font-size:11px;color:#9ca3af;margin-bottom:4px;font-weight:500}
.metric-box .m-value{font-size:26px;font-weight:700;color:#111827}

/* IP 배지 */
.ip-row{display:flex;gap:8px;flex-wrap:wrap;margin-top:8px}
.ip-item{font-size:12px;background:#f8fafc;border:1px solid #e5e7eb;
    border-radius:6px;padding:4px 10px;color:#374151}
.ip-label{color:#9ca3af;font-size:11px;margin-right:4px}
</style>
""", unsafe_allow_html=True)

# ============================================================
# 필터링 (사이드바 제거, 좌측 컬럼으로)
# ============================================================
company_count = df["회사명"].nunique()

# 헤더
modal_groups = sorted(df["모달리티_그룹"].unique().tolist())
modal_counts = df["모달리티_그룹"].value_counts()

tag_html = ""
for g in [g for g in modal_groups if g != "기타"][:6]:
    cnt = modal_counts.get(g, 0)
    tag_html += f'<span class="tag-chip">{g} {cnt}</span>'

st.markdown(f"""
<div class="top-header">
  <h1>🧬 헬스케어 IR 기술 검색</h1>
  <p>제품 범주·발전 단계·질환군·투자자 테마 개념 태그를 조합해 연관 기업을 탐색합니다. 필터는 모두 함께 적용됩니다(조합 검색).</p>
  <div class="tag-row">{tag_html}<span class="tag-chip">총 {company_count}개 기업</span></div>
</div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["  🔍 기업 검색  ", "  📊 통계 분석  "])

with tab1:
    left, right = st.columns([1, 2.8])

    # ── 좌측 필터 패널 ──────────────────────────────────────
    with left:
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

        search = st.text_input("", placeholder="회사명 · 질환 · 기술 키워드",
                               label_visibility="collapsed")

        st.markdown("<div class='filter-title'>제품 범주</div>", unsafe_allow_html=True)
        mod_groups = sorted([g for g in df["모달리티_그룹"].unique() if g != "기타"])
        mod_counts_dict = df.drop_duplicates("회사명")["모달리티_그룹"].value_counts().to_dict()
        sel_modalities = []
        for g in mod_groups:
            cnt = mod_counts_dict.get(g, 0)
            if st.checkbox(f"{g}  **{cnt}**", key=f"mod_{g}"):
                sel_modalities.append(g)

        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
        st.markdown("<div class='filter-title'>발전 단계</div>", unsafe_allow_html=True)
        stage_vals = sorted([s for s in df["리드에셋 개발단계"].unique() if s])
        sel_stages = []
        stage_counts = df.drop_duplicates("회사명")["리드에셋 개발단계"].value_counts().to_dict()
        for s in stage_vals[:8]:
            cnt = stage_counts.get(s, 0)
            if st.checkbox(f"{s}  **{cnt}**", key=f"stg_{s}"):
                sel_stages.append(s)

        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
        st.markdown("<div class='filter-title'>질환군</div>", unsafe_allow_html=True)
        dis_groups = sorted([g for g in df["치료영역_그룹"].unique() if g != "기타"])
        dis_counts_dict = df.drop_duplicates("회사명")["치료영역_그룹"].value_counts().to_dict()
        sel_diseases = []
        for g in dis_groups:
            cnt = dis_counts_dict.get(g, 0)
            if st.checkbox(f"{g}  **{cnt}**", key=f"dis_{g}"):
                sel_diseases.append(g)

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        if st.button("🔄 필터 초기화", use_container_width=True):
            st.rerun()

    # ── 우측 결과 패널 ──────────────────────────────────────
    with right:
        # 필터 적용
        filtered = df.copy()
        if search:
            q = search.lower()
            mask = (
                filtered["회사명"].str.lower().str.contains(q, na=False) |
                filtered["세부 적응증"].str.lower().str.contains(q, na=False) |
                filtered["주요사업 한줄요약"].str.lower().str.contains(q, na=False) |
                filtered["모달리티"].str.lower().str.contains(q, na=False) |
                filtered["핵심 타깃/MoA"].str.lower().str.contains(q, na=False)
            )
            filtered = filtered[mask]
        if sel_modalities:
            filtered = filtered[filtered["모달리티_그룹"].isin(sel_modalities)]
        if sel_stages:
            filtered = filtered[filtered["리드에셋 개발단계"].isin(sel_stages)]
        if sel_diseases:
            filtered = filtered[filtered["치료영역_그룹"].isin(sel_diseases)]

        company_groups = group_by_company(filtered)
        total = len(company_groups)
        pipe_total = len(filtered)

        st.markdown(
            f"<div style='padding:10px 0 8px;font-size:13px;color:#6b7280'>"
            f"검색 결과 <b style='color:#111827'>{total}개 기업</b> / 전체 {company_count}개 &nbsp;·&nbsp; 파이프라인 {pipe_total}개"
            f"</div>", unsafe_allow_html=True)

        if not company_groups:
            st.info("조건에 맞는 기업이 없습니다.")
        else:
            # 페이지네이션
            page_size = 20
            total_pages = max(1, (total - 1) // page_size + 1)
            if total_pages > 1:
                page = st.number_input("페이지", min_value=1, max_value=total_pages, value=1, step=1)
            else:
                page = 1
            start = (page - 1) * page_size
            page_items = dict(list(company_groups.items())[start:start+page_size])

            for cname, d in page_items.items():
                info = d["info"]
                pipes = d["pipelines"]

                # 대표 정보
                stage  = str(pipes[0]["리드에셋 개발단계"]) if pipes else ""
                modal  = str(pipes[0]["모달리티"]) if pipes else ""
                area   = str(pipes[0]["치료영역"]) if pipes else ""
                summary = str(info.get("주요사업 한줄요약",""))
                invest  = str(info.get("누적 투자유치액",""))
                investors = str(info.get("주요 투자사",""))
                yr     = str(info.get("설립연도",""))
                loc    = str(info.get("본사 주소",""))
                emp    = str(info.get("임직원수",""))
                patent_reg = str(info.get("특허 등록 건수",""))
                patent_app = str(info.get("특허 출원 건수",""))
                pct    = str(info.get("PCT 출원 여부",""))
                partner= str(info.get("잠재 파트너사 / 고객사",""))

                stage_cls = (
                    "badge-pre" if any(x in stage for x in ["전임상","Pre","pre"]) else
                    "badge-1"   if "1상" in stage else
                    "badge-2"   if "2상" in stage else
                    "badge-3"   if "3상" in stage else
                    "badge-tag"
                )

                # 카드 HTML
                badges = ""
                if modal:
                    mg = get_modality_group(modal)
                    badges += f'<span class="badge badge-modality">{mg}</span>'
                if stage:
                    badges += f'<span class="badge {stage_cls}">{stage}</span>'
                if area:
                    dg = get_disease_group(area)
                    if dg != "기타":
                        badges += f'<span class="badge badge-disease">{dg}</span>'

                meta_parts = []
                if yr:   meta_parts.append(f"설립 {yr}")
                if loc:  meta_parts.append(loc[:20])
                if emp:  meta_parts.append(f"임직원 {emp}명")
                meta_str = " &nbsp;·&nbsp; ".join(meta_parts)

                ip_html = ""
                if patent_reg: ip_html += f'<span class="ip-item"><span class="ip-label">등록</span>{patent_reg}건</span>'
                if patent_app: ip_html += f'<span class="ip-item"><span class="ip-label">출원</span>{patent_app}건</span>'
                if pct:        ip_html += f'<span class="ip-item"><span class="ip-label">PCT</span>{pct}</span>'

                invest_html = ""
                if invest:    invest_html += f'<span class="ip-item"><span class="ip-label">투자유치</span>{invest}</span>'
                if investors: invest_html += f'<span class="ip-item"><span class="ip-label">투자사</span>{investors[:30]}</span>'

                with st.expander(f"**{cname}**　{stage}　{get_disease_group(area) if area else ''}　파이프라인 {len(pipes)}개", expanded=False):
                    # 헤더 배지 + 요약
                    st.markdown(f"""
                    <div style='margin-bottom:8px'>{badges}</div>
                    <div class='company-meta'>{meta_str}</div>
                    {"<div class='company-summary'>"+summary+"</div>" if summary else ""}
                    """, unsafe_allow_html=True)

                    # 인포 그리드
                    if invest_html or ip_html:
                        st.markdown(f"""
                        <div class='ip-row'>{invest_html}{ip_html}</div>
                        """, unsafe_allow_html=True)

                    # 파이프라인 테이블
                    if pipes:
                        st.markdown(f"<div style='margin-top:14px;font-size:12px;font-weight:600;color:#374151'>📋 파이프라인 ({len(pipes)}개)</div>", unsafe_allow_html=True)
                        rows_html = ""
                        for p in pipes:
                            s2 = p["리드에셋 개발단계"]
                            sc2 = ("badge-pre" if any(x in s2 for x in ["전임상","Pre","pre"]) else
                                   "badge-1" if "1상" in s2 else
                                   "badge-2" if "2상" in s2 else
                                   "badge-3" if "3상" in s2 else "badge-tag")
                            rows_html += f"""<tr>
                                <td><b>{p['리드에셋 코드명'] or '-'}</b></td>
                                <td><span class="badge {sc2}" style="font-size:10px">{s2 or '-'}</span></td>
                                <td>{p['치료영역'] or '-'}</td>
                                <td>{p['모달리티'] or '-'}</td>
                                <td>{p['세부 적응증'] or '-'}</td>
                                <td>{p['핵심 타깃/MoA'] or '-'}</td>
                            </tr>"""
                        st.markdown(f"""
                        <table class="pipe-table">
                          <thead><tr>
                            <th>코드명</th><th>개발단계</th><th>치료영역</th>
                            <th>모달리티</th><th>적응증</th><th>핵심 타깃/MoA</th>
                          </tr></thead>
                          <tbody>{rows_html}</tbody>
                        </table>""", unsafe_allow_html=True)

                    # 기술 차별점
                    tech = str(pipes[0].get("기술 차별점 요약","")) if pipes else ""
                    if tech:
                        st.markdown(f"""
                        <div style='margin-top:12px;padding:10px 12px;background:#f8fafc;border-radius:6px;border-left:3px solid #3b82f6'>
                          <span style='font-size:11px;font-weight:600;color:#3b82f6'>차별점</span>
                          <div style='font-size:12px;color:#374151;margin-top:4px;line-height:1.6'>{tech}</div>
                        </div>""", unsafe_allow_html=True)

                    # 파트너사
                    if partner:
                        st.markdown(f"""
                        <div style='margin-top:8px;font-size:12px;color:#6b7280'>
                          <span style='font-weight:600'>잠재 파트너사</span> &nbsp;{partner}
                        </div>""", unsafe_allow_html=True)

# ── 탭2: 통계 분석 ──────────────────────────────────────────
with tab2:
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**치료영역 분포**")
        ac = df["치료영역_그룹"].value_counts().reset_index()
        ac.columns = ["치료영역","수"]
        fig = px.pie(ac, names="치료영역", values="수",
                     color_discrete_sequence=px.colors.qualitative.Set3, hole=0.4)
        fig.update_layout(margin=dict(t=10,b=10,l=10,r=10), height=320, font_family="Noto Sans KR")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.markdown("**모달리티 분포**")
        mc = df["모달리티_그룹"].value_counts().reset_index()
        mc.columns = ["모달리티","수"]
        fig2 = px.bar(mc, x="수", y="모달리티", orientation="h",
                      color_discrete_sequence=["#1d4ed8"])
        fig2.update_layout(margin=dict(t=10,b=10,l=10,r=10), height=360,
                           font_family="Noto Sans KR", yaxis_title="", xaxis_title="파이프라인 수")
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("**개발단계 분포**")
    sc = df["리드에셋 개발단계"].value_counts().reset_index()
    sc.columns = ["개발단계","수"]
    fig3 = px.bar(sc.head(12), x="개발단계", y="수",
                  color_discrete_sequence=["#0d1b3e"])
    fig3.update_layout(margin=dict(t=10,b=10,l=10,r=10), height=280,
                       font_family="Noto Sans KR", xaxis_title="", yaxis_title="파이프라인 수")
    st.plotly_chart(fig3, use_container_width=True)
