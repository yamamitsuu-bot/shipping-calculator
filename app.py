import streamlit as st

# --- 1. 箱のサイズデータ ---
BOX_DATA = [
    {"name": "60サイズ", "dims": [18.5, 18.5, 22.0], "size_key": "60"},
    {"name": "80サイズ", "dims": [24.0, 24.0, 32.0], "size_key": "80"},
    {"name": "100サイズ", "dims": [30.0, 30.0, 40.0], "size_key": "100"},
    {"name": "120サイズ", "dims": [30.0, 30.0, 60.0], "size_key": "120"},
    {"name": "140サイズ", "dims": [37.5, 37.5, 65.0], "size_key": "140"},
    {"name": "160サイズ", "dims": [55.0, 40.0, 60.0], "size_key": "160"},
]
BOX_SIZES_STR = ["60", "80", "100", "120", "140", "160"]

# --- 2. 3社の配送料金データ ---
RATES = {
    # ゆうパック (IMG_0213)
    "yu_pack": {
        "福岡県内": [770, 980, 1210, 1540, 1810, 2090],
        "九州":     [980, 980, 1430, 1760, 2090, 2420],
        "中国":     [980, 980, 1430, 1760, 2090, 2420],
        "四国":     [980, 980, 1430, 1760, 2090, 2420],
        "関西":     [990, 990, 1540, 1870, 2200, 2530],
        "北陸":     [1210, 1210, 1760, 2090, 2420, 2750],
        "東海":     [1210, 1210, 1760, 2090, 2420, 2750],
        "関東":     [1210, 1210, 1760, 2090, 2420, 2750],
        "信越":     [1210, 1210, 1760, 2090, 2420, 2750],
        "東北":     [1320, 1320, 1870, 2200, 2530, 2860],
        "北海道":   [1540, 1540, 2090, 2420, 2750, 3080],
        "沖縄":     [990, 1210, 1540, 1870, 2200, 2530],
    },
    # ヤマト (IMG_0212)
    "yamato": {
        "福岡県内": [880, 1150, 1430, 1650, 2090, 2530],
        "九州":     [880, 1150, 1430, 1650, 2090, 2530],
        "中国":     [1040, 1320, 1650, 2090, 2530, 2970],
        "四国":     [1040, 1320, 1650, 2090, 2530, 2970],
        "関西":     [1040, 1320, 1650, 2090, 2530, 2970],
        "北陸":     [1430, 1760, 2090, 2530, 2970, 3410],
        "東海":     [1430, 1760, 2090, 2530, 2970, 3410],
        "関東":     [1430, 1760, 2090, 2530, 2970, 3410],
        "信越":     [1430, 1760, 2090, 2530, 2970, 3410],
        "東北":     [1760, 2090, 2420, 2860, 3300, 3740],
        "北海道":   [2530, 2860, 3190, 3630, 4070, 4510],
        "沖縄":     [1320, 1980, 2530, 3300, 4070, 4730],
    },
    # 佐川 (IMG_0211)
    "sagawa": {
        "福岡県内": [570, 750, 970, 1380, 1380, 1590],
        "九州":     [570, 750, 970, 1380, 1380, 1590],
        "中国":     [620, 780, 1010, 1500, 1500, 1710],
        "四国":     [670, 970, 1160, 1600, 1600, 1820],
        "関西":     [670, 970, 1160, 1600, 1600, 1820],
        "北陸":     [820, 1130, 1330, 1820, 1820, 2040],
        "東海":     [720, 1020, 1220, 1710, 1710, 1930],
        "関東":     [930, 1230, 1440, 1930, 1930, 2150],
        "信越":     [930, 1230, 1440, 1930, 1930, 2150],
        "東北":     [1030, 1330, 1550, 2040, 2040, 2260],
        "北海道":   [1130, 1440, 1650, 2150, 2150, 2370],
        "沖縄":     [3000, 3500, 4100, 6000, 6000, 6500],
    }
}

# --- 3. 計算ロジック ---

def find_optimal_box(item_l, item_w, item_h):
    if item_l <= 0 or item_w <= 0 or item_h <= 0:
        return ("エラー: 3辺すべてに0より大きい数値を入力してください。", None)
    item_dims_sorted = sorted([item_l, item_w, item_h])
    for box in BOX_DATA:
        box_dims_sorted = sorted(box["dims"])
        if (item_dims_sorted[0] <= box_dims_sorted[0] and
            item_dims_sorted[1] <= box_dims_sorted[1] and
            item_dims_sorted[2] <= box_dims_sorted[2]):
            return (box["name"], box["size_key"])
    return ("160サイズを超えるため、どの箱にも収まりません。", None)

def find_cheapest_rate(size_key, destination):
    if size_key is None:
        return (None, None)
    try:
        size_index = BOX_SIZES_STR.index(size_key)
    except ValueError:
        return ("内部エラー: サイズキーが見つかりません。", None)

    rate_yu_pack = RATES["yu_pack"][destination][size_index]
    rate_yamato = RATES["yamato"][destination][size_index]
    rate_sagawa = RATES["sagawa"][destination][size_index]

    results = [
        ("ゆうパック", rate_yu_pack),
        ("ヤマト運輸", rate_yamato),
        ("佐川急便", rate_sagawa)
    ]
    sorted_results = sorted(results, key=lambda x: x[1])
    return (sorted_results[0], sorted_results)

# --- 4. StreamlitのUI（画面）部分 ---

st.title('📦 最適箱サイズ ＋ 🚚 最安送料計算ツール')
st.write('荷物の3辺の長さ（cm）と、配送先の地域を選択してください。')
st.write('（参照データ：画像メモの箱寸法と運賃表）')

st.header('1. 荷物のサイズ(cm)を入力')
col1, col2, col3 = st.columns(3)
with col1:
    l = st.number_input('長さ 1 (cm)', min_value=0.1, value=10.0, step=0.1)
with col2:
    w = st.number_input('長さ 2 (cm)', min_value=0.1, value=10.0, step=0.1)
with col3:
    h = st.number_input('長さ 3 (cm)', min_value=0.1, value=10.0, step=0.1)

st.header('2. 配送先を選択')
destination = st.selectbox(
    '配送先を選んでください',
    options=["福岡県内", "九州", "中国", "四国", "関西", "北陸", "東海", "関東", "信越", "東北", "北海道", "沖縄"],
    index=7 # デフォルトを「関東」にしておく
)

st.write('---')

# 計算ボタン
if st.button('計算スタート', type="primary"):
    # 手順 1: 最適な箱のサイズを計算
    (box_name, size_key) = find_optimal_box(l, w, h)
    
    st.subheader('診断結果')
    st.markdown(f"📦 推奨される箱のサイズ: **{box_name}**")
    
    # 手順 2: 最安の送料を計算
    (cheapest, all_rates) = find_cheapest_rate(size_key, destination)
    
    if cheapest:
        st.markdown(f"🚚 {destination} への最安送料 ({box_name}):")
        st.success(f"🥇 **{cheapest[0]}: {cheapest[1]} 円**")
        
        st.subheader("--- 3社 料金比較 ---")
        
        # 比較表をきれいに表示
        col_company, col_rate = st.columns(2)
        with col_company:
            for company, rate in all_rates:
                st.write(f"{company}")
        with col_rate:
            for company, rate in all_rates:
                st.write(f"**{rate} 円**")
    else:
        st.error("送料を計算できませんでした。（箱のサイズが大きすぎるか、入力値が不正です）")