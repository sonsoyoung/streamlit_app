import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px
import math
import os

# Page Config
st.set_page_config(
    page_title="서울시 공영주차장 스마트 안내 서비스",
    page_icon="🅿️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.3rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

# 1. Robust Data Loading Function
@st.cache_data
def load_data():
    # app.py 가 있는 경로 기준으로 파일 탐색
    current_dir = os.path.dirname(os.path.abspath(__file__))
    target_filename = "서울시 공영주차장 안내 정보.csv"
    file_path = os.path.join(current_dir, target_filename)
    
    # 1차 시도: 지정된 파일명 탐색
    if not os.path.exists(file_path):
        # 2차 시도: 현재 디렉토리 또는 하위 디렉토리의 첫 번째 csv 파일 탐색
        csv_candidates = [f for f in os.listdir(current_dir) if f.endswith('.csv')]
        if csv_candidates:
            file_path = os.path.join(current_dir, csv_candidates[0])
        else:
            st.error(f"❌ '{target_filename}' 파일을 찾을 수 없습니다. GitHub 저장소 루트에 CSV 파일이 올바르게 업로드되었는지 확인해 주세요.")
            st.stop()
            
    # 한국어 CSV 인코딩 시도 (CP949 -> EUC-KR -> UTF-8 순)
    df = None
    encodings = ['cp949', 'euc-kr', 'utf-8-sig', 'utf-8']
    
    for enc in encodings:
        try:
            df = pd.read_csv(file_path, encoding=enc)
            break
        except Exception:
            continue
            
    if df is None:
        st.error("❌ CSV 파일을 읽는 데 실패했습니다 (인코딩 오류). 파일 형식을 확인해 주세요.")
        st.stop()
        
    # Extract Gu from '주소'
    if '주소' in df.columns:
        df['자치구'] = df['주소'].astype(str).str.extract(r'([\uac00-\ud7a3]+구)')
        df['자치구'] = df['자치구'].fillna('기타')
    else:
        df['자치구'] = '기타'
        
    # Fill defaults for numerical features
    num_cols = ['기본 주차 요금', '기본 주차 시간(분 단위)', '추가 단위 요금', '추가 단위 시간(분 단위)', '총 주차면', '위도', '경도']
    for c in num_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
        else:
            df[c] = 0
            
    # Clean Lat/Lng for map rendering
    df['위도_valid'] = (df['위도'] >= 37.3) & (df['위도'] <= 37.7)
    df['경도_valid'] = (df['경도'] >= 126.7) & (df['경도'] <= 127.3)
    
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"데이터 로딩 중 예외가 발생했습니다: {e}")
    st.stop()

# Header
st.markdown('<div class="main-header">🅿️ 서울시 공영주차장 스마트 안내 서비스</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">서울시 내 공영주차장 위치, 지도 시각화, 요금 계산기 및 최저가/랜덤 추천 서비스</div>', unsafe_allow_html=True)

# Sidebar Filters
st.sidebar.header("🔍 검색 및 필터 옵션")

# 1. District Filter
gu_list = ["전체"] + sorted([g for g in df['자치구'].unique() if g != '기타']) + ["기타"]
selected_gu = st.sidebar.selectbox("자치구 선택", gu_list)

# 2. Type Filter
type_col = '주차장 종류명' if '주차장 종류명' in df.columns else '주차장 종류'
type_list = ["전체"] + sorted([t for t in df[type_col].dropna().unique()]) if type_col in df.columns else ["전체"]
selected_type = st.sidebar.selectbox("주차장 종류", type_list)

# 3. Keyword Search
search_kw = st.sidebar.text_input("주차장명 / 주소 검색어", "")

# Apply Filters
filtered_df = df.copy()

if selected_gu != "전체":
    filtered_df = filtered_df[filtered_df['자치구'] == selected_gu]

if selected_type != "전체" and type_col in filtered_df.columns:
    filtered_df = filtered_df[filtered_df[type_col] == selected_type]

if search_kw:
    filtered_df = filtered_df[
        filtered_df['주차장명'].astype(str).str.contains(search_kw, case=False) | 
        filtered_df['주소'].astype(str).str.contains(search_kw, case=False)
    ]

# Summary Cards
col1, col2, col3, col4 = st.columns(4)
col1.metric("검색된 주차장", f"{len(filtered_df):,} 개")

