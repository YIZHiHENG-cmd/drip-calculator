import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="ETF 投資介紹工具", layout="wide")
st.title("0050 vs 009816：ETF標的績效比一比🤡")

# 側邊欄：讓使用者選擇想看哪檔 ETF
st.sidebar.header("請選擇 ETF")
etf_option = st.sidebar.selectbox(
    "想要查看哪一檔 ETF？",
    ("0050 (元大台灣50)", "009816 (凱基台灣TOP50)")
)

# 根據選擇設定股票代號
if "0050" in etf_option:
    ticker = "0050.TW"
    name = "元大台灣50"
    intro = "如果你想參與台灣經濟的長線成長，又不想花時間天天盯盤研究個股，0050 就是最省心的起手式。它老老實實地打包了台灣市值最大、最賺錢的前 50 家護國神山（像是台積電、鴻海、聯發科等）。因為上市超過二十年，經歷過無數次市場大風大浪，規模和穩定度都是元老級的。加上每半年定期把成分股賺的利息配發到你的帳戶裡，非常適合喜歡手邊有現金流、追求安穩踏實的長期投資人。不過，因為它是傳統的配息型，拿到股息如果沒有自己手動再買回，長期的複利效果就會被打折扣，且領配息時也可能面臨被課稅與扣匯費的損耗。"
elif "009816" in etf_option:
    ticker = "009816.TW"
    name = "凱基台灣TOP50"
    intro = "009816 同樣是鎖定台灣前 50 大企業巨頭，但它在機制上做了更具攻擊性的升級。這檔 ETF 最大的特色是「不配息」，成分股發出來的股利，會直接在基金內部自動幫你買進更多特價股票，徹底免去被課股利所得稅、二代健保和手續費的損耗，讓複利像雪球一樣滾到最滿。同時，它還加入了「動能加碼」的選股策略，會自動把資金往近期市場上氣勢最旺、最飆的強勢股集中，非常適合還在資產累積期、追求長線報酬率最大化的小資族與年輕人。但要注意的是，這種動能策略在市場震盪盤整、類股輪動太快時，容易出現追高殺低的損耗；且因為剛上市不久，缺乏長期的真實市場檢驗，加上資產高度集中在科技業，遇到景氣下行時的波動和修正壓力也會比較大。"

# 顯示 ETF 簡介
st.subheader(f"🔍 {etf_option} 簡介")
st.write(intro)

st.markdown("---")

# 抓取即時數據與圖表
st.subheader("📈 歷史走勢與股價變化")
with st.spinner("正在從雲端抓取最新股市數據..."):
    # 透過 yfinance 抓取過去一年的歷史價格
    data = yf.Ticker(ticker)
    df = data.history(period="1y")
    
    if not df.empty:
        # 計算最新收盤價
        latest_price = df['Close'].iloc[-1]
        st.metric(label=f"{name} 最新收盤價", value=f"{latest_price:.2f} TWD")
        
        # 一行程式碼直接畫出精美折線圖！
        st.line_chart(df['Close'])
    else:
        st.error("暫時無法抓取該股票數據，請檢查代號是否正確。")

#--------------------------------------------------------
st.markdown("---")
st.subheader("🧮 DRIP 股息再投資複利計算機(一次性投入的情況下)")
st.write("輸入你的預期投資規劃，即可親眼見證「執行股息再投資(DRIP)」與「將股息花掉」在多年後的淨獲利差距。")

# 讓使用者輸入參數的滑桿與輸入框
col1, col2 = st.columns(2)
with col1:
    init_investment = st.number_input("初始投資金額 (TWD)", min_value=10000, value=100000, step=10000)
    years = st.slider("投資年數", min_value=1, max_value=30, value=10)
with col2:
    annual_return = st.slider("預估年化報酬率 (%)（含股息）", min_value=1.0, max_value=15.0, value=8.0, step=0.5)
    
    # 智慧型判斷：若選擇 009816 則強制配息率為 0%
    if "009816" in etf_option:
        dividend_yield = 0.0
        st.info("💡 009816 為不配息（收益滾入再投資）型 ETF，系統已自動將配息率設為 0%。它在內部已自動執行 DRIP 囉！")
    else:
        dividend_yield = st.slider("預估年配息率 (%)", min_value=0.0, max_value=10.0, value=5.0, step=0.5)

# 核心數學計算
# 1. 有執行 DRIP (總市值以年化報酬率全力複利滾動)
total_drip = init_investment * ((1 + annual_return / 100) ** years)

# 2. 沒有執行 DRIP (本金只享受股價漲幅)
# 股價年漲幅 = 年化總報酬率 - 配息率
price_growth_rate = (annual_return - dividend_yield) / 100
total_no_drip = init_investment * ((1 + price_growth_rate) ** years)

# 3. 計算純利潤 (淨獲利 = 總市值 - 初始本金)
profit_drip = total_drip - init_investment
profit_no_drip = total_no_drip - init_investment

# 4. 計算投資報酬率 (ROI)
roi_drip = (profit_drip / init_investment) * 100
roi_no_drip = (profit_no_drip / init_investment) * 100

# 顯示計算結果
st.markdown("### 📊 淨獲利（純賺到的錢）對比")
c1, c2 = st.columns(2)

c1.metric(
    label="🔄 執行 DRIP（純淨獲利）", 
    value=f"${profit_drip:,.0f} TWD",
    delta=f"總報酬率 +{roi_drip:.1f}%"
)

c2.metric(
    label="☕ 沒執行 DRIP（純淨獲利，股息拿去花）", 
    value=f"${profit_no_drip:,.0f} TWD",
    delta=f"總報酬率 +{roi_no_drip:.1f}%"
)

# 痛點分析結論
net_difference = profit_drip - profit_no_drip

if net_difference > 0:
    st.success(
    f"💡 **你多賺的錢**：扣除投入的 **{init_investment:,.0f} TWD** 本金後，"
        f"執行 DRIP 能幫你淨賺 **{profit_drip:,.0f} TWD**！"
        f"比起把股息花掉的作法（只淨賺 {profit_no_drip:,.0f} TWD），"
        f"你**純粹靠複利多賺了 {net_difference:,.0f} TWD**！"
    )
else:
    st.info("💡 調整上方滑桿，看看不同的報酬率與時間，會如何拉開資產的差距🥵")
