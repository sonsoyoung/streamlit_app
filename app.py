import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="MBTI 여행지 추천",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- MBTI 데이터 베이스 ---
MBTI_DESTINATIONS = {
    "ISTJ": {
        "destination": "독일 뮌헨",
        "category": "도시",
        "style": "휴양",
        "tag": "#체계적인 #역사와전통 #안정적인",
        "desc": "계획적이고 질서를 중시하는 ISTJ에게는 대중교통이 발달하고 정돈된 문화와 역사가 깊은 뮌헨이 제격입니다.",
        "spots": ["알테 피나코텍 미술관", "마리엔 광장", "영국 정원"],
        "tip": "철저한 사전 예약을 통해 분 단위 동선을 짜보세요!"
    },
    "ISFJ": {
        "destination": "일본 교토",
        "category": "도시",
        "style": "휴양",
        "tag": "#고즈넉한 #배려와차분함 #전통적인",
        "desc": "조용하고 따뜻한 환경을 선호하는 ISFJ는 고즈넉한 사찰과 조용한 골목길이 인상적인 교토에서 마음의 평온을 찾을 수 있습니다.",
        "spots": ["아라시야마 대나무 숲", "청수사(키요미즈데라)", "전통 료칸 숙박"],
        "tip": "조용한 료칸에서 정갈한 가이세키 요리를 즐겨보세요."
    },
    "INFJ": {
        "destination": "스위스 인터라켄",
        "category": "자연",
        "style": "휴양",
        "tag": "#사색하는 #장엄한자연 #조용한힐링",
        "desc": "깊은 생각과 영감을 찾아 떠나는 INFJ에게는 압도적인 대자연 속에서 혼자만의 시간을 가질 수 있는 스위스가 완벽합니다.",
        "spots": ["융프라우요흐", "툰 호수 유람선", "아이거 트레일 산책"],
        "tip": "노트와 펜을 챙겨 알프스를 바라보며 여행 일기를 써보세요."
    },
    "INTJ": {
        "destination": "영국 런던",
        "category": "도시",
        "style": "휴양",
        "tag": "#지적탐구 #박물관투어 #독립적인",
        "desc": "지적 호기심이 풍부하고 독립적인 INTJ에게는 세계적인 박물관과 미술관, 풍부한 역사가 가득한 런던이 매력적입니다.",
        "spots": ["대영박물관", "테이트 모던", "자연사박물관"],
        "tip": "무료로 개방되는 국립 박물관들의 동선을 미리 파악해 집중 탐방하세요."
    },
    "ISTP": {
        "destination": "뉴질랜드 퀸스타운",
        "category": "자연",
        "style": "액티비티",
        "tag": "#모험가 #스릴만점 #자유로운",
        "desc": "손재주가 좋고 만능 재주꾼인 ISTP는 직접 몸으로 체험하고 스릴을 느낄 수 있는 액티비티의 천국 퀸스타운을 추천합니다.",
        "spots": ["번지점프", "스카이다이빙", "밀포드 사운드 크루즈"],
        "tip": "현지 액티비티 패키지를 이용해 스릴을 연속으로 즐겨보세요."
    },
    "ISFP": {
        "destination": "인도네시아 발리",
        "category": "자연",
        "style": "휴양",
        "tag": "#감성충만 #여유로운 #예술적영감",
        "desc": "예술가적 기질과 유유자적함을 즐기는 ISFP에게는 예쁜 카페와 아름다운 석양, 여유가 가득한 발리가 딱입니다.",
        "spots": ["우붓 예술 마을", "스미냐크 비치클럽", "울루와투 사원 석양"],
        "tip": "일정을 너무 타이트하게 잡지 말고 매일의 기분에 따라 움직여보세요."
    },
    "INFP": {
        "destination": "체코 프라하",
        "category": "도시",
        "style": "휴양",
        "tag": "#낭만적인 #동화같은 #감성여행",
        "desc": "이상주의자이자 낭만파인 INFP는 마치 동화 속에 들어온 듯한 골목길과 아기자기한 야경을 자랑하는 프라하와 사랑에 빠질 것입니다.",
        "spots": ["카를교 야경", "프라하 성", "존 레논 벽"],
        "tip": "해질녘 카를교 위에서 버스킹 음악을 들으며 감성에 빠져보세요."
    },
    "INTP": {
        "destination": "아이슬란드 레이캬비크",
        "category": "자연",
        "style": "액티비티",
        "tag": "#신비로운 #신비한지형 #호기심천국",
        "desc": "독창적이고 분석적인 INTP에게는 독특한 지형과 오로라, 지열 온천 등 자연의 신비를 다각도로 연구/체험할 수 있는 아이슬란드가 제격입니다.",
        "spots": ["블루라군 온천", "골든 서클 투어", "오로라 헌팅"],
        "tip": "렌터카 투어를 통해 예측 불가능한 자연환경을 탐험해보세요."
    },
    "ESTP": {
        "destination": "태국 방콕",
        "category": "도시",
        "style": "액티비티",
        "tag": "#화려한야경 #나이트라이프 #자극과재미",
        "desc": "에너지 넘치고 자극을 좋아하는 ESTP는 화려한 야시장, 활기찬 거리, 풍부한 먹거리가 가득한 방콕에서 최상의 즐거움을 느낍니다.",
        "spots": ["카오산 로드", "왓 아룬 루프탑 바", "아이콘시암 쇼핑몰"],
        "tip": "툭툭이를 타고 카오산로드의 밤문화를 즐겨보세요."
    },
    "ESFP": {
        "destination": "미국 하와이",
        "category": "자연",
        "style": "액티비티",
        "tag": "#인싸들의성지 #열정적인 #해변휴양",
        "desc": "사교적이고 에너지 넘치는 ESFP는 파란 바다, 흥겨운 하와이안 음악, 다양한 해양 스포츠가 기다리는 하와이가 최적입니다.",
        "spots": ["와이키키 해변 서핑", "하나우마 베이 스노클링", "쿠알로아 랜치 투어"],
        "tip": "해변에서 현지인 및 여행자들과 자연스럽게 어울려보세요."
    },
    "ENFP": {
        "destination": "스페인 바르셀로나",
        "category": "도시",
        "style": "액티비티",
        "tag": "#열정만점 #가우디건축 #자유로운영혼",
        "desc": "창의적이고 열정적인 ENFP에게는 가우디의 독창적인 건축물과 열정적인 플라멩코, 독특한 문화가 숨쉬는 바르셀로나를 추천합니다.",
        "spots": ["사그라다 파밀리아 성당", "구엘 공원", "보케리아 시장"],
        "tip": "타파스 투어를 하며 매번 새로운 맛과 사람들을 경험해보세요."
    },
    "ENTP": {
        "destination": "미국 뉴욕",
        "category": "도시",
        "style": "액티비티",
        "tag": "#트렌디한 #다양성 #잠들지않는도시",
        "desc": "새로운 아이디어와 모험을 즐기는 ENTP에게는 끊임없이 변하고 다채로운 문화가 공존하는 세계의 중심, 뉴욕이 탐험 욕구를 자극합니다.",
        "spots": ["타임스퀘어", "브로드웨이 뮤지컬", "하이라인 파크"],
        "tip": "루프탑 바에서 뉴욕의 스카이라인을 보며 새로운 사람들과 대화해보세요."
    },
    "ESTJ": {
        "destination": "싱가포르",
        "category": "도시",
        "style": "휴양",
        "tag": "#쾌적한 #완벽한치안 #효율적인",
        "desc": "실용적이고 체계적인 ESTJ에게는 완벽한 치안, 깨끗한 환경, 효율적인 도시 시스템을 갖춘 싱가포르가 최고의 만족감을 줍니다.",
        "spots": ["마리나 베이 샌즈", "가든스 바이 더 베이", "센토사 섬"],
        "tip": "동선을 최적화하여 랜드마크를 효율적으로 모두 방문해보세요."
    },
    "ESFJ": {
        "destination": "베트남 다낭",
        "category": "자연",
        "style": "휴양",
        "tag": "#가성비갑 #친절한 #가족친구와함께",
        "desc": "친절하고 사람들과 나누는 것을 좋아하는 ESFJ에게는 가성비 좋은 리조트, 친절한 사람들, 호이안의 예쁜 야경이 있는 다낭이 완벽합니다.",
        "spots": ["바나힐 테마파크", "호이안 올드타운", "미케 비치"],
        "tip": "소중한 사람들과 함께 맛있는 음식을 나누며 추억을 만드세요."
    },
    "ENFJ": {
        "destination": "프랑스 파리",
        "category": "도시",
        "style": "휴양",
        "tag": "#로맨틱 #예술과낭만 #영감을주는",
        "desc": "타인에게 영감을 주고 로맨틱함을 꿈꾸는 ENFJ는 에펠탑 아래에서의 잔디밭 소풍과 미술관이 가득한 파리에서 커다란 행복을 느낍니다.",
        "spots": ["에펠탑 센강 소풍", "루브르 박물관", "몽마르트르 언덕"],
        "tip": "센강 유람선(바토무슈)을 타고 파리의 밤 야경을 감상해보세요."
    },
    "ENTJ": {
        "destination": "아랍에미리트 두바이",
        "category": "도시",
        "style": "액티비티",
        "tag": "#웅장함 #초현대적 #압도적스케일",
        "desc": "대담하고 야망이 넘치는 ENTJ는 세계 최고층 빌딩, 인공섬 등 압도적인 스케일과 비전을 보여주는 두바이에서 큰 자극을 받습니다.",
        "spots": ["부르즈 할리파 Observatory", "사막 사파리 투어", "두바이 몰"],
        "tip": "도시의 발전상과 미래지향적 건축물들을 둘러보며 영감을 얻으세요."
    }
}