avg_fee = filtered_df[filtered_df['기본 주차 요금'] > 0]['기본 주차 요금'].mean() if not filtered_df.empty else 0
col2.metric("평균 기본 요금", f"{int(avg_fee):,} 원" if avg_fee > 0 else "N/A")

total_spaces = filtered_df['총 주차면'].sum() if '총 주차면' in filtered_df.columns else 0
col3.metric("총 주차면수", f"{int(total_spaces):,} 면")
col4.metric("선택한 자치구", selected_gu)

st.markdown("---")

# Navigation Tabs
tab1, tab2, tab3, tab4 = st.tabs(["🗺️ 지도 및 목록", "📊 통계 분석", "💰 요금 계산기", "🎯 맞춤 추천"])

# ==================== TAB 1: Map & Data Table ====================
with tab1:
    st.subheader("📍 주차장 위치 지도")
    
    map_df = filtered_df[filtered_df['위도_valid'] & filtered_df['경도_valid']]
    
    if map_df.empty:
        st.info("지도상에 표시할 위치(위도/경도) 정보가 있는 주차장이 없습니다.")
    else:
        center_lat = map_df['위도'].mean()
        center_lng = map_df['경도'].mean()
        
        m = folium.Map(location=[center_lat, center_lng], zoom_start=12 if selected_gu == "전체" else 14)
        
        for idx, row in map_df.head(150).iterrows():
            base_f = int(row['기본 주차 요금'])
            base_t = int(row['기본 주차 시간(분 단위)'])
            
            popup_html = f"""
            <div style="width:210px;">
                <b>{row['주차장명']}</b><br>
                <b>주소:</b> {row['주소']}<br>
                <b>기본요금:</b> {base_f:,}원 ({base_t}분 기준)<br>
                <b>주차면수:</b> {int(row.get('총 주차면', 0))}면<br>
                <b>전화:</b> {row.get('전화번호', '정보없음')}
            </div>
            """
            folium.Marker(
                location=[row['위도'], row['경도']],
                popup=folium.Popup(popup_html, max_width=250),
                tooltip=row['주차장명'],
                icon=folium.Icon(color="blue", icon="info-sign")
            ).add_to(m)
            
        st_folium(m, width=1100, height=480)
        
    st.subheader("📋 공영주차장 목록")
    show_cols = [c for c in ['주차장명', '자치구', '주차장 종류명', '유무료구분명', '기본 주차 요금', '기본 주차 시간(분 단위)', '추가 단위 요금', '추가 단위 시간(분 단위)', '총 주차면', '전화번호', '주소'] if c in filtered_df.columns]
    st.dataframe(filtered_df[show_cols], use_container_width=True)
    
    csv_bytes = filtered_df[show_cols].to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
    st.download_button(
        label="📥 검색 결과 CSV 다운로드",
        data=csv_bytes,
        file_name=f"seoul_parking_{selected_gu}.csv",
        mime="text/csv"
    )

# ==================== TAB 2: Charts ====================
with tab2:
    st.subheader("📊 서울시 공영주차장 통계")
    
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown("##### 🏢 자치구별 주차장 수")
        gu_counts = df[df['자치구'] != '기타']['자치구'].value_counts().reset_index()
        gu_counts.columns = ['자치구', '주차장수']
        fig1 = px.bar(gu_counts, x='자치구', y='주차장수', color='주차장수', color_continuous_scale='Blues')
        st.plotly_chart(fig1, use_container_width=True)
        
    with c2:
        st.markdown("##### 🚗 주차장 종류별 비율")
        if '주차장 종류명' in df.columns:
            kind_counts = df['주차장 종류명'].value_counts().reset_index()
            kind_counts.columns = ['종류', '개수']
            fig2 = px.pie(kind_counts, names='종류', values='개수', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig2, use_container_width=True)
            
    st.markdown("##### 💸 자치구별 평균 기본 주차요금")
    gu_fee = df[df['기본 주차 요금'] > 0].groupby('자치구')['기본 주차 요금'].mean().reset_index()
    gu_fee.columns = ['자치구', '평균기본요금']
    gu_fee['평균기본요금'] = gu_fee['평균기본요금'].round(0)
    fig3 = px.bar(gu_fee.sort_values('평균기본요금', ascending=False), x='자치구', y='평균기본요금', color='평균기본요금', color_continuous_scale='Reds')
    st.plotly_chart(fig3, use_container_width=True)

