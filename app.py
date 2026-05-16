import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
    df = pd.read_excel(data_path)
    df = df.fillna("")
    return df

df = load_data()

# ============================================================
# 스타일
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');

html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }

.main-header {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    color: white; padding: 2rem 2.5rem; border-radius: 12px;
    margin-bottom: 1.5rem;
}
.main-header h1 { font-size: 26px; font-weight: 700; margin: 0 0 4px; }
.main-header p  { font-size: 14px; opacity: 0.75; margin: 0; }

.metric-card {
    background: white; border: 1px solid #e8ecf0;
    border-radius: 10px; padding: 1.2rem 1.5rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.metric-card .label { font-size: 12px; color: #8a9bb0; margin-bottom: 4px; font-weight: 500; }
.metric-card .value { font-size: 28px; font-weight: 700; color: #1a2332; }

.company-card {
    background: white; border: 1px solid #e8ecf0;
    border-radius: 12px; padding: 1.25rem 1.5rem;
    margin-bottom: 12px; box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    transition: box-shadow 0.2s;
}
.company-card:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.1); }
.company-name { font-size: 16px; font-weight: 700; color: #1a2332; margin-bottom: 4px; }
.company-summary { font-size: 13px; color: #5a6a7e; margin-bottom: 10px; line-height: 1.6; }

.badge {
    display: inline-block; font-size: 11px; font-weight: 500;
    padding: 3px 10px; border-radius: 20px; margin-right: 5px; margin-bottom: 4px;
}
.badge-stage-pre  { background: #e8f5e9; color: #2e7d32; }
.badge-stage-1    { background: #e3f2fd; color: #1565c0; }
.badge-stage-2    { background: #fff3e0; color: #e65100; }
.badge-stage-3    { background: #f3e5f5; color: #6a1b9a; }
.badge-area       { background: #f0f4ff; color: #3451b2; }
.badge-modality   { background: #f5f0ff; color: #5b21b6; }

.info-row { display: flex; gap: 1.5rem; margin-top: 10px; padding-top: 10px; border-top: 1px solid #f0f2f5; }
.info-item .info-label { font-size: 11px; color: #8a9bb0; margin-bottom: 2px; }
.info-item .info-value { font-size: 13px; color: #1a2332; font-weight: 500; }

div[data-testid="stSidebar"] { background: #f8fafc; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 헤더
# ============================================================
st.markdown(f"""
<div class="main-header">
    <h1>🧬 바이오 IR 데이터베이스</h1>
    <p>총 {len(df)}개 기업 · {df['파싱일자'].max() if '파싱일자' in df.columns else ''} 기준</p>
</div>
""", unsafe_allow_html=True)

# ============================================================
# 사이드바 필터
# ============================================================
with st.sidebar:
    st.markdown("### 🔍 필터")

    search = st.text_input("검색", placeholder="회사명, 적응증, 기술...")

    areas = ["전체"] + sorted([x for x in df["치료영역"].dropna().unique() if x != ""])
    sel_area = st.selectbox("치료영역", areas)

    modalities = ["전체"] + sorted([x for x in df["모달리티"].dropna().unique() if x != ""])
    sel_modality = st.selectbox("모달리티", modalities)

    stages = ["전체"] + sorted([x for x in df["리드에셋 개발단계"].dropna().unique() if x != ""])
    sel_stage = st.selectbox("개발단계", stages)

    countries = ["전체"] + sorted([x for x in df["국가"].dropna().unique() if x != ""])
    sel_country = st.selectbox("국가", countries)

    st.markdown("---")
    if st.button("🔄 필터 초기화", use_container_width=True):
        st.rerun()

# ============================================================
# 필터링
# ============================================================
filtered = df.copy()

if search:
    mask = (
        filtered["회사명"].str.contains(search, na=False, case=False) |
        filtered.get("세부 적응증", pd.Series(dtype=str)).str.contains(search, na=False, case=False) |
        filtered.get("주요사업 한줄요약", pd.Series(dtype=str)).str.contains(search, na=False, case=False) |
        filtered.get("핵심 타깃/MoA", pd.Series(dtype=str)).str.contains(search, na=False, case=False)
    )
    filtered = filtered[mask]

if sel_area != "전체":
    filtered = filtered[filtered["치료영역"] == sel_area]
if sel_modality != "전체":
    filtered = filtered[filtered["모달리티"] == sel_modality]
if sel_stage != "전체":
    filtered = filtered[filtered["리드에셋 개발단계"] == sel_stage]
if sel_country != "전체":
    filtered = filtered[filtered["국가"] == sel_country]

# 회사 단위로 중복 제거 (파이프라인 여러 개인 경우 첫 행만)
filtered_companies = filtered.drop_duplicates(subset=["회사명"])

# ============================================================
# 요약 지표
# ============================================================
col1, col2, col3, col4 = st.columns(4)
metrics = [
    ("검색된 기업", len(filtered_companies)),
    ("치료영역 수", filtered["치료영역"].nunique()),
    ("모달리티 수", filtered["모달리티"].nunique()),
    ("전체 파이프라인", len(filtered)),
]
for col, (label, value) in zip([col1, col2, col3, col4], metrics):
    with col:
        st.markdown(f"""
        <div class="metric-card">
            <div class="label">{label}</div>
            <div class="value">{value}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================
# 탭 구성
# ============================================================
tab1, tab2, tab3 = st.tabs(["📋 기업 카드", "📊 차트 분석", "📄 전체 데이터"])

# ── 탭1: 기업 카드 ──────────────────────────────────────────
with tab1:
    if filtered_companies.empty:
        st.info("조건에 맞는 기업이 없습니다.")
    else:
        for _, row in filtered_companies.iterrows():
            stage = str(row.get("리드에셋 개발단계", ""))
            stage_cls = (
                "badge-stage-pre" if "전임상" in stage or "pre" in stage.lower() else
                "badge-stage-1"   if "1상"   in stage else
                "badge-stage-2"   if "2상"   in stage else
                "badge-stage-3"   if "3상"   in stage else
                "badge-stage-pre"
            )
            area     = str(row.get("치료영역", ""))
            modality = str(row.get("모달리티", ""))
            summary  = str(row.get("주요사업 한줄요약", ""))
            indication = str(row.get("세부 적응증", ""))
            partner  = str(row.get("잠재 파트너사 / 고객사", ""))
            patent   = f"등록 {row.get('특허 등록 건수','')}건 / 출원 {row.get('특허 출원 건수','')}건"
            ceo      = str(row.get("대표이사", ""))
            homepage = str(row.get("홈페이지", ""))

            with st.expander(f"**{row.get('회사명', '-')}**  |  {stage}  |  {area}", expanded=False):
                st.markdown(f"""
                <div style="margin-bottom:10px">
                    <span class="badge {stage_cls}">{stage}</span>
                    <span class="badge badge-area">{area}</span>
                    <span class="badge badge-modality">{modality}</span>
                </div>
                <div style="font-size:14px;color:#3a4a5c;margin-bottom:12px;line-height:1.7">{summary}</div>
                """, unsafe_allow_html=True)

                c1, c2, c3 = st.columns(3)
                with c1:
                    st.markdown("**적응증**")
                    st.markdown(f"<div style='font-size:13px;color:#5a6a7e'>{indication}</div>", unsafe_allow_html=True)
                with c2:
                    st.markdown("**잠재 파트너사**")
                    st.markdown(f"<div style='font-size:13px;color:#5a6a7e'>{partner if partner else '-'}</div>", unsafe_allow_html=True)
                with c3:
                    st.markdown("**특허 현황**")
                    st.markdown(f"<div style='font-size:13px;color:#5a6a7e'>{patent}</div>", unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                c4, c5, c6 = st.columns(3)
                with c4:
                    st.markdown("**대표이사**")
                    st.markdown(f"<div style='font-size:13px'>{ceo if ceo else '-'}</div>", unsafe_allow_html=True)
                with c5:
                    st.markdown("**홈페이지**")
                    if homepage:
                        st.markdown(f"<a href='{homepage}' target='_blank' style='font-size:13px'>{homepage}</a>", unsafe_allow_html=True)
                    else:
                        st.markdown("<div style='font-size:13px'>-</div>", unsafe_allow_html=True)
                with c6:
                    st.markdown("**누적 투자유치액**")
                    inv = str(row.get("누적 투자유치액", ""))
                    st.markdown(f"<div style='font-size:13px'>{inv if inv else '-'}</div>", unsafe_allow_html=True)

# ── 탭2: 차트 분석 ──────────────────────────────────────────
with tab2:
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("**치료영역 분포**")
        area_counts = filtered["치료영역"].value_counts().reset_index()
        area_counts.columns = ["치료영역", "기업수"]
        if not area_counts.empty:
            fig = px.pie(area_counts, names="치료영역", values="기업수",
                         color_discrete_sequence=px.colors.qualitative.Set3,
                         hole=0.4)
            fig.update_layout(margin=dict(t=10,b=10,l=10,r=10), height=300,
                              showlegend=True, font_family="Noto Sans KR")
            st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown("**모달리티 분포**")
        mod_counts = filtered["모달리티"].value_counts().reset_index()
        mod_counts.columns = ["모달리티", "기업수"]
        if not mod_counts.empty:
            fig2 = px.bar(mod_counts, x="기업수", y="모달리티", orientation="h",
                          color_discrete_sequence=["#2c5364"])
            fig2.update_layout(margin=dict(t=10,b=10,l=10,r=10), height=300,
                               font_family="Noto Sans KR", yaxis_title="",
                               xaxis_title="기업 수")
            st.plotly_chart(fig2, use_container_width=True)

    st.markdown("**개발단계 분포**")
    stage_order = ["전임상", "임상 1상", "임상 1/2상", "임상 2상", "임상 2/3상", "임상 3상", "허가"]
    stage_counts = filtered["리드에셋 개발단계"].value_counts().reset_index()
    stage_counts.columns = ["개발단계", "기업수"]
    if not stage_counts.empty:
        fig3 = px.bar(stage_counts, x="개발단계", y="기업수",
                      color_discrete_sequence=["#203a43"])
        fig3.update_layout(margin=dict(t=10,b=10,l=10,r=10), height=280,
                           font_family="Noto Sans KR", xaxis_title="", yaxis_title="기업 수")
        st.plotly_chart(fig3, use_container_width=True)

# ── 탭3: 전체 데이터 ────────────────────────────────────────
with tab3:
    show_cols = [c for c in [
        "회사명", "국가", "치료영역", "모달리티", "리드에셋 개발단계",
        "세부 적응증", "잠재 파트너사 / 고객사",
        "특허 등록 건수", "특허 출원 건수", "PCT 출원 여부",
        "누적 투자유치액", "주요 투자사", "파싱일자"
    ] if c in filtered.columns]

    st.dataframe(filtered[show_cols], use_container_width=True, height=500)

    csv = filtered.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
    st.download_button("⬇️ 현재 필터 결과 다운로드 (CSV)", csv,
                       "ir_filtered.csv", "text/csv")