# --- 사이드바: 사용자 입력 ---
st.sidebar.title("✈️ MBTI 여행지 추천")
st.sidebar.markdown("당신의 **MBTI**와 **여행 취향**을 선택해주세요!")

mbti_list = list(MBTI_DESTINATIONS.keys())
selected_mbti = st.sidebar.selectbox("MBTI를 선택하세요", mbti_list, index=0)

st.sidebar.divider()
st.sidebar.subheader("🎯 추가 취향 필터")
pref_category = st.sidebar.radio("선호하는 풍경", ["상관없음", "자연", "도시"])
pref_style = st.sidebar.radio("선호하는 스타일", ["상관없음", "휴양", "액티비티"])

# --- 메인 화면 ---
st.title("🗺️ 나만의 MBTI 맞춤 여행지")
st.caption("성격 유형에 꼭 맞는 완벽한 여행지를 찾아드립니다.")
st.divider()

data = MBTI_DESTINATIONS[selected_mbti]

# 매칭 여부 판별
category_match = (pref_category == "상관없음") or (pref_category == data["category"])
style_match = (pref_style == "상관없음") or (pref_style == data["style"])
is_perfect_match = category_match and style_match

# 상단 상태 알림 (결과를 가리지 않고 친절히 안내만 제공)
if is_perfect_match:
    st.success(f"🎯 **[{selected_mbti}]** 추천지인 **{data['destination']}**는 선택하신 취향(**{data['category']} / {data['style']}**)과 완벽히 일치합니다!")
else:
    mismatched = []
    if not category_match:
        mismatched.append(f"풍경: {pref_category} ≠ {data['category']}")
    if not style_match:
        mismatched.append(f"스타일: {pref_style} ≠ {data['style']}")
    
    st.info(f"💡 **[{selected_mbti}]** 대표 추천지는 **[{data['category']} / {data['style']}]** 성향의 **{data['destination']}**입니다.\n\n"
            f"(선택하신 필터: {', '.join(mismatched)})")

# 추천지 메인 영역 (항상 노출)
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader(f"[{selected_mbti}] 대표 추천")
    st.header(f"📍 {data['destination']}")
    
    # 속성 칩 표시
    st.markdown(f"**속성:** `{data['category']}` | `{data['style']}`")
    st.write(f"**태그:** `{data['tag']}`")
    st.info(data["desc"])

with col2:
    st.subheader("💡 추천 주요 일정 & 팁")
    st.markdown("**추천 명소 및 활동:**")
    for spot in data["spots"]:
        st.markdown(f"- {spot}")
    
    st.warning(f"**여행 팁:** {data['tip']}")

st.divider()
st.caption("TIP: 사이드바에서 다른 MBTI나 필터를 선택해 자유롭게 비교해 보세요!")