# ==================== TAB 3: Fee Calculator ====================
with tab3:
    st.subheader("💰 주차요금 예상 계산기")
    st.write("주차장을 선택하고 예정 이용 시간을 입력하시면 예상 금액을 자동 계산합니다.")
    
    calc_col1, calc_col2 = st.columns([2, 1])
    
    target_df = filtered_df if not filtered_df.empty else df
    
    with calc_col1:
        selected_parking = st.selectbox("주차장 선택", options=target_df['주차장명'].unique())
        p_info = target_df[target_df['주차장명'] == selected_parking].iloc[0]
        
    with calc_col2:
        use_time = st.number_input("이용 예정 시간 (분)", min_value=5, max_value=1440, value=60, step=10)
        
    base_fee = float(p_info['기본 주차 요금'])
    base_time = float(p_info['기본 주차 시간(분 단위)']) if p_info['기본 주차 시간(분 단위)'] > 0 else 5.0
    add_fee = float(p_info['추가 단위 요금'])
    add_time = float(p_info['추가 단위 시간(분 단위)']) if p_info['추가 단위 시간(분 단위)'] > 0 else 5.0
    
    if use_time <= base_time:
        est_fee = base_fee
    else:
        extra_min = use_time - base_time
        extra_units = math.ceil(extra_min / add_time) if add_time > 0 else 0
        est_fee = base_fee + (extra_units * add_fee)
        
    st.info(f"📍 **선택한 주차장:** {p_info['주차장명']} | **주소:** {p_info['주소']}")
    
    r1, r2, r3 = st.columns(3)
    r1.metric("기본요금 조건", f"{int(base_fee):,}원 / {int(base_time)}분")
    r2.metric("추가요금 조건", f"{int(add_fee):,}원 / {int(add_time)}분당" if add_fee > 0 else "추가요금 없음")
    r3.metric("💡 총 예상 주차요금", f"{int(est_fee):,} 원", delta=f"{use_time}분 이용 기준")

# ==================== TAB 4: Recommendations ====================
with tab4:
    st.subheader("🎯 맞춤 주차장 추천")
    
    rec_t1, rec_t2 = st.tabs(["💵 최저가 주차장 TOP 5", "🎲 오늘 어디 댈까? 랜덤 추천"])
    
    with rec_t1:
        st.write(f"현재 선택된 자치구 (**{selected_gu}**) 에서 기본 요금이 가장 저렴한 공영주차장입니다.")
        
        cheap_df = filtered_df[filtered_df['기본 주차 요금'] > 0].sort_values(
            by=['기본 주차 요금', '기본 주차 시간(분 단위)'], 
            ascending=[True, False]
        ).head(5)
        
        if cheap_df.empty:
            st.warning("선택 조건 내에 유료 요금 정보가 등록된 주차장이 없습니다.")
        else:
            for idx, r in cheap_df.reset_index(drop=True).iterrows():
                b_fee = int(r['기본 주차 요금'])
                b_time = int(r['기본 주차 시간(분 단위)'])
                a_fee = int(r['추가 단위 요금'])
                a_time = int(r['추가 단위 시간(분 단위)'])
                
                with st.expander(f"TOP {idx+1}. {r['주차장명']} — 기본 {b_fee:,}원 ({b_time}분)"):
                    st.write(f"- **주소:** {r['주소']}")
                    st.write(f"- **추가 요금:** {a_time}분당 {a_fee:,}원")
                    st.write(f"- **총 주차면:** {int(r.get('총 주차면', 0))}면")
                    st.write(f"- **전화번호:** {r.get('전화번호', '정보없음')}")
                    
    with rec_t2:
        st.write("주차 장소를 고민 중이시라면 아래 버튼을 눌러 조건에 어울리는 주차장을 랜덤으로 뽑아보세요.")
        if st.button("🎲 랜덤 주차장 추천받기"):
            if not filtered_df.empty:
                pick = filtered_df.sample(n=1).iloc[0]
                st.balloons()
                st.success(f"🎉 **추천 주차장:** {pick['주차장명']}")
                st.write(f"📍 **위치:** {pick['주소']} ({pick['자치구']})")
                st.write(f"💵 **기본 요금:** {int(pick['기본 주차 요금']):,}원 / {int(pick['기본 주차 시간(분 단위)'])}분")
                st.write(f"📞 **전화번호:** {pick.get('전화번호', '정보없음')}")
            else:
                st.error("선택한 검색 조건에 맞는 주차장이 없습니다.")
